from flask import Blueprint, request, jsonify
from patriot.backend.database import db
from patriot.backend.models.user import User
from shared.auth.token_required import require_token

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/", methods=["GET"])
@require_token
def get_account():
    user_info = getattr(request, "user", None)
    if not user_info or "id" not in user_info:
        return jsonify({"error": "User not found"}), 404
    user = User.query.get(user_info["id"])
    if not user:
        return jsonify({"error": "User not found"}), 404
    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "theme": user.theme,
            }
        ),
        200,
    )


@accounts_bp.route("/update", methods=["PUT"])
@require_token
def update_account():
    user_info = getattr(request, "user", None)
    if not user_info or "id" not in user_info:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    user = User.query.get(user_info["id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.name = data.get("name", user.name)
    user.theme = data.get("theme", user.theme)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Account updated",
                "user": {"id": user.id, "username": user.username, "theme": user.theme},
            }
        ),
        200,
    )
