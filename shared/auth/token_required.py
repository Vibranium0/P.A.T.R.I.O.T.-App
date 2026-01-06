"""
JWT Authentication Middleware for P.A.T.R.I.O.T. and Sentinel Apps

This module provides proper JWT validation using Flask-JWT-Extended.
Use @require_token decorator instead of manually checking tokens.
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtended

# Alias for backwards compatibility and clarity
# New code should use: @jwt_required()
require_token = jwt_required


def get_current_user_id():
    """
    Get the current user ID from JWT token.
    Must be called within a route protected by @jwt_required() or @require_token
    """
    user_id = get_jwt_identity()
    return int(user_id) if user_id else None


def get_user_claims():
    """
    Get all JWT claims for current request.
    Includes user_id, username, household_id, etc.
    Must be called within a route protected by @jwt_required() or @require_token
    """
    return get_jwt()


def verify_token():
    """
    Manually verify JWT token in request.
    Useful if you need to verify token outside of a route decorator.
    
    Returns:
        (user_id, claims) on success
        None on failure
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        claims = get_jwt()
        return (int(user_id) if user_id else None, claims)
    except JWTExtended:
        return None
