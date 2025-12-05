from flask import Blueprint, request, jsonify

funds_bp = Blueprint("funds", __name__)
from database import db
from models import Fund, Transaction
from models.account import Account
from shared.utils.household_helpers import get_current_household_id
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from decimal import Decimal


@funds_bp.route("/", methods=["GET"])
@jwt_required()
def list_funds():
    """Get all funds for the current household"""
    household_id = get_current_household_id()

    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    funds = Fund.query.filter_by(household_id=household_id)
    funds = funds.order_by(Fund.created_at.desc()).all()
    return jsonify([fund.to_dict() for fund in funds]), 200


@funds_bp.route("/", methods=["POST"])
@jwt_required()
def create_fund():
    """Create a new fund for the current household"""
    household_id = get_current_household_id()

    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    balance = data.get("balance", 0.0)
    goal = data.get("goal", 0.0)
    is_cash = data.get("is_cash", False)
    account_id = data.get("account_id")
    description = data.get("description")
    fund_type = data.get("fund_type")
    recurring_amount = data.get("recurring_amount")
    next_deposit_date = data.get("next_deposit_date")
    skip_next = data.get("skip_next", False)

    # Validate required fields
    if not name:
        return jsonify({"error": "Fund name is required"}), 400

    # If is_cash is True, set fund_type to Cash and clear account_id
    if is_cash:
        fund_type = "Cash"
        account_id = None
    elif not fund_type:
        # If not cash and no fund_type specified, default to Expenses
        fund_type = "Expenses"

    # Validate account_id for non-cash funds (must belong to same household)
    account = None
    if not is_cash and account_id:
        account = Account.query.filter_by(
            id=account_id, household_id=household_id
        ).first()
        if not account:
            return jsonify({"error": "Account not found or access denied"}), 404

    # Validate fund_type
    if fund_type not in ["Expenses", "Savings", "Cash"]:
        return jsonify({"error": "Fund type must be Expenses, Savings, or Cash"}), 400

    # Validate balance and goal
    try:
        balance = float(balance)
        if balance < 0:
            return jsonify({"error": "Balance cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid balance amount"}), 400

    try:
        goal = float(goal)
        if goal < 0:
            return jsonify({"error": "Goal cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid goal amount"}), 400

    # Validate recurring_amount if provided
    if recurring_amount is not None:
        try:
            recurring_amount = float(recurring_amount)
            if recurring_amount < 0:
                return jsonify({"error": "Recurring amount cannot be negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid recurring amount"}), 400

    # Parse next_deposit_date if provided
    from datetime import datetime

    if next_deposit_date:
        try:
            next_deposit_date = datetime.strptime(next_deposit_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Check if fund name already exists for this household
    existing_fund = Fund.query.filter_by(household_id=household_id, name=name).first()
    if existing_fund:
        return jsonify({"error": "Fund with this name already exists"}), 400

    # Create new fund
    fund = Fund(
        name=name,
        balance=balance,
        goal=goal,
        is_cash=is_cash,
        account_id=account_id,
        description=description,
        fund_type=fund_type,
        recurring_amount=recurring_amount,
        next_deposit_date=next_deposit_date,
        skip_next=skip_next,
        household_id=household_id,
    )

    try:
        db.session.add(fund)
        db.session.commit()

        # Fetch and return the newly created fund with all fields
        funds = Fund.query.filter_by(household_id=household_id)
        funds = funds.order_by(Fund.created_at.desc()).all()
        return jsonify([fund.to_dict() for fund in funds]), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create fund: {str(e)}"}), 500


@funds_bp.route("/<int:fund_id>", methods=["PATCH"])
@jwt_required()
def update_fund(fund_id):
    """Edit name, goal, or balance of a fund"""
    household_id = get_current_household_id()

    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Get fund and verify household access
    fund = Fund.query.filter_by(id=fund_id, household_id=household_id).first()
    if not fund:
        return jsonify({"error": "Fund not found or access denied"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    balance = data.get("balance", None)
    goal = data.get("goal", None)
    is_cash = data.get("is_cash", None)
    account_id = data.get("account_id", None)
    description = data.get("description", None)
    fund_type = data.get("fund_type", None)
    recurring_amount = data.get("recurring_amount", None)
    next_deposit_date = data.get("next_deposit_date", None)
    skip_next = data.get("skip_next", None)

    # Validate and update fields
    if name is not None:
        fund.name = name

    if balance is not None:
        try:
            balance = float(balance)
            if balance < 0:
                return jsonify({"error": "Balance cannot be negative"}), 400
            fund.balance = balance
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid balance amount"}), 400

    if goal is not None:
        try:
            goal = float(goal)
            if goal < 0:
                return jsonify({"error": "Goal cannot be negative"}), 400
            fund.goal = goal
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid goal amount"}), 400

    if is_cash is not None:
        fund.is_cash = is_cash
        if is_cash:
            fund_type = "Cash"
            account_id = None
        elif fund.fund_type not in ["Expenses", "Savings"]:
            fund_type = "Expenses"

    if account_id is not None:
        # Validate account_id for non-cash funds (must belong to same household)
        account = Account.query.filter_by(
            id=account_id, household_id=household_id
        ).first()
        if not account:
            return jsonify({"error": "Account not found or access denied"}), 404

    if fund_type is not None:
        # Validate fund_type
        if fund_type not in ["Expenses", "Savings", "Cash"]:
            return (
                jsonify({"error": "Fund type must be Expenses, Savings, or Cash"}),
                400,
            )
        fund.fund_type = fund_type

    if recurring_amount is not None:
        try:
            recurring_amount = float(recurring_amount)
            if recurring_amount < 0:
                return jsonify({"error": "Recurring amount cannot be negative"}), 400
            fund.recurring_amount = recurring_amount
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid recurring amount"}), 400

    if next_deposit_date is not None:
        # Parse next_deposit_date
        try:
            next_deposit_date = datetime.strptime(next_deposit_date, "%Y-%m-%d").date()
            fund.next_deposit_date = next_deposit_date
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if skip_next is not None:
        fund.skip_next = skip_next

    try:
        db.session.commit()
        return (
            jsonify({"message": "Fund updated successfully", "fund": fund.to_dict()}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update fund: {str(e)}"}), 500


@funds_bp.route("/<int:fund_id>/withdraw", methods=["POST"])
@jwt_required()
def withdraw_from_fund(fund_id):
    """Withdraw money from a fund (creates transaction with recurring support)"""
    current_user_id = get_jwt_identity()

    # Get fund and verify ownership
    fund = Fund.query.filter_by(id=fund_id, user_id=current_user_id).first()
    if not fund:
        return jsonify({"error": "Fund not found or access denied"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    amount = data.get("amount")
    description = data.get("description", f"Withdrawal from {fund.name}")
    date_str = data.get("date", date.today().isoformat())
    is_recurring = data.get("is_recurring", False)
    frequency = data.get("frequency")

    if amount is None:
        return jsonify({"error": "Amount is required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
        transaction_date = datetime.fromisoformat(
            date_str.replace("Z", "+00:00")
        ).date()
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400

    if fund.balance < amount:
        return (
            jsonify(
                {
                    "error": "Insufficient funds",
                    "current_balance": fund.balance,
                    "requested_amount": amount,
                }
            ),
            400,
        )

    try:
        # Create transaction
        transaction = Transaction(
            user_id=current_user_id,
            fund_id=fund.id,
            amount=amount,
            description=description,
            category="Withdrawal",
            transaction_type="expense",
            date=transaction_date,
            is_recurring=is_recurring,
            frequency=frequency if is_recurring else None,
        )

        # Calculate next occurrence if recurring
        if is_recurring and frequency:
            transaction.next_occurrence = transaction.calculate_next_occurrence(
                transaction_date
            )

        # Update fund balance
        fund.balance -= amount
        if hasattr(fund, "account") and fund.account:
            fund.account.balance -= Decimal(str(amount))

        db.session.add(transaction)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Successfully withdrew ${amount} from {fund.name}",
                    "fund": fund.to_dict(),
                    "transaction": transaction.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to withdraw funds: {str(e)}"}), 500


@funds_bp.route("/<int:fund_id>/toggle-skip", methods=["PATCH"])
@jwt_required()
def toggle_skip_next(fund_id):
    """Toggle the skip_next flag for a fund"""
    current_user_id = get_jwt_identity()

    # Get fund and verify ownership
    fund = Fund.query.filter_by(id=fund_id, user_id=current_user_id).first()
    if not fund:
        return jsonify({"error": "Fund not found or access denied"}), 404

    try:
        fund.skip_next = not fund.skip_next
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Skip next deposit {'enabled' if fund.skip_next else 'disabled'} for {fund.name}",
                    "fund": fund.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to toggle skip next: {str(e)}"}), 500


@funds_bp.route("/process-recurring", methods=["POST"])
@jwt_required()
def process_recurring_deposits():
    """Process all recurring deposits for funds that are due"""
    current_user_id = get_jwt_identity()

    # Get all funds that are due for recurring deposits
    funds = Fund.query.filter_by(user_id=current_user_id).all()
    processed_funds = []

    try:
        for fund in funds:
            if fund.is_due_for_deposit():
                if fund.process_recurring_deposit():
                    processed_funds.append(fund)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Processed {len(processed_funds)} recurring deposits",
                    "processed_funds": [fund.to_dict() for fund in processed_funds],
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"error": f"Failed to process recurring deposits: {str(e)}"}),
            500,
        )
