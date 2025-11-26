# backend/utils/forecasting.py
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from backend.models.bill import Bill
from backend.models.fund import Fund
from backend.models.income import Income
from backend.database import db


def generate_forecast(household_id, start_date=None, months_to_project=3, buffer=100):
    """
    Generate a comprehensive financial forecast for the household.

    Args:
        household_id (int): Household ID to generate forecast for
        start_date (date): Starting date for forecast (default: today)
        months_to_project (int): Number of months to project forward (default: 3)
        buffer (float): Minimum cash buffer to maintain (default: 100)

    Returns:
        dict: Contains projection array and summary statistics
    """
    if start_date is None:
        start_date = date.today()

    end_date = start_date + relativedelta(months=months_to_project)

    # Get all active bills for the household
    bills = Bill.query.filter_by(household_id=household_id, is_active=True).all()

    # Get all funds with recurring deposits
    funds = Fund.query.filter(
        Fund.household_id == household_id,
        Fund.recurring_amount.isnot(None),
        Fund.recurring_amount > 0,
    ).all()

    # Get household's income sources (Income model doesn't have is_active field)
    incomes = Income.query.filter_by(household_id=household_id).all()

    # Calculate starting balance (sum of all cash funds)
    cash_funds = Fund.query.filter_by(household_id=household_id, fund_type="Cash").all()
    starting_balance = sum(fund.balance for fund in cash_funds)

    # Generate projection events
    projection_events = []
    current_balance = starting_balance

    # Generate all events within the projection period
    all_events = []

    # Add bill events
    for bill in bills:
        bill_events = _generate_bill_events(bill, start_date, end_date)
        all_events.extend(bill_events)

    # Add fund deposit events
    for fund in funds:
        if not fund.skip_next and fund.next_deposit_date:
            fund_events = _generate_fund_events(fund, start_date, end_date)
            all_events.extend(fund_events)

    # Add income events
    for income in incomes:
        income_events = _generate_income_events(income, start_date, end_date)
        all_events.extend(income_events)

    # Sort all events by date
    all_events.sort(key=lambda x: x["date"])

    # Calculate running balance and create projection
    min_balance = current_balance
    min_balance_date = start_date

    for event in all_events:
        current_balance += event["amount"]

        if current_balance < min_balance:
            min_balance = current_balance
            min_balance_date = event["date"]

        projection_events.append(
            {
                "date": event["date"].isoformat(),
                "event": event["description"],
                "type": event["type"],
                "amount": event["amount"],
                "expected_balance": round(current_balance, 2),
            }
        )

    # Calculate summary statistics
    expected_minimum = min_balance
    actual_minimum = min_balance - buffer
    extra_payment_needed = max(0, buffer - min_balance) if min_balance < buffer else 0

    # Calculate buffer status
    if min_balance >= buffer * 1.5:
        buffer_status = "OK"
    elif min_balance >= buffer:
        buffer_status = "Warning"
    else:
        buffer_status = "Danger"

    # Get upcoming bills (next 7 days)
    upcoming_bills = _get_upcoming_bills(household_id, start_date, days=7)

    # Calculate expected balance at next pay cycle
    next_pay_date = _get_next_pay_date(incomes, start_date)
    expected_balance_next_pay = _calculate_balance_at_date(
        projection_events, next_pay_date, starting_balance
    )

    return {
        "projection": projection_events,
        "summary": {
            "starting_balance": round(starting_balance, 2),
            "expected_minimum": round(expected_minimum, 2),
            "actual_minimum": round(actual_minimum, 2),
            "extra_payment_needed": round(extra_payment_needed, 2),
            "buffer_status": buffer_status,
            "min_balance_date": min_balance_date.isoformat(),
            "upcoming_bills": upcoming_bills,
            "next_pay_date": next_pay_date.isoformat() if next_pay_date else None,
            "expected_balance_next_pay": (
                round(expected_balance_next_pay, 2)
                if expected_balance_next_pay
                else None
            ),
        },
    }


