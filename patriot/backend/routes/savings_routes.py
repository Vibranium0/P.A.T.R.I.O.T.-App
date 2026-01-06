"""
Savings routes - CRUD endpoints for savings transactions
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from patriot.backend.database import db
from patriot.backend.models.saving import Saving
from patriot.backend.models.account import Account
from patriot.backend.models.fund import Fund
from patriot.backend.models.goal import Goal
from patriot.backend.models.category import Category
from shared.utils.household_helpers import get_current_household_id, get_current_user_id

savings_bp = Blueprint("savings", __name__)


@savings_bp.route("/", methods=["GET"])
@jwt_required()
def get_savings():
    """Get all savings transactions for the current household"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Optional filters
    account_id = request.args.get("account_id")
    fund_id = request.args.get("fund_id")
    goal_id = request.args.get("goal_id")
    transaction_type = request.args.get("transaction_type")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort_by = request.args.get("sort_by", "date")
    order = request.args.get("order", "desc")

    query = Saving.query.filter_by(household_id=household_id)

    # Apply filters
    if account_id:
        query = query.filter_by(account_id=int(account_id))
    if fund_id:
        query = query.filter_by(fund_id=int(fund_id))
    if goal_id:
        query = query.filter_by(goal_id=int(goal_id))
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    if start_date:
        query = query.filter(Saving.date >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(Saving.date <= datetime.fromisoformat(end_date).date())

    # Apply sorting
    if sort_by == "date":
        query = query.order_by(Saving.date.desc() if order == "desc" else Saving.date.asc())
    elif sort_by == "amount":
        query = query.order_by(Saving.amount.desc() if order == "desc" else Saving.amount.asc())

    savings = query.all()

    return jsonify({
        "savings": [saving.to_dict() for saving in savings],
        "count": len(savings)
    }), 200


@savings_bp.route("/<int:saving_id>", methods=["GET"])
@jwt_required()
def get_saving(saving_id):
    """Get a specific savings transaction"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    saving = Saving.query.filter_by(
        id=saving_id,
        household_id=household_id
    ).first()

    if not saving:
        return jsonify({"error": "Savings transaction not found"}), 404

    return jsonify(saving.to_dict()), 200


@savings_bp.route("/", methods=["POST"])
@jwt_required()
def create_saving():
    """Create a new savings transaction"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    user_id = get_current_user_id()
    data = request.get_json()

    # Validate required fields
    if not data.get("amount"):
        return jsonify({"error": "Amount is required"}), 400
    if not data.get("transaction_type"):
        return jsonify({"error": "Transaction type is required"}), 400

    # Validate transaction_type
    valid_types = ["deposit", "withdrawal", "interest"]
    if data["transaction_type"] not in valid_types:
        return jsonify({"error": f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"}), 400

    # Validate account if provided
    if data.get("account_id"):
        account = Account.query.filter_by(
            id=data["account_id"],
            household_id=household_id
        ).first()
        if not account:
            return jsonify({"error": "Account not found"}), 404

    # Validate fund if provided
    if data.get("fund_id"):
        fund = Fund.query.filter_by(
            id=data["fund_id"],
            household_id=household_id
        ).first()
        if not fund:
            return jsonify({"error": "Fund not found"}), 404

    # Validate goal if provided
    if data.get("goal_id"):
        goal = Goal.query.filter_by(
            id=data["goal_id"],
            household_id=household_id
        ).first()
        if not goal:
            return jsonify({"error": "Goal not found"}), 404

    # Validate category if provided
    if data.get("category_id"):
        category = Category.query.filter_by(
            id=data["category_id"],
            household_id=household_id
        ).first()
        if not category:
            return jsonify({"error": "Category not found"}), 404

    try:
        # Parse date
        saving_date = date.today()
        if data.get("date"):
            saving_date = datetime.fromisoformat(data["date"]).date()

        saving = Saving(
            household_id=household_id,
            created_by_user_id=user_id,
            account_id=data.get("account_id"),
            fund_id=data.get("fund_id"),
            goal_id=data.get("goal_id"),
            category_id=data.get("category_id"),
            date=saving_date,
            amount=float(data["amount"]),
            transaction_type=data["transaction_type"],
            source=data.get("source"),
            description=data.get("description"),
            is_recurring=data.get("is_recurring", False),
            is_automatic=data.get("is_automatic", False),
            notes=data.get("notes")
        )

        db.session.add(saving)
        db.session.commit()

        return jsonify({
            "message": "Savings transaction created successfully",
            "saving": saving.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create savings transaction: {str(e)}"}), 500


@savings_bp.route("/<int:saving_id>", methods=["PUT"])
@jwt_required()
def update_saving(saving_id):
    """Update a savings transaction"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    saving = Saving.query.filter_by(
        id=saving_id,
        household_id=household_id
    ).first()

    if not saving:
        return jsonify({"error": "Savings transaction not found"}), 404

    data = request.get_json()

    try:
        # Update fields if provided
        if "amount" in data:
            saving.amount = float(data["amount"])
        if "transaction_type" in data:
            valid_types = ["deposit", "withdrawal", "interest"]
            if data["transaction_type"] not in valid_types:
                return jsonify({"error": f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"}), 400
            saving.transaction_type = data["transaction_type"]
        if "date" in data:
            saving.date = datetime.fromisoformat(data["date"]).date()
        if "source" in data:
            saving.source = data["source"]
        if "description" in data:
            saving.description = data["description"]
        if "is_recurring" in data:
            saving.is_recurring = data["is_recurring"]
        if "is_automatic" in data:
            saving.is_automatic = data["is_automatic"]
        if "notes" in data:
            saving.notes = data["notes"]
        
        # Validate and update account
        if "account_id" in data:
            if data["account_id"]:
                account = Account.query.filter_by(
                    id=data["account_id"],
                    household_id=household_id
                ).first()
                if not account:
                    return jsonify({"error": "Account not found"}), 404
            saving.account_id = data["account_id"]
        
        # Validate and update fund
        if "fund_id" in data:
            if data["fund_id"]:
                fund = Fund.query.filter_by(
                    id=data["fund_id"],
                    household_id=household_id
                ).first()
                if not fund:
                    return jsonify({"error": "Fund not found"}), 404
            saving.fund_id = data["fund_id"]
        
        # Validate and update goal
        if "goal_id" in data:
            if data["goal_id"]:
                goal = Goal.query.filter_by(
                    id=data["goal_id"],
                    household_id=household_id
                ).first()
                if not goal:
                    return jsonify({"error": "Goal not found"}), 404
            saving.goal_id = data["goal_id"]
        
        # Validate and update category
        if "category_id" in data:
            if data["category_id"]:
                category = Category.query.filter_by(
                    id=data["category_id"],
                    household_id=household_id
                ).first()
                if not category:
                    return jsonify({"error": "Category not found"}), 404
            saving.category_id = data["category_id"]

        db.session.commit()

        return jsonify({
            "message": "Savings transaction updated successfully",
            "saving": saving.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update savings transaction: {str(e)}"}), 500


@savings_bp.route("/<int:saving_id>", methods=["DELETE"])
@jwt_required()
def delete_saving(saving_id):
    """Delete a savings transaction"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    saving = Saving.query.filter_by(
        id=saving_id,
        household_id=household_id
    ).first()

    if not saving:
        return jsonify({"error": "Savings transaction not found"}), 404

    try:
        db.session.delete(saving)
        db.session.commit()

        return jsonify({"message": "Savings transaction deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete savings transaction: {str(e)}"}), 500


@savings_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_savings_stats():
    """Get savings statistics for the household"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Get date range from query params
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400

    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        # Get net savings
        net_savings = Saving.get_net_savings(household_id, start, end)

        # Get totals by type
        deposits = Saving.get_total_for_period(household_id, start, end, "deposit")
        withdrawals = Saving.get_total_for_period(household_id, start, end, "withdrawal")
        interest = Saving.get_total_for_period(household_id, start, end, "interest")

        # Get savings rate
        savings_rate = Saving.get_savings_rate(household_id, start, end)

        # Get monthly average
        monthly_avg = Saving.get_monthly_average(household_id, months=6)

        return jsonify({
            "net_savings": net_savings,
            "deposits": deposits,
            "withdrawals": withdrawals,
            "interest": interest,
            "savings_rate": savings_rate,
            "monthly_average": monthly_avg,
            "start_date": start_date,
            "end_date": end_date
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to calculate stats: {str(e)}"}), 500


@savings_bp.route("/by-goal/<int:goal_id>", methods=["GET"])
@jwt_required()
def get_savings_by_goal(goal_id):
    """Get all savings transactions for a specific goal"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Verify goal belongs to household
    goal = Goal.query.filter_by(
        id=goal_id,
        household_id=household_id
    ).first()

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    savings = Saving.get_by_goal(household_id, goal_id)

    return jsonify({
        "goal": goal.to_dict(),
        "savings": [saving.to_dict() for saving in savings],
        "count": len(savings)
    }), 200


@savings_bp.route("/by-fund/<int:fund_id>", methods=["GET"])
@jwt_required()
def get_savings_by_fund(fund_id):
    """Get all savings transactions for a specific fund"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Verify fund belongs to household
    fund = Fund.query.filter_by(
        id=fund_id,
        household_id=household_id
    ).first()

    if not fund:
        return jsonify({"error": "Fund not found"}), 404

    savings = Saving.get_by_fund(household_id, fund_id)

    return jsonify({
        "fund": fund.to_dict(),
        "savings": [saving.to_dict() for saving in savings],
        "count": len(savings)
    }), 200
