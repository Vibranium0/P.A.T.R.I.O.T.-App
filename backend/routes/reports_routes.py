from flask import Blueprint, jsonify, request
from backend.models import Fund, Transaction, Bill, Income, Debt
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.forecasting import generate_forecast, get_bill_schedule_summary
from datetime import datetime, date, timedelta
from backend.utils.auth_helpers import get_current_household_id

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary_report():
    """Enhanced summary report with forecasting data"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Get user's funds and transactions
    funds = Fund.query.filter_by(household_id=household_id).all()
    total_balance = sum(f.balance for f in funds)
    total_transactions = Transaction.query.filter_by(household_id=household_id).count()

    # Get basic forecast data for next 30 days
    try:
        forecast_data = generate_forecast(
            household_id=household_id, months_to_project=1
        )

        return (
            jsonify(
                {
                    "total_balance": total_balance,
                    "total_transactions": total_transactions,
                    "funds": [
                        {
                            "id": f.id,
                            "name": f.name,
                            "balance": f.balance,
                            "fund_type": f.fund_type,
                        }
                        for f in funds
                    ],
                    "forecast_summary": {
                        "upcoming_bills": forecast_data["summary"]["upcoming_bills"],
                        "expected_balance": forecast_data["summary"].get(
                            "expected_balance_next_pay"
                        ),
                        "extra_payment_needed": forecast_data["summary"][
                            "extra_payment_needed"
                        ],
                        "buffer_status": forecast_data["summary"]["buffer_status"],
                        "next_pay_date": forecast_data["summary"].get("next_pay_date"),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        # Fall back to basic summary if forecasting fails
        return (
            jsonify(
                {
                    "total_balance": total_balance,
                    "total_transactions": total_transactions,
                    "funds": [
                        {
                            "id": f.id,
                            "name": f.name,
                            "balance": f.balance,
                            "fund_type": f.fund_type,
                        }
                        for f in funds
                    ],
                    "forecast_summary": {
                        "upcoming_bills": [],
                        "expected_balance": None,
                        "extra_payment_needed": 0,
                        "buffer_status": "Unknown",
                        "next_pay_date": None,
                    },
                }
            ),
            200,
        )


@reports_bp.route("/forecast", methods=["GET"])
@jwt_required()
def forecast_report():
    """Comprehensive forecast report with customizable parameters"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Parse query parameters
    start_date_str = request.args.get("start_date")
    months_to_project = int(request.args.get("months_to_project", 3))
    buffer = float(request.args.get("buffer", 100))

    try:
        # Parse start date or use today
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        else:
            start_date = date.today()

        # Generate comprehensive forecast
        forecast_data = generate_forecast(
            household_id=household_id,
            start_date=start_date,
            months_to_project=months_to_project,
            buffer=buffer,
        )

        return jsonify(forecast_data), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to generate forecast: {str(e)}"}), 500


