# backend/routes/debts_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import db
from backend.models.debt import Debt
from datetime import datetime, date
from backend.utils.auth_helpers import get_current_household_id, get_current_user_id

debts_bp = Blueprint("debts", __name__)


@debts_bp.route("/", methods=["GET"])
@jwt_required()
def get_debts():
    """Get all debts for the current user"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        debts = Debt.query.filter_by(household_id=household_id, is_active=True).all()
        return jsonify([debt.to_dict() for debt in debts]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@debts_bp.route("/", methods=["POST"])
@jwt_required()
def create_debt():
    """Create a new debt"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        current_user_id = get_current_user_id()
        data = request.get_json()

        # Validate required fields
        required_fields = [
            "name",
            "total_amount",
            "current_balance",
            "minimum_payment",
            "due_date",
            "category",
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Parse due_date
        try:
            due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}), 400

        debt = Debt(
            household_id=household_id,
            owner_user_id=current_user_id,
            name=data["name"],
            description=data.get("description", ""),
            total_amount=float(data["total_amount"]),
            current_balance=float(data["current_balance"]),
            minimum_payment=float(data["minimum_payment"]),
            interest_rate=float(data.get("interest_rate", 0.0)),
            due_date=due_date,
            category=data["category"],
            account_number=data.get("account_number", ""),
        )

        db.session.add(debt)
        db.session.commit()

        return jsonify(debt.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@debts_bp.route("/<int:debt_id>", methods=["GET"])
@jwt_required()
def get_debt(debt_id):
    """Get a specific debt"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        debt = Debt.query.filter_by(id=debt_id, household_id=household_id).first()

        if not debt:
            return jsonify({"error": "Debt not found"}), 404

        return jsonify(debt.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@debts_bp.route("/<int:debt_id>", methods=["PUT"])
@jwt_required()
def update_debt(debt_id):
    """Update a specific debt"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        debt = Debt.query.filter_by(id=debt_id, household_id=household_id).first()

        if not debt:
            return jsonify({"error": "Debt not found"}), 404

        data = request.get_json()

        # Update fields if provided
        if "name" in data:
            debt.name = data["name"]
        if "description" in data:
            debt.description = data["description"]
        if "total_amount" in data:
            debt.total_amount = float(data["total_amount"])
        if "current_balance" in data:
            debt.current_balance = float(data["current_balance"])
        if "minimum_payment" in data:
            debt.minimum_payment = float(data["minimum_payment"])
        if "interest_rate" in data:
            debt.interest_rate = float(data["interest_rate"])
        if "due_date" in data:
            try:
                debt.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
            except ValueError:
                return (
                    jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}),
                    400,
                )
        if "category" in data:
            debt.category = data["category"]
        if "account_number" in data:
            debt.account_number = data["account_number"]
        if "is_active" in data:
            debt.is_active = bool(data["is_active"])

        db.session.commit()
        return jsonify(debt.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@debts_bp.route("/<int:debt_id>", methods=["DELETE"])
@jwt_required()
def delete_debt(debt_id):
    """Delete a specific debt"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        debt = Debt.query.filter_by(id=debt_id, household_id=household_id).first()

        if not debt:
            return jsonify({"error": "Debt not found"}), 404

        db.session.delete(debt)
        db.session.commit()

        return jsonify({"message": "Debt deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@debts_bp.route("/<int:debt_id>/payment", methods=["POST"])
@jwt_required()
def make_payment(debt_id):
    """Make a payment towards a debt"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        debt = Debt.query.filter_by(id=debt_id, household_id=household_id).first()

        if not debt:
            return jsonify({"error": "Debt not found"}), 404

        data = request.get_json()
        if "amount" not in data:
            return jsonify({"error": "Payment amount is required"}), 400

        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Payment amount must be positive"}), 400

        if amount > debt.current_balance:
            return (
                jsonify({"error": "Payment amount cannot exceed current balance"}),
                400,
            )

        # Make the payment
        debt.make_payment(amount)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Payment of ${amount:.2f} applied successfully",
                    "debt": debt.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@debts_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_debt_summary():
    """Get debt summary for the current user"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404

        total_debt = Debt.get_total_debt(household_id)
        total_minimum_payments = Debt.get_total_minimum_payments(household_id)

        # Get debt breakdown by category
        debts_by_category = (
            db.session.query(
                Debt.category,
                db.func.sum(Debt.current_balance).label("total_balance"),
                db.func.count(Debt.id).label("count"),
            )
            .filter_by(household_id=household_id, is_active=True)
            .group_by(Debt.category)
            .all()
        )

        category_breakdown = [
            {
                "category": category,
                "total_balance": float(total_balance),
                "count": count,
            }
            for category, total_balance, count in debts_by_category
        ]

        return (
            jsonify(
                {
                    "total_debt": float(total_debt),
                    "total_minimum_payments": float(total_minimum_payments),
                    "category_breakdown": category_breakdown,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
