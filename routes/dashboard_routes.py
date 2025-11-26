# backend/routes/dashboard_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from backend.database import db
from backend.models.fund import Fund
from backend.models.transaction import Transaction
from backend.models.income import Income
from sqlalchemy import func, and_
from backend.utils.auth_helpers import get_current_household_id

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_dashboard_summary():
    """Get dashboard summary including income, total, expenses, cash, and savings"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        # Calculate current pay period (last 14 days)
        pay_period_start = date.today() - timedelta(days=14)

        # Get income for current pay period
        income_total = (
            db.session.query(func.sum(Income.amount))
            .filter(
                Income.household_id == household_id, Income.date >= pay_period_start
            )
            .scalar()
            or 0.0
        )

        # Get total recurring deposits (biweekly total)
        total_recurring = Fund.get_total_recurring_amount(household_id)

        # Get totals by fund type
        expenses_total = Fund.get_total_by_type(household_id, "Expenses")
        cash_total = Fund.get_total_by_type(household_id, "Cash")
        savings_total = Fund.get_total_by_type(household_id, "Savings")

        return (
            jsonify(
                {
                    "income": float(income_total),
                    "total": float(total_recurring),
                    "expenses": float(expenses_total),
                    "cash": float(cash_total),
                    "savings": float(savings_total),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/charts/bills", methods=["GET"])
@jwt_required()
def get_bills_chart_data():
    """Get bill spending breakdown for spider chart"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        # Get bills spending by category from transactions
        # Filter for expense transactions in bill categories
        bill_categories = [
            "Utilities",
            "Housing",
            "Subscriptions",
            "Insurance",
            "Loans",
        ]

        chart_data = {"labels": [], "values": []}

        for category in bill_categories:
            # Sum expenses for this category
            total = (
                db.session.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.household_id == household_id,
                    Transaction.category == category,
                    Transaction.transaction_type == "expense",
                )
                .scalar()
                or 0.0
            )

            if total > 0:  # Only include categories with spending
                chart_data["labels"].append(category)
                chart_data["values"].append(float(total))

        # If no data, provide default structure
        if not chart_data["labels"]:
            chart_data = {
                "labels": ["Utilities", "Housing", "Subscriptions"],
                "values": [0, 0, 0],
            }

        return jsonify(chart_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/charts/debts", methods=["GET"])
@jwt_required()
def get_debts_chart_data():
    """Get debt spending breakdown for spider chart"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        # Get debt spending by category from transactions
        debt_categories = [
            "Car Loan",
            "Credit Card",
            "Student Loan",
            "Mortgage",
            "Personal Loan",
        ]

        chart_data = {"labels": [], "values": []}

        for category in debt_categories:
            # Sum expenses for this category
            total = (
                db.session.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.household_id == household_id,
                    Transaction.category == category,
                    Transaction.transaction_type == "expense",
                )
                .scalar()
                or 0.0
            )

            if total > 0:  # Only include categories with spending
                chart_data["labels"].append(category)
                chart_data["values"].append(float(total))

        # If no data, provide default structure
        if not chart_data["labels"]:
            chart_data = {
                "labels": ["Car Loan", "Credit Card", "Student Loan"],
                "values": [0, 0, 0],
            }

        return jsonify(chart_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/process-recurring", methods=["POST"])
@jwt_required()
def process_recurring_deposits():
    """Process all recurring deposits for the current user"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        # Get all funds with recurring deposits
        funds = (
            Fund.query.filter_by(household_id=household_id)
            .filter(Fund.recurring_amount.isnot(None))
            .all()
        )

        processed_count = 0
        total_processed = 0.0

        for fund in funds:
            if fund.process_recurring_deposit():
                processed_count += 1
                total_processed += fund.recurring_amount

        # Commit changes
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Processed {processed_count} recurring deposits",
                    "total_amount": float(total_processed),
                    "processed_funds": processed_count,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