def _generate_bill_events(bill, start_date, end_date):
    """Generate bill payment events within the date range"""
    events = []
    current_date = bill.calculate_next_due_date(start_date)

    while current_date <= end_date:
        events.append(
            {
                "date": current_date,
                "description": f"{bill.name} (Bill)",
                "type": "bill_payment",
                "amount": -float(bill.amount),
                "bill_id": bill.id,
            }
        )

        # Calculate next occurrence
        if bill.frequency == "weekly":
            current_date += timedelta(days=7)
        elif bill.frequency == "biweekly":
            current_date += timedelta(days=14)
        elif bill.frequency == "monthly":
            current_date += relativedelta(months=1)
        elif bill.frequency == "quarterly":
            current_date += relativedelta(months=3)
        elif bill.frequency == "yearly":
            current_date += relativedelta(years=1)
        else:
            # Default to monthly
            current_date += relativedelta(months=1)

    return events


def _generate_fund_events(fund, start_date, end_date):
    """Generate fund deposit events within the date range"""
    events = []
    current_date = fund.next_deposit_date

    if current_date < start_date:
        # Calculate next deposit after start_date
        while current_date < start_date:
            current_date += timedelta(days=14)  # Assuming biweekly deposits

    while current_date <= end_date:
        events.append(
            {
                "date": current_date,
                "description": f"{fund.name} Deposit",
                "type": "fund_deposit",
                "amount": -float(
                    fund.recurring_amount
                ),  # Negative because it's leaving cash
                "fund_id": fund.id,
            }
        )

        # Assume biweekly deposits for funds
        current_date += timedelta(days=14)

    return events


def _generate_income_events(income, start_date, end_date):
    """Generate income events within the date range"""
    events = []

    # For now, assume biweekly income based on the existing income model
    # This would need to be enhanced based on your Income model structure
    current_date = start_date

    # Find next occurrence (assuming biweekly on specific day)
    while current_date.weekday() != 4:  # Friday = 4
        current_date += timedelta(days=1)

    while current_date <= end_date:
        events.append(
            {
                "date": current_date,
                "description": f"{income.source} (Income)",
                "type": "income",
                "amount": float(income.amount),
                "income_id": income.id,
            }
        )

        # Next biweekly occurrence
        current_date += timedelta(days=14)

    return events


def _get_upcoming_bills(household_id, start_date, days=7):
    """Get bills due in the next N days"""
    end_date = start_date + timedelta(days=days)
    bills = Bill.query.filter_by(household_id=household_id, is_active=True).all()

    upcoming = []
    for bill in bills:
        next_due = bill.calculate_next_due_date(start_date)
        if start_date <= next_due <= end_date:
            upcoming.append(
                {
                    "id": bill.id,
                    "name": bill.name,
                    "amount": float(bill.amount),
                    "due_date": next_due.isoformat(),
                    "category": bill.category,
                    "is_autopay": bill.is_autopay,
                }
            )

    return sorted(upcoming, key=lambda x: x["due_date"])


def _get_next_pay_date(incomes, start_date):
    """Calculate the next pay date based on income sources"""
    if not incomes:
        return None

    # Simple logic: assume biweekly pay on Fridays
    current_date = start_date
    while current_date.weekday() != 4:  # Friday = 4
        current_date += timedelta(days=1)

    return current_date


def _calculate_balance_at_date(projection_events, target_date, starting_balance):
    """Calculate expected balance at a specific date"""
    if not target_date:
        return None

    balance = starting_balance
    for event in projection_events:
        event_date = datetime.fromisoformat(event["date"]).date()
        if event_date <= target_date:
            balance += event["amount"]
        else:
            break

    return balance


def get_bill_schedule_summary(household_id, start_date=None, days=30):
    """
    Get a simple bill schedule for the next N days.
    Used by the bill scheduling route.
    """
    if start_date is None:
        start_date = date.today()

    end_date = start_date + timedelta(days=days)
    bills = Bill.query.filter_by(household_id=household_id, is_active=True).all()

    schedule = []
    for bill in bills:
        next_due = bill.calculate_next_due_date(start_date)
        if start_date <= next_due <= end_date:
            schedule.append(
                {
                    "date": next_due.isoformat(),
                    "bill_id": bill.id,
                    "name": bill.name,
                    "amount": float(bill.amount),
                    "category": bill.category,
                    "is_autopay": bill.is_autopay,
                }
            )

    return sorted(schedule, key=lambda x: x["date"])
