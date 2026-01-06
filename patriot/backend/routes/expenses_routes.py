"""
Expenses routes - CRUD endpoints for expense tracking
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from patriot.backend.database import db
from patriot.backend.models.expense import Expense
from patriot.backend.models.category import Category
from patriot.backend.models.account import Account
from shared.utils.household_helpers import get_current_household_id, get_current_user_id

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/", methods=["GET"])
@jwt_required()
def get_expenses():
    """Get all expenses for the current household"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Optional filters
    category_id = request.args.get("category_id")
    account_id = request.args.get("account_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    merchant = request.args.get("merchant")
    min_amount = request.args.get("min_amount")
    max_amount = request.args.get("max_amount")
    sort_by = request.args.get("sort_by", "date")
    order = request.args.get("order", "desc")

    query = Expense.query.filter_by(household_id=household_id)

    # Apply filters
    if category_id:
        query = query.filter_by(category_id=int(category_id))
    if account_id:
        query = query.filter_by(account_id=int(account_id))
    if start_date:
        query = query.filter(Expense.date >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(Expense.date <= datetime.fromisoformat(end_date).date())
    if merchant:
        query = query.filter(Expense.merchant.ilike(f"%{merchant}%"))
    if min_amount:
        query = query.filter(Expense.amount >= float(min_amount))
    if max_amount:
        query = query.filter(Expense.amount <= float(max_amount))

    # Apply sorting
    if sort_by == "date":
        query = query.order_by(Expense.date.desc() if order == "desc" else Expense.date.asc())
    elif sort_by == "amount":
        query = query.order_by(Expense.amount.desc() if order == "desc" else Expense.amount.asc())
    elif sort_by == "merchant":
        query = query.order_by(Expense.merchant.desc() if order == "desc" else Expense.merchant.asc())

    expenses = query.all()

    return jsonify({
        "expenses": [exp.to_dict() for exp in expenses],
        "count": len(expenses)
    }), 200


@expenses_bp.route("/<int:expense_id>", methods=["GET"])
@jwt_required()
def get_expense(expense_id):
    """Get a specific expense"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    expense = Expense.query.filter_by(
        id=expense_id,
        household_id=household_id
    ).first()

    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify(expense.to_dict()), 200


@expenses_bp.route("/", methods=["POST"])
@jwt_required()
def create_expense():
    """Create a new expense"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    user_id = get_current_user_id()
    data = request.get_json()

    # Validate required fields
    if not data.get("amount"):
        return jsonify({"error": "Amount is required"}), 400
    if not data.get("description"):
        return jsonify({"error": "Description is required"}), 400

    # Validate category if provided
    if data.get("category_id"):
        category = Category.query.filter_by(
            id=data["category_id"],
            household_id=household_id
        ).first()
        if not category:
            return jsonify({"error": "Category not found"}), 404

    # Validate account if provided
    if data.get("account_id"):
        account = Account.query.filter_by(
            id=data["account_id"],
            household_id=household_id
        ).first()
        if not account:
            return jsonify({"error": "Account not found"}), 404

    try:
        # Parse date
        expense_date = date.today()
        if data.get("date"):
            expense_date = datetime.fromisoformat(data["date"]).date()

        expense = Expense(
            household_id=household_id,
            created_by_user_id=user_id,
            account_id=data.get("account_id"),
            category_id=data.get("category_id"),
            bill_id=data.get("bill_id"),
            date=expense_date,
            amount=float(data["amount"]),
            description=data["description"],
            merchant=data.get("merchant"),
            payment_method=data.get("payment_method"),
            is_recurring=data.get("is_recurring", False),
            tags=data.get("tags"),
            receipt_url=data.get("receipt_url"),
            notes=data.get("notes")
        )

        db.session.add(expense)
        db.session.commit()

        return jsonify({
            "message": "Expense created successfully",
            "expense": expense.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create expense: {str(e)}"}), 500


@expenses_bp.route("/<int:expense_id>", methods=["PUT"])
@jwt_required()
def update_expense(expense_id):
    """Update an expense"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    expense = Expense.query.filter_by(
        id=expense_id,
        household_id=household_id
    ).first()

    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    data = request.get_json()

    try:
        # Update fields if provided
        if "amount" in data:
            expense.amount = float(data["amount"])
        if "description" in data:
            expense.description = data["description"]
        if "date" in data:
            expense.date = datetime.fromisoformat(data["date"]).date()
        if "merchant" in data:
            expense.merchant = data["merchant"]
        if "payment_method" in data:
            expense.payment_method = data["payment_method"]
        if "is_recurring" in data:
            expense.is_recurring = data["is_recurring"]
        if "tags" in data:
            expense.tags = data["tags"]
        if "receipt_url" in data:
            expense.receipt_url = data["receipt_url"]
        if "notes" in data:
            expense.notes = data["notes"]
        
        # Validate and update category
        if "category_id" in data:
            if data["category_id"]:
                category = Category.query.filter_by(
                    id=data["category_id"],
                    household_id=household_id
                ).first()
                if not category:
                    return jsonify({"error": "Category not found"}), 404
            expense.category_id = data["category_id"]
        
        # Validate and update account
        if "account_id" in data:
            if data["account_id"]:
                account = Account.query.filter_by(
                    id=data["account_id"],
                    household_id=household_id
                ).first()
                if not account:
                    return jsonify({"error": "Account not found"}), 404
            expense.account_id = data["account_id"]

        db.session.commit()

        return jsonify({
            "message": "Expense updated successfully",
            "expense": expense.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update expense: {str(e)}"}), 500


@expenses_bp.route("/<int:expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(expense_id):
    """Delete an expense"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    expense = Expense.query.filter_by(
        id=expense_id,
        household_id=household_id
    ).first()

    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    try:
        db.session.delete(expense)
        db.session.commit()

        return jsonify({"message": "Expense deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete expense: {str(e)}"}), 500


@expenses_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_expense_stats():
    """Get expense statistics for the household"""
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

        # Get total for period
        total = Expense.get_total_for_period(household_id, start, end)

        # Get totals by category
        by_category = Expense.get_total_by_category(household_id, start, end)
        
        category_data = []
        for total_amount, category_id in by_category:
            if category_id:
                category = Category.query.get(category_id)
                category_data.append({
                    "category_id": category_id,
                    "category_name": category.name if category else "Unknown",
                    "total": float(total_amount)
                })

        # Get monthly average
        monthly_avg = Expense.get_monthly_average(household_id, months=6)

        return jsonify({
            "total": total,
            "by_category": category_data,
            "monthly_average": monthly_avg,
            "start_date": start_date,
            "end_date": end_date
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to calculate stats: {str(e)}"}), 500
