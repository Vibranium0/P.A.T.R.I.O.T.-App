"""
Auth routes for P.A.T.R.I.O.T. backend
Validates JWT tokens from Sentinel Login backend
Integrates with Sentinel Systems for cross-app authentication
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from patriot.backend.config import Config

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/validate", methods=["GET"])
@jwt_required()
def validate():
    """
    Validate JWT token and return user information.
    Expects token in Authorization header: Bearer <token>
    
    Returns:
        {
            "user_id": <user_id>,
            "username": <username>,
            "household_id": <household_id>
        }
    """
    try:
        # Get user ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Extract additional claims from JWT (household_id is added by Sentinel)
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        household_id = claims.get("household_id")
        username = claims.get("username")
        
        return jsonify({
            "user_id": current_user_id,
            "username": username,
            "household_id": household_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Token validation failed", "details": str(e)}), 401


# ============================================================================
# SENTINEL SYSTEMS - Backend Integration Endpoints
# These endpoints allow P.A.T.R.I.O.T. to communicate with Sentinel login
# ============================================================================


@auth_bp.route("/sentinel/health", methods=["GET"])
def sentinel_health():
    """
    Health check endpoint for Sentinel Systems integration.
    Sentinel and other Sentinel apps use this to verify P.A.T.R.I.O.T. 
    backend is online and part of the Sentinel network.
    
    Returns:
        - status: "online" if healthy
        - app_name: Name of this application
        - version: API version
        - sentinel_system: True (indicates this is a Sentinel app)
    """
    return jsonify({
        "status": "online",
        "app_name": current_app.config.get("APP_NAME", "P.A.T.R.I.O.T."),
        "version": "1.0.0",
        "sentinel_system": True,
        "jwt_secret_configured": bool(current_app.config.get("JWT_SECRET_KEY")),
    }), 200


@auth_bp.route("/sentinel/token-info", methods=["POST"])
def sentinel_token_info():
    """
    Endpoint for Sentinel to validate tokens issued by Sentinel.
    Used to verify token authenticity and get user claims.
    
    Request body:
        {
            "token": "<jwt_token>"
        }
    
    Returns:
        - user_id: User ID from token
        - username: Username from token
        - household_id: Household ID from token
        - valid: True if token is valid
    """
    try:
        data = request.get_json() or {}
        token = data.get("token")
        
        if not token:
            return jsonify({"error": "token parameter required"}), 400
        
        from flask_jwt_extended import decode_token
        
        # Decode token using same JWT_SECRET_KEY
        claims = decode_token(token)
        
        return jsonify({
            "valid": True,
            "user_id": claims.get("sub"),  # Subject (user_id)
            "username": claims.get("username"),
            "household_id": claims.get("household_id"),
        }), 200
        
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": "Token validation failed",
            "details": str(e)
        }), 401


@auth_bp.route("/debug/sentinel-status", methods=["GET"])
def debug_sentinel_status():
    """
    Debug endpoint to check Sentinel integration status.
    Shows whether P.A.T.R.I.O.T. can communicate with Sentinel.
    
    SECURITY: Only use in development. Should be disabled in production.
    
    Returns:
        - sentinel_online: True if Sentinel is reachable
        - sentinel_url: URL of configured Sentinel
        - jwt_configured: True if JWT_SECRET_KEY is set
        - p_a_t_r_i_o_t_url: This app's backend URL
        - connection_status: "ready", "incomplete", or "error"
    """
    try:
        from patriot.backend.utils.sentinel_client import get_sentinel_client
        
        client = get_sentinel_client()
        status = client.verify_sentinel_connection()
        
        # Add P.A.T.R.I.O.T. backend URL
        status["p_a_t_r_i_o_t_url"] = current_app.config.get("APP_BACKEND_URL")
        status["patriot_url"] = current_app.config.get("APP_URL")
        
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "error": "Debug check failed",
            "details": str(e),
            "connection_status": "error"
        }), 500
