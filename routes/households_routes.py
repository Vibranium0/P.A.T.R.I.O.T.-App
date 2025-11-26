# backend/routes/households_routes.py
"""
Household Management Routes
Handles creating households, inviting members, and managing household memberships.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import db
from backend.models import User, Household, HouseholdInvite, user_household
from datetime import datetime, timedelta
import secrets
import string

households_bp = Blueprint('households', __name__, url_prefix='/api/households')


def generate_invite_token():
    """Generate a secure random token for household invites"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))


def get_user_household(user_id):
    """Get the user's default household ID"""
    user = User.query.get(user_id)
    if not user:
        return None
    return user.default_household_id


@households_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_households():
    """Get all households the current user belongs to"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get all households user belongs to
        households = user.households.all()
        
        return jsonify({
            "households": [h.to_dict(include_members=True) for h in households],
            "default_household_id": user.default_household_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@households_bp.route('/<int:household_id>', methods=['GET'])
@jwt_required()
def get_household(household_id):
    """Get details of a specific household"""
    try:
        current_user_id = get_jwt_identity()
        household = Household.query.get(household_id)
        
        if not household:
            return jsonify({"error": "Household not found"}), 404
        
        # Check if user is a member
        user = User.query.get(current_user_id)
        if user not in household.members:
            return jsonify({"error": "Access denied - you are not a member of this household"}), 403
        
        return jsonify(household.to_dict(include_members=True)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@households_bp.route('/', methods=['POST'])
@jwt_required()
def create_household():
    """Create a new household (for creating shared budgets)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        name = data.get('name')
        if not name:
            return jsonify({"error": "Household name is required"}), 400
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Create new household
        household = Household(
            name=name,
            created_by=current_user_id,
            created_at=datetime.utcnow()
        )
        db.session.add(household)
        db.session.flush()  # Get the household ID
        
        # Add creator as owner
        db.session.execute(
            user_household.insert().values(
                user_id=current_user_id,
                household_id=household.id,
                role='owner',
                joined_at=datetime.utcnow()
            )
        )
        
        # Set as default household if user doesn't have one
        if not user.default_household_id:
            user.default_household_id = household.id
        
        db.session.commit()
        
        return jsonify({
            "message": "Household created successfully",
            "household": household.to_dict(include_members=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@households_bp.route('/<int:household_id>', methods=['PUT'])
@jwt_required()
def update_household(household_id):
    """Update household details (owner only)"""
    try:
        current_user_id = get_jwt_identity()
        household = Household.query.get(household_id)
        
        if not household:
            return jsonify({"error": "Household not found"}), 404
        
        user = User.query.get(current_user_id)
        if not household.is_owner(user):
            return jsonify({"error": "Only the household owner can update details"}), 403
        
        data = request.get_json()
        if 'name' in data:
            household.name = data['name']
        
        db.session.commit()
        
        return jsonify({
            "message": "Household updated successfully",
            "household": household.to_dict(include_members=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@households_bp.route('/<int:household_id>/invite', methods=['POST'])
@jwt_required()
def invite_member(household_id):
    """Invite someone to join the household (mission/operation)"""
    try:
        current_user_id = get_jwt_identity()
        household = Household.query.get(household_id)
        
        if not household:
            return jsonify({"error": "Household not found"}), 404
        
        # Check if user is a member (any member can invite)
        user = User.query.get(current_user_id)
        if user not in household.members:
            return jsonify({"error": "Only household members can send invites"}), 403
        
        data = request.get_json()
        invitee_email = data.get('email')
        
        if not invitee_email:
            return jsonify({"error": "Email is required"}), 400
        
        # Check if user is already a member
        existing_member = User.query.filter_by(email=invitee_email).first()
        if existing_member and existing_member in household.members:
            return jsonify({"error": "This user is already a household member"}), 400
        
        # Check for pending invite
        existing_invite = HouseholdInvite.query.filter_by(
            household_id=household_id,
            invitee_email=invitee_email,
            status='pending'
        ).first()
        
        if existing_invite and not existing_invite.is_expired():
            return jsonify({"error": "An active invite already exists for this email"}), 400
        
        # Create invite
        invite = HouseholdInvite(
            household_id=household_id,
            inviter_id=current_user_id,
            invitee_email=invitee_email,
            token=generate_invite_token(),
            status='pending',
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(invite)
        db.session.commit()
        
        # TODO: Send email with invite link
        # For now, return the token so it can be shared manually
        invite_url = f"/join-household/{invite.token}"
        
        return jsonify({
            "message": "Invitation sent successfully",
            "invite": invite.to_dict(),
            "invite_url": invite_url,
            "note": "Share this link with your partner to join the operation"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@households_bp.route('/invites/<token>', methods=['GET'])
@jwt_required()
def get_invite_details(token):
    """Get details of an invite (to show who's inviting and to which household)"""
    try:
        invite = HouseholdInvite.query.filter_by(token=token).first()
        
        if not invite:
            return jsonify({"error": "Invite not found"}), 404
        
        if invite.status != 'pending':
            return jsonify({"error": f"This invite has already been {invite.status}"}), 400
        
        if invite.is_expired():
            invite.status = 'expired'
            db.session.commit()
            return jsonify({"error": "This invite has expired"}), 400
        
        return jsonify(invite.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@households_bp.route('/invites/<token>/accept', methods=['POST'])
@jwt_required()
def accept_invite(token):
    """Accept an invitation to join a household"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        invite = HouseholdInvite.query.filter_by(token=token).first()
        
        if not invite:
            return jsonify({"error": "Invite not found"}), 404
        
        # Verify email matches
        if user.email != invite.invitee_email:
            return jsonify({"error": "This invite was sent to a different email address"}), 403
        
        if invite.status != 'pending':
            return jsonify({"error": f"This invite has already been {invite.status}"}), 400
        
        if invite.is_expired():
            invite.status = 'expired'
            db.session.commit()
            return jsonify({"error": "This invite has expired"}), 400
        
        household = Household.query.get(invite.household_id)
        if not household:
            return jsonify({"error": "Household not found"}), 404
        
        # Add user to household
        db.session.execute(
            user_household.insert().values(
                user_id=current_user_id,
                household_id=household.id,
                role='member',
                joined_at=datetime.utcnow()
            )
        )
        
        # Set as default household if user doesn't have one
        if not user.default_household_id:
            user.default_household_id = household.id
        
        # Mark invite as accepted
        invite.status = 'accepted'
        
        db.session.commit()
        
        return jsonify({
            "message": "Welcome to the operation! You've successfully joined the household.",
            "household": household.to_dict(include_members=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@households_bp.route('/invites/<token>/reject', methods=['POST'])
@jwt_required()
def reject_invite(token):
    """Reject an invitation"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        invite = HouseholdInvite.query.filter_by(token=token).first()
        
        if not invite:
            return jsonify({"error": "Invite not found"}), 404
        
        if user.email != invite.invitee_email:
            return jsonify({"error": "This invite was sent to a different email address"}), 403
        
        if invite.status != 'pending':
            return jsonify({"error": f"This invite has already been {invite.status}"}), 400
        
        invite.status = 'rejected'
        db.session.commit()
        
        return jsonify({"message": "Invitation rejected"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@households_bp.route('/<int:household_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_member(household_id, user_id):
    """Remove a member from the household (owner only)"""
    try:
        current_user_id = get_jwt_identity()
        household = Household.query.get(household_id)
        
        if not household:
            return jsonify({"error": "Household not found"}), 404
        
        current_user = User.query.get(current_user_id)
        if not household.is_owner(current_user):
            return jsonify({"error": "Only the household owner can remove members"}), 403
        
        user_to_remove = User.query.get(user_id)
        if not user_to_remove:
            return jsonify({"error": "User not found"}), 404
        
        if user_to_remove not in household.members:
            return jsonify({"error": "User is not a member of this household"}), 400
        
        if user_id == current_user_id:
            return jsonify({"error": "Owner cannot remove themselves. Transfer ownership or delete household instead."}), 400
        
        # Remove from household
        household.remove_member(user_to_remove)
        
        # If this was their default household, clear it
        if user_to_remove.default_household_id == household_id:
            user_to_remove.default_household_id = None
        
        db.session.commit()
        
        return jsonify({"message": "Member removed successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@households_bp.route('/<int:household_id>/leave', methods=['POST'])
@jwt_required()
def leave_household(household_id):
    """Leave a household (members only, not owner)"""
    try:
        current_user_id = get_jwt_identity()
        household = Household.query.get(household_id)
        
        if not household:
            return jsonify({"error": "Household not found"}), 404
        
        user = User.query.get(current_user_id)
        if user not in household.members:
            return jsonify({"error": "You are not a member of this household"}), 400
        
        if household.is_owner(user):
            return jsonify({"error": "Owner cannot leave household. Transfer ownership or delete household instead."}), 400
        
        # Remove from household
        household.remove_member(user)
        
        # If this was their default household, clear it
        if user.default_household_id == household_id:
            user.default_household_id = None
        
        db.session.commit()
        
        return jsonify({"message": "You have left the household"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@households_bp.route('/<int:household_id>/switch', methods=['POST'])
@jwt_required()
def switch_default_household(household_id):
    """Switch to a different household as the default"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        household = Household.query.get(household_id)
        if not household:
            return jsonify({"error": "Household not found"}), 404
        
        if user not in household.members:
            return jsonify({"error": "You are not a member of this household"}), 403
        
        user.default_household_id = household_id
        db.session.commit()
        
        return jsonify({
            "message": "Default household switched successfully",
            "household": household.to_dict(include_members=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@households_bp.route('/<int:household_id>', methods=['DELETE'])
@jwt_required()
def delete_household(household_id):
    """Delete a household (owner only) - WARNING: deletes all associated data"""
    try:
        current_user_id = get_jwt_identity()
        household = Household.query.get(household_id)
        
        if not household:
            return jsonify({"error": "Household not found"}), 404
        
        user = User.query.get(current_user_id)
        if not household.is_owner(user):
            return jsonify({"error": "Only the household owner can delete the household"}), 403
        
        # TODO: This will cascade delete all funds, bills, accounts, transactions, etc.
        # Consider adding a confirmation step or soft delete
        db.session.delete(household)
        db.session.commit()
        
        return jsonify({"message": "Household deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
