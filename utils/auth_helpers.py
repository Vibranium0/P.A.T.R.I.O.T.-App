# backend/utils/auth_helpers.py
"""
Authentication and authorization helper functions for household-based access control
"""
from flask_jwt_extended import get_jwt, get_jwt_identity
from backend.models import User


def get_current_household_id():
    """
    Get the current user's household_id from JWT claims.
    This is the primary way to filter resources by household.
    """
    claims = get_jwt()
    return claims.get('household_id')


def get_current_user_id():
    """
    Get the current user's ID from JWT identity.
    Use this for tracking who created/owns a resource.
    """
    user_id = get_jwt_identity()
    return int(user_id) if user_id else None


def get_user_household(user_id):
    """
    Get a user's default household ID from database.
    Fallback when household_id is not in JWT claims.
    """
    user = User.query.get(user_id)
    if not user:
        return None
    return user.default_household_id


def require_household_access(household_id):
    """
    Check if current user has access to the specified household.
    Returns True if user is a member, False otherwise.
    """
    current_household = get_current_household_id()
    if not current_household:
        # Fallback: check user's default household
        user_id = get_current_user_id()
        current_household = get_user_household(user_id)
    
    return current_household == household_id
