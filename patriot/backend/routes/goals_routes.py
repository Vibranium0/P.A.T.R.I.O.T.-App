"""
Goals routes - CRUD endpoints for financial goals
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from patriot.backend.database import db
from patriot.backend.models.goal import Goal
from patriot.backend.models.account import Account
from patriot.backend.models.fund import Fund
from shared.utils.household_helpers import get_current_household_id, get_current_user_id

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("/", methods=["GET"])
@jwt_required()
def get_goals():
    """Get all goals for the current household"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Optional filters
    is_active = request.args.get("is_active")
    is_completed = request.args.get("is_completed")
    category = request.args.get("category")
    priority = request.args.get("priority")

    query = Goal.query.filter_by(household_id=household_id)

    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == "true")
    if is_completed is not None:
        query = query.filter_by(is_completed=is_completed.lower() == "true")
    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)

    goals = query.order_by(Goal.target_date.asc()).all()

    return jsonify({
        "goals": [goal.to_dict() for goal in goals],
        "count": len(goals)
    }), 200


@goals_bp.route("/active", methods=["GET"])
@jwt_required()
def get_active_goals():
    """Get all active (not completed) goals"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    goals = Goal.get_active_goals(household_id)

    return jsonify({
        "goals": [goal.to_dict() for goal in goals],
        "count": len(goals)
    }), 200


@goals_bp.route("/completed", methods=["GET"])
@jwt_required()
def get_completed_goals():
    """Get all completed goals"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    goals = Goal.get_completed_goals(household_id)

    return jsonify({
        "goals": [goal.to_dict() for goal in goals],
        "count": len(goals)
    }), 200


@goals_bp.route("/<int:goal_id>", methods=["GET"])
@jwt_required()
def get_goal(goal_id):
    """Get a specific goal"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    goal = Goal.query.filter_by(
        id=goal_id,
        household_id=household_id
    ).first()

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    return jsonify(goal.to_dict()), 200


@goals_bp.route("/", methods=["POST"])
@jwt_required()
def create_goal():
    """Create a new goal"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    user_id = get_current_user_id()
    data = request.get_json()

    # Validate required fields
    if not data.get("name"):
        return jsonify({"error": "Goal name is required"}), 400
    if not data.get("target_amount"):
        return jsonify({"error": "Target amount is required"}), 400

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

    try:
        # Parse dates
        target_date = None
        if data.get("target_date"):
            target_date = datetime.fromisoformat(data["target_date"]).date()
        
        start_date = date.today()
        if data.get("start_date"):
            start_date = datetime.fromisoformat(data["start_date"]).date()

        goal = Goal(
            household_id=household_id,
            created_by_user_id=user_id,
            name=data["name"],
            description=data.get("description"),
            target_amount=float(data["target_amount"]),
            current_amount=float(data.get("current_amount", 0)),
            target_date=target_date,
            start_date=start_date,
            category=data.get("category"),
            priority=data.get("priority", "medium"),
            fund_id=data.get("fund_id"),
            account_id=data.get("account_id"),
            icon=data.get("icon"),
            color=data.get("color"),
            notes=data.get("notes")
        )

        db.session.add(goal)
        db.session.commit()

        return jsonify({
            "message": "Goal created successfully",
            "goal": goal.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create goal: {str(e)}"}), 500


@goals_bp.route("/<int:goal_id>", methods=["PUT"])
@jwt_required()
def update_goal(goal_id):
    """Update a goal"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    goal = Goal.query.filter_by(
        id=goal_id,
        household_id=household_id
    ).first()

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    data = request.get_json()

    try:
        # Update fields if provided
        if "name" in data:
            goal.name = data["name"]
        if "description" in data:
            goal.description = data["description"]
        if "target_amount" in data:
            goal.target_amount = float(data["target_amount"])
        if "current_amount" in data:
            goal.current_amount = float(data["current_amount"])
        if "target_date" in data:
            if data["target_date"]:
                goal.target_date = datetime.fromisoformat(data["target_date"]).date()
            else:
                goal.target_date = None
        if "category" in data:
            goal.category = data["category"]
        if "priority" in data:
            goal.priority = data["priority"]
        if "icon" in data:
            goal.icon = data["icon"]
        if "color" in data:
            goal.color = data["color"]
        if "notes" in data:
            goal.notes = data["notes"]
        if "is_active" in data:
            goal.is_active = data["is_active"]
        
        # Validate and update account
        if "account_id" in data:
            if data["account_id"]:
                account = Account.query.filter_by(
                    id=data["account_id"],
                    household_id=household_id
                ).first()
                if not account:
                    return jsonify({"error": "Account not found"}), 404
            goal.account_id = data["account_id"]
        
        # Validate and update fund
        if "fund_id" in data:
            if data["fund_id"]:
                fund = Fund.query.filter_by(
                    id=data["fund_id"],
                    household_id=household_id
                ).first()
                if not fund:
                    return jsonify({"error": "Fund not found"}), 404
            goal.fund_id = data["fund_id"]

        db.session.commit()

        return jsonify({
            "message": "Goal updated successfully",
            "goal": goal.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update goal: {str(e)}"}), 500


@goals_bp.route("/<int:goal_id>", methods=["DELETE"])
@jwt_required()
def delete_goal(goal_id):
    """Delete a goal"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    goal = Goal.query.filter_by(
        id=goal_id,
        household_id=household_id
    ).first()

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    try:
        db.session.delete(goal)
        db.session.commit()

        return jsonify({"message": "Goal deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete goal: {str(e)}"}), 500


@goals_bp.route("/<int:goal_id>/contribute", methods=["POST"])
@jwt_required()
def contribute_to_goal(goal_id):
    """Add a contribution to a goal"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    goal = Goal.query.filter_by(
        id=goal_id,
        household_id=household_id
    ).first()

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    data = request.get_json()

    if not data.get("amount"):
        return jsonify({"error": "Contribution amount is required"}), 400

    try:
        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Contribution amount must be positive"}), 400

        success = goal.add_contribution(amount)
        if not success:
            return jsonify({"error": "Failed to add contribution"}), 400

        db.session.commit()

        return jsonify({
            "message": "Contribution added successfully",
            "goal": goal.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add contribution: {str(e)}"}), 500


@goals_bp.route("/<int:goal_id>/withdraw", methods=["POST"])
@jwt_required()
def withdraw_from_goal(goal_id):
    """Withdraw from a goal"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    goal = Goal.query.filter_by(
        id=goal_id,
        household_id=household_id
    ).first()

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    data = request.get_json()

    if not data.get("amount"):
        return jsonify({"error": "Withdrawal amount is required"}), 400

    try:
        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Withdrawal amount must be positive"}), 400

        success = goal.withdraw(amount)
        if not success:
            return jsonify({"error": "Insufficient funds in goal"}), 400

        db.session.commit()

        return jsonify({
            "message": "Withdrawal processed successfully",
            "goal": goal.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to process withdrawal: {str(e)}"}), 500
