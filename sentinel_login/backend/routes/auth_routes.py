from flask import Blueprint, request, jsonify, current_app, make_response
from datetime import datetime, timedelta
import secrets
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
    get_jwt,
)
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt

from database import db
from models.user import User
from models.household import Household

auth_bp = Blueprint("auth", __name__)


# --- Password Reset with Security Question ---
@auth_bp.route("/password-reset/request", methods=["POST"])
def password_reset_request():
    data = request.get_json()
    identifier = data.get("username")
    if not identifier:
        return jsonify({"error": "username required"}), 400
    user = User.query.filter(
        (User.username == identifier)
    ).first()
    if not user or not user.security_question:
        return jsonify({"error": "user not found or no security question set"}), 404
    return jsonify({"security_question": user.security_question}), 200


@auth_bp.route("/password-reset/confirm", methods=["POST"])
def password_reset_confirm():
    data = request.get_json()
    identifier = data.get("username")
    security_answer = data.get("security_answer")
    new_password = data.get("new_password")
    if not identifier or not security_answer or not new_password:
        return (
            jsonify(
                {"error": "username, security answer, and new password required"}
            ),
            400,
        )
    user = User.query.filter(
        (User.username == identifier)
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
                # "email": user.email,  # Removed
                "household_id": user.default_household_id,
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True, locations=["cookies"])
def refresh():
    """
    Issue a new access token using a valid refresh token from HttpOnly cookie.
    Also issues a new refresh token to implement token rotation.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "user not found"}), 404
    
    # Get remember_me preference from request body if provided
    data = request.get_json() or {}
    remember_me = data.get("remember_me", False)
    
    # Set token durations based on remember_me
    access_expires = timedelta(days=30) if remember_me else timedelta(days=1)
    refresh_expires = timedelta(days=90) if remember_me else timedelta(days=7)
    
    additional_claims = {"household_id": user.default_household_id}
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims,
        expires_delta=access_expires,
    )
    
    # Issue new refresh token (token rotation for security)
    new_refresh_token = create_refresh_token(
        identity=str(user.id),
        expires_delta=refresh_expires
    )
    
    response = make_response(
        jsonify({"access_token": access_token}),
        200
    )
    
    # Set new refresh token as HttpOnly cookie
    response.set_cookie(
        "refresh_token_cookie",  # Flask-JWT-Extended default name
        value=new_refresh_token,
        httponly=True,
        secure=current_app.config.get("JWT_COOKIE_SECURE", False),
        samesite="Lax",
        max_age=int(refresh_expires.total_seconds()),
        path="/",
    )
    
    return response


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logout by clearing the refresh token cookie.
    Access token in memory will be discarded by frontend.
    """
    response = make_response(
        jsonify({"message": "logged out successfully"}),
        200
    )
    
    # Clear the refresh token cookie
    response.set_cookie(
        "refresh_token_cookie",  # Flask-JWT-Extended default name
        value="",
        httponly=True,
        secure=current_app.config.get("JWT_COOKIE_SECURE", False),
        samesite="Lax",
        max_age=0,  # Expire immediately
        path="/",
    )
    
    return response


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    security_question = data.get("security_question")
    security_answer = data.get("security_answer")

    if (
        not username
        or not password
        or not security_question
        or not security_answer
    ):
        return (
            jsonify(
                {
                    "error": "username, password, security question, and answer required"
                }
            ),
            400,
        )

    # Validate field lengths
    if len(username) > 80:
        return jsonify({"error": "username must be 80 characters or less"}), 400
    if len(security_question) > 255:
        return jsonify({"error": "security question must be 255 characters or less"}), 400
    if len(security_answer) > 255:
        return jsonify({"error": "security answer must be 255 characters or less"}), 400

    existing = User.query.filter(
        (User.username == username)
    ).first()
    if existing:
        return jsonify({"error": "user exists"}), 409

    bcrypt = Bcrypt(current_app)
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")

    # Use username as email if email not provided (for backward compatibility)
    email = data.get("email", f"{username}@sentinel.local")
    
    try:
        user = User(
            username=username,
            email=email,
            password_hash=hashed,
            security_question=security_question,
            security_answer=security_answer,
        )
        db.session.add(user)
        db.session.flush()  # get user.id before creating household

        # Create a new household for the user with required fields
        household = Household(
            name=f"{username}'s Household"
        )
        db.session.add(household)
        db.session.flush()  # get household.id before commit

        # Update user's default household
        user.default_household_id = household.id
        db.session.commit()
        return jsonify({"message": "registered"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    identifier = data.get("username")
    password = data.get("password")
    remember_me = data.get("remember_me", False)

    if not identifier or not password:
        return jsonify({"error": "username and password required"}), 400

    # Try to find user by username only
    user = User.query.filter(
        (User.username == identifier)
    ).first()

    # Sentinel sync logic removed: no cross-app sync available in sentinel-login

    if not user:
        return jsonify({"error": "user not found"}), 404

    bcrypt = Bcrypt(current_app)
    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid password"}), 401

    # Include household_id in JWT claims
    additional_claims = {"household_id": user.default_household_id}
    
    # Extend token duration if remember_me is true
    access_expires = timedelta(days=30) if remember_me else timedelta(days=1)
    refresh_expires = timedelta(days=90) if remember_me else timedelta(days=7)
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims,
        expires_delta=access_expires,
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),
        expires_delta=refresh_expires
    )

    # Create response with access token in body
    response = make_response(
        jsonify(
            {
                "access_token": access_token,
                "username": user.username,
                "email": user.email,
                "household_id": user.default_household_id,
                "remember_me": remember_me,
            }
        ),
        200,
    )
    
    # Set refresh token as HttpOnly cookie (XSS protection)
    # Flask-JWT-Extended expects specific cookie names
    response.set_cookie(
        "refresh_token_cookie",  # Flask-JWT-Extended default name
        value=refresh_token,
        httponly=True,
        secure=current_app.config.get("JWT_COOKIE_SECURE", False),  # True in production with HTTPS
        samesite="Lax",  # CSRF protection
        max_age=int(refresh_expires.total_seconds()),
        path="/",
    )
    
    return response


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
