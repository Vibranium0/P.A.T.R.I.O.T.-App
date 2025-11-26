"""
Financial accounts routes
"""
from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models.account import Account
from backend.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.auth_helpers import get_current_household_id, get_current_user_id

financial_accounts_bp = Blueprint("financial_accounts", __name__)

@financial_accounts_bp.route("/", methods=["GET"])
@jwt_required()
def get_accounts():
    """Get all financial accounts for the current user."""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    accounts = Account.query.filter_by(household_id=household_id, is_active=True).all()
    
    return jsonify({
        "accounts": [account.to_dict() for account in accounts],
        "count": len(accounts)
    }), 200


@financial_accounts_bp.route("/", methods=["POST"])
@jwt_required()
def create_account():
    """Create a new financial account."""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    current_user_id = get_current_user_id()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["name", "type", "institution"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        account = Account(
            household_id=household_id,
            owner_user_id=current_user_id,
            name=data["name"],
            type=data["type"],
            institution=data["institution"],
            balance=data.get("balance", 0.00),
            last_four=data.get("last_four"),
            is_active=True
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            "message": "Account created successfully",
            "account": account.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@financial_accounts_bp.route("/<int:account_id>", methods=["GET"])
@jwt_required()
def get_account(account_id):
    """Get a specific financial account."""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    account = Account.query.filter_by(id=account_id, household_id=household_id).first()
    
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    return jsonify({"account": account.to_dict()}), 200


@financial_accounts_bp.route("/<int:account_id>", methods=["PUT"])
@jwt_required()
def update_account(account_id):
    """Update a financial account."""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    data = request.get_json()
    
    account = Account.query.filter_by(id=account_id, household_id=household_id).first()
    
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    try:
        # Update fields
        account.name = data.get("name", account.name)
        account.type = data.get("type", account.type)
        account.institution = data.get("institution", account.institution)
        account.balance = data.get("balance", account.balance)
        account.last_four = data.get("last_four", account.last_four)
        
        db.session.commit()
        
        return jsonify({
            "message": "Account updated successfully",
            "account": account.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@financial_accounts_bp.route("/<int:account_id>", methods=["DELETE"])
@jwt_required()
def delete_account(account_id):
    """Delete (deactivate) a financial account."""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    account = Account.query.filter_by(id=account_id, household_id=household_id).first()
    
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    try:
        # Soft delete
        account.is_active = False
        db.session.commit()
        
        return jsonify({"message": "Account deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
