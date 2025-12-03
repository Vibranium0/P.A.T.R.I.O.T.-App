# backend/utils/auth_helpers.py
"""
Authentication helper functions (non-household-specific)
For household helpers, use shared/utils/household_helpers.py
"""
from flask_jwt_extended import get_jwt_identity


def get_current_user_id():
    """
    Get the current user's ID from JWT identity.
    Use this for tracking who created/owns a resource.
    """
    user_id = get_jwt_identity()
    return int(user_id) if user_id else None
