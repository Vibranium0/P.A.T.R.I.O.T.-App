from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import secrets
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from backend.database import db
from backend.models import User, Household, user_household
from backend.utils.email_service import send_verification_email
from backend.templates.verification_theme import get_verification_styles

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not password or not email:
        return jsonify({"error": "username, email, and password required"}), 400

    existing = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        return jsonify({"error": "user exists"}), 409

    token = secrets.token_urlsafe(32)
    token_exp = datetime.utcnow() + timedelta(hours=24)
    bcrypt = Bcrypt(current_app)
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        email=email,
        password=hashed,
        is_verified=False,
        verification_token=token,
        token_expiration=token_exp,
    )

    db.session.add(user)
    db.session.flush()  # Get user ID before creating household
    
    # Auto-create default household for new user
    household = Household(
        name=f"{username}'s Household",
        created_by=user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(household)
    db.session.flush()
    
    # Add user to household as owner
    db.session.execute(
        user_household.insert().values(
            user_id=user.id,
            household_id=household.id,
            role='owner',
            joined_at=datetime.utcnow()
        )
    )
    
    # Set as default household
    user.default_household_id = household.id
    
    db.session.commit()
    send_verification_email(email, token)

    return jsonify({"message": "registered - verification email sent"}), 201


@auth_bp.route("/verify-email", methods=["GET"])
def verify_email():
    token = request.args.get("token")
    if not token:
        return _verification_page("Error", "Verification token is required.", False)

    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return _verification_page("Error", "Invalid verification token.", False)
    if user.token_expiration and user.token_expiration < datetime.utcnow():
        return _verification_page("Error", "Verification token has expired. Please request a new verification email.", False)

    user.is_verified = True
    user.verification_token = None
    user.token_expiration = None
    db.session.commit()

    return _verification_page("Success", "Your email has been verified successfully! Welcome to P.A.T.R.I.O.T.", True)


def _verification_page(title, message, success):
    """Generate a user-friendly HTML page for email verification results"""
    # Frontend URL for redirecting after verification
    frontend_url = current_app.config['APP_URL']
    login_url = f"{frontend_url}/login"
    register_url = f"{frontend_url}/register"
    
    # Get themed styles
    styles = get_verification_styles()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Verification - Sentinel Systems</title>
        <style>
            {styles}
        </style>
    </head>
    <body>
        <div class="background-logo"></div>
        <div class="container">
            <div class="header">
                <div class="app-name">SENTINEL SYSTEMS</div>
                <h1 class="title">{title}</h1>
                <p class="message">{message}</p>
                {"<a href='" + login_url + "' class='btn'>Continue to Login</a>" if success else "<a href='" + register_url + "' class='btn'>Request New Verification</a>"}
            </div>
        </div>
    </body>
    </html>
    """
    return html


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    identifier = data.get("email")  # Can be username or email
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "username/email and password required"}), 400

    # Try to find user by email OR username
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()
    
    # If user not found locally, try to sync from other Sentinel apps
    if not user:
        from shared.user_sync import get_sync_service
        sync_service = get_sync_service(current_app.config)
        
        if sync_service:
            current_app.logger.info(f"User {identifier} not found locally, attempting Sentinel sync...")
            user = sync_service.auto_sync_on_login(identifier, db.session, User)
            
            if user:
                current_app.logger.info(f"Successfully synced user {identifier} from another Sentinel app")
            else:
                current_app.logger.info(f"User {identifier} not found in any Sentinel app")
    
    if not user:
        return jsonify({"error": "user not found"}), 404

    bcrypt = Bcrypt(current_app)
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "invalid password"}), 401

    if not user.is_verified:
        return jsonify({"error": "email not verified"}), 403

    # Include household_id in JWT claims
    additional_claims = {
        "household_id": user.default_household_id
    }
    token = create_access_token(
        identity=str(user.id), 
        additional_claims=additional_claims,
        expires_delta=timedelta(days=1)
    )
    
    return jsonify({
        "access_token": token, 
        "username": user.username,
        "email": user.email,
        "household_id": user.default_household_id
    }), 200


@auth_bp.route("/test-jwt", methods=["GET"])
@jwt_required()
def test_jwt():
    """Test endpoint to verify JWT is working"""
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    return jsonify({
        "message": "JWT is working!",
        "user_id": current_user_id,
        "username": user.username if user else "Unknown"
    }), 200


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    """
    Resend verification email to user.
    Expects: {"email": "user@example.com"}
    """
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "email required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "user not found"}), 404

    if user.is_verified:
        return jsonify({"error": "user already verified"}), 400

    # Generate new verification token and expiration
    token = secrets.token_urlsafe(32)
    token_exp = datetime.utcnow() + timedelta(hours=24)
    
    # Update user with new token
    user.verification_token = token
    user.token_expiration = token_exp
    db.session.commit()

    # Send verification email
    send_verification_email(email, token)

    return jsonify({"message": "verification email resent"}), 200


@auth_bp.route("/test-verification-page", methods=["GET"])
def test_verification_page():
    """
    Test endpoint to preview the verification page.
    Add ?success=true for success page, or ?success=false for error page
    """
    success = request.args.get("success", "true").lower() == "true"
    
    if success:
        return _verification_page(
            "Success",
            "Your email has been verified successfully! Welcome to P.A.T.R.I.O.T.",
            True
        )
    else:
        return _verification_page(
            "Error",
            "Verification token has expired. Please request a new verification email.",
            False
        )


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Request a password reset email.
    Expects: {"email": "user@example.com"}
    """
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "email required"}), 400

    user = User.query.filter_by(email=email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return jsonify({"message": "If that email exists, a password reset link has been sent"}), 200

    # Generate reset token and expiration (1 hour)
    reset_token = secrets.token_urlsafe(32)
    reset_token_exp = datetime.utcnow() + timedelta(hours=1)
    
    # Store token in user record
    user.verification_token = reset_token
    user.token_expiration = reset_token_exp
    db.session.commit()

    # Send password reset email
    try:
        from utils.email_service import send_password_reset_email
        send_password_reset_email(email, reset_token)
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {str(e)}")
        # Still return success to user for security
    
    return jsonify({"message": "If that email exists, a password reset link has been sent"}), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Reset password with token.
    Expects: {"token": "reset_token", "new_password": "newpass123"}
    """
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"error": "token and new_password required"}), 400

    if len(new_password) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400

    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({"error": "invalid or expired reset token"}), 400
    
    if user.token_expiration and user.token_expiration < datetime.utcnow():
        return jsonify({"error": "reset token has expired"}), 400

    # Hash new password
    bcrypt = Bcrypt(current_app)
    hashed = bcrypt.generate_password_hash(new_password).decode("utf-8")
    
    # Update password and clear reset token
    user.password = hashed
    user.verification_token = None
    user.token_expiration = None
    db.session.commit()

    return jsonify({"message": "password reset successful"}), 200


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
    # Don't share verification tokens (they're single-use)
    return jsonify({
        "username": user.username,
        "email": user.email,
        "password": user.password,  # Already hashed, safe to sync
        "is_verified": user.is_verified,
        "synced_from": current_app.config.get('APP_NAME', 'Unknown App')
    }), 200


@auth_bp.route("/sentinel/health", methods=["GET"])
def sentinel_health():
    """
    Health check endpoint for Sentinel Systems.
    Other apps use this to verify this app is online and part of the network.
    """
    return jsonify({
        "status": "online",
        "app_name": current_app.config.get('APP_NAME', 'Unknown'),
        "version": "1.0.0",
        "sentinel_system": True
    }), 200
