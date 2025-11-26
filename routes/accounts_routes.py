from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import User  # or Account if separate
from flask_jwt_extended import jwt_required, get_jwt_identity

accounts_bp = Blueprint("accounts", __name__)

@accounts_bp.route("/", methods=["GET"])
@jwt_required()
def get_account():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "theme": user.theme
    }), 200


@accounts_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_account():
    user_id = get_jwt_identity()
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.name = data.get("name", user.name)
    user.theme = data.get("theme", user.theme)
    db.session.commit()

    return jsonify({"message": "Account updated", "user": {
        "id": user.id,
        "username": user.username,
        "theme": user.theme
    }}), 200