@reports_bp.route("/upcoming-bills", methods=["GET"])
@jwt_required()
def upcoming_bills_report():
    """Get upcoming bills with optional date range"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    days = int(request.args.get("days", 30))

    try:
        upcoming_bills = get_bill_schedule_summary(household_id, date.today(), days)

        return (
            jsonify(
                {
                    "upcoming_bills": upcoming_bills,
                    "total_amount": sum(bill["amount"] for bill in upcoming_bills),
                    "autopay_amount": sum(
                        bill["amount"] for bill in upcoming_bills if bill["is_autopay"]
                    ),
                    "manual_amount": sum(
                        bill["amount"]
                        for bill in upcoming_bills
                        if not bill["is_autopay"]
                    ),
                    "period_days": days,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Failed to get upcoming bills: {str(e)}"}), 500


@reports_bp.route("/financial-health", methods=["GET"])
@jwt_required()
def financial_health_report():
    """Comprehensive financial health analysis"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    try:
        # Get user's financial data
        funds = Fund.query.filter_by(household_id=household_id).all()

        # Calculate totals by fund type
        cash_funds = sum(f.balance for f in funds if f.fund_type == "Cash")
        savings_funds = sum(f.balance for f in funds if f.fund_type == "Savings")
        expense_funds = sum(f.balance for f in funds if f.fund_type == "Expenses")

        # Get forecast for buffer analysis
        forecast = generate_forecast(household_id=household_id, months_to_project=6)

        # Calculate financial health metrics
        total_balance = cash_funds + savings_funds + expense_funds
        emergency_fund_ratio = cash_funds / max(
            total_balance, 1
        )  # Avoid division by zero

        # Determine health status
        if forecast["summary"]["buffer_status"] == "OK" and emergency_fund_ratio >= 0.3:
            health_status = "Excellent"
        elif (
            forecast["summary"]["buffer_status"] == "Warning"
            or emergency_fund_ratio >= 0.15
        ):
            health_status = "Good"
        elif (
            forecast["summary"]["buffer_status"] == "Danger"
            or emergency_fund_ratio >= 0.05
        ):
            health_status = "Fair"
        else:
            health_status = "Poor"

        return (
            jsonify(
                {
                    "health_status": health_status,
                    "total_balance": round(total_balance, 2),
                    "cash_funds": round(cash_funds, 2),
                    "savings_funds": round(savings_funds, 2),
                    "expense_funds": round(expense_funds, 2),
                    "emergency_fund_ratio": round(emergency_fund_ratio * 100, 1),
                    "buffer_status": forecast["summary"]["buffer_status"],
                    "projected_minimum": forecast["summary"]["expected_minimum"],
                    "extra_payment_needed": forecast["summary"]["extra_payment_needed"],
                    "recommendations": _generate_recommendations(
                        health_status, emergency_fund_ratio, forecast["summary"]
                    ),
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify({"error": f"Failed to generate financial health report: {str(e)}"}),
            500,
        )


def _generate_recommendations(health_status, emergency_fund_ratio, forecast_summary):
    """Generate personalized financial recommendations"""
    recommendations = []

    if emergency_fund_ratio < 0.15:
        recommendations.append(
            "Consider building a larger emergency fund (cash reserves)"
        )

    if forecast_summary["extra_payment_needed"] > 0:
        recommendations.append(
            f"Consider adding ${forecast_summary['extra_payment_needed']:.2f} to maintain your buffer"
        )

    if forecast_summary["buffer_status"] == "Danger":
        recommendations.append(
            "Your projected balance is below the safety buffer - review upcoming expenses"
        )

    if health_status == "Poor":
        recommendations.append(
            "Focus on reducing expenses and increasing income sources"
        )
    elif health_status == "Fair":
        recommendations.append(
            "You're on the right track - continue building your savings"
        )
    elif health_status == "Good":
        recommendations.append(
            "Consider optimizing your fund allocations for better returns"
        )
    else:
        recommendations.append(
            "Excellent financial health - consider investment opportunities"
        )

    return recommendations


@reports_bp.route("/income-breakdown", methods=["GET"])
@jwt_required()
def income_breakdown():
    """Get income breakdown by category for charts"""
    try:
        user_id = get_jwt_identity()

        # Get income data grouped by category
        from sqlalchemy import func

        income_data = (
            Income.query.with_entities(
                Income.category, func.sum(Income.amount).label("total_amount")
            )
            .filter_by(user_id=user_id)
            .group_by(Income.category)
            .all()
        )

        chart_data = [
            {"category": category, "amount": float(total_amount)}
            for category, total_amount in income_data
        ]

        return jsonify(chart_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/debt-breakdown", methods=["GET"])
@jwt_required()
def debt_breakdown():
    """Get debt breakdown by category for charts"""
    try:
        user_id = get_jwt_identity()

        # Get debt data grouped by category
        from sqlalchemy import func

        debt_data = (
            Debt.query.with_entities(
                Debt.category, func.sum(Debt.current_balance).label("total_balance")
            )
            .filter_by(user_id=user_id, is_active=True)
            .group_by(Debt.category)
            .all()
        )

        chart_data = [
            {"category": category, "amount": float(total_balance)}
            for category, total_balance in debt_data
        ]

        return jsonify(chart_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
