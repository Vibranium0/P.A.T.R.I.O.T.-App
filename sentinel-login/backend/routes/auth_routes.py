from sqlalchemy.exc import SQLAlchemyError


# --- Password Reset with Security Question ---
@auth_bp.route("/password-reset/request", methods=["POST"])
def password_reset_request():
    data = request.get_json()
    identifier = data.get("email") or data.get("username")
    if not identifier:
        return jsonify({"error": "username or email required"}), 400
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()
    if not user or not user.security_question:
        return jsonify({"error": "user not found or no security question set"}), 404
    return jsonify({"security_question": user.security_question}), 200


@auth_bp.route("/password-reset/confirm", methods=["POST"])
def password_reset_confirm():
    data = request.get_json()
    identifier = data.get("email") or data.get("username")
    security_answer = data.get("security_answer")
    new_password = data.get("new_password")
    if not identifier or not security_answer or not new_password:
        return (
            jsonify(
                {"error": "username/email, security answer, and new password required"}
            ),
            400,
        )
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()
    if not user or not user.security_answer:
        return jsonify({"error": "user not found or no security answer set"}), 404
    if user.security_answer.strip().lower() != security_answer.strip().lower():
        return jsonify({"error": "incorrect security answer"}), 403
    bcrypt = Bcrypt(current_app)
    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "database error"}), 500
    return jsonify({"message": "password reset successful"}), 200


from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import secrets
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
    get_jwt,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/validate", methods=["GET"])
@jwt_required()
def validate():
    """
    Validate JWT and return user info. Returns 200 if valid, 401 if not.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "user not found"}), 404
    return (
        jsonify(
            {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "household_id": user.default_household_id,
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Issue a new access token using a valid refresh token.
    Expects Authorization: Bearer <refresh_token>
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "user not found"}), 404
    additional_claims = {"household_id": user.default_household_id}
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims,
        expires_delta=timedelta(days=1),
    )
    return jsonify({"access_token": access_token}), 200


from flask_bcrypt import Bcrypt
from database import db
from sentinel_login.backend.models.user import User
from sentinel_login.backend.models.household import Household


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    security_question = data.get("security_question")
    security_answer = data.get("security_answer")

    if (
        not username
        or not password
        or not email
        or not security_question
        or not security_answer
    ):
        return (
            jsonify(
                {
                    "error": "username, email, password, security question, and answer required"
                }
            ),
            400,
        )

    existing = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        return jsonify({"error": "user exists"}), 409

    bcrypt = Bcrypt(current_app)
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")

    # Create a new household for the user
    household = Household()
    db.session.add(household)
    db.session.flush()  # get household.id before commit

    user = User(
        username=username,
        email=email,
        password=hashed,
        default_household_id=household.id,
        security_question=security_question,
        security_answer=security_answer,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "registered"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    identifier = data.get("email") or data.get("username")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "username/email and password required"}), 400

    # Try to find user by email OR username
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    # Sentinel sync logic removed: no cross-app sync available in sentinel-login

    if not user:
        return jsonify({"error": "user not found"}), 404

    bcrypt = Bcrypt(current_app)
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "invalid password"}), 401

    # Include household_id in JWT claims
    additional_claims = {"household_id": user.default_household_id}
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims,
        expires_delta=timedelta(days=1),
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "username": user.username,
                "email": user.email,
                "household_id": user.default_household_id,
            }
        ),
        200,
    )


@auth_bp.route("/test-jwt", methods=["GET"])
@jwt_required()
def test_jwt():
    """Test endpoint to verify JWT is working"""
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    return (
        jsonify(
            {
                "message": "JWT is working!",
                "user_id": current_user_id,
                "username": user.username if user else "Unknown",
            }
        ),
        200,
    )


# ============================================================================
# SENTINEL SYSTEMS - User Sync Endpoints
# These endpoints allow Sentinel apps to share user accounts
# ============================================================================


@auth_bp.route("/sentinel/user-lookup", methods=["GET"])
def sentinel_user_lookup():
    """
    Lookup user for Sentinel Systems cross-app sync.
    Other Sentinel apps call this to find if a user exists here.

    Query params:
        identifier: username or email to search for

    Returns:
        User data (without sensitive tokens) or 404
    """
    identifier = request.args.get("identifier")

    if not identifier:
        return jsonify({"error": "identifier parameter required"}), 400

    # Find user by username or email
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    if not user:
        return jsonify({"error": "user not found"}), 404

    # Return user data (password hash is safe to share - it's already hashed)
    return (
        jsonify(
            {
                "username": user.username,
                "email": user.email,
                "password": user.password,  # Already hashed, safe to sync
                "synced_from": current_app.config.get("APP_NAME", "Unknown App"),
            }
        ),
        200,
    )


@auth_bp.route("/sentinel/health", methods=["GET"])
def sentinel_health():
    """
    Health check endpoint for Sentinel Systems.
    Other apps use this to verify this app is online and part of the network.
    """
    return (
        jsonify(
            {
                "status": "online",
                "app_name": current_app.config.get("APP_NAME", "Unknown"),
                "version": "1.0.0",
                "sentinel_system": True,
            }
        ),
        200,
    )
