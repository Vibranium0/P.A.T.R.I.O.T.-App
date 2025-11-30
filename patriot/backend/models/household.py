# backend/models/household.py
from datetime import datetime
from backend.database import db


# Association table for many-to-many relationship between users and households
user_household = db.Table('user_household',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('household_id', db.Integer, db.ForeignKey('households.id'), primary_key=True),
    db.Column('role', db.String(20), default='member'),  # 'owner' or 'member'
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class Household(db.Model):
    __tablename__ = "households"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    members = db.relationship(
        'User',
        secondary=user_household,
        backref=db.backref('households', lazy='dynamic')
    )
    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Household {self.name}>'

    def to_dict(self, include_members=True):
        """Convert household to dictionary for JSON serialization"""
        result = {
            'id': self.id,
            'name': self.name,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_members:
            # Get member details with roles
            result['members'] = []
            for member in self.members:
                # Query the association table for role
                role_query = db.session.execute(
                    db.select(user_household.c.role, user_household.c.joined_at)
                    .where(
                        db.and_(
                            user_household.c.user_id == member.id,
                            user_household.c.household_id == self.id
                        )
                    )
                ).first()
                
                result['members'].append({
                    'id': member.id,
                    'username': member.username,
                    'email': member.email,
                    'name': member.name,
                    'role': role_query[0] if role_query else 'member',
                    'joined_at': role_query[1].isoformat() if role_query and role_query[1] else None
                })
        
        return result

    def add_member(self, user, role='member'):
        """Add a user to the household"""
        if user not in self.members:
            # Insert into association table with role
            db.session.execute(
                user_household.insert().values(
                    user_id=user.id,
                    household_id=self.id,
                    role=role,
                    joined_at=datetime.utcnow()
                )
            )
            return True
        return False

    def remove_member(self, user):
        """Remove a user from the household"""
        if user in self.members:
            db.session.execute(
                user_household.delete().where(
                    db.and_(
                        user_household.c.user_id == user.id,
                        user_household.c.household_id == self.id
                    )
                )
            )
            return True
        return False

    def is_owner(self, user):
        """Check if user is the household owner"""
        role_query = db.session.execute(
            db.select(user_household.c.role)
            .where(
                db.and_(
                    user_household.c.user_id == user.id,
                    user_household.c.household_id == self.id
                )
            )
        ).first()
        
        return role_query and role_query[0] == 'owner'


class HouseholdInvite(db.Model):
    __tablename__ = "household_invites"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    # Relationships
    household = db.relationship('Household', backref=db.backref('invites', lazy=True))
    inviter = db.relationship('User', foreign_keys=[inviter_id])

    def __repr__(self):
        return f'<HouseholdInvite to {self.invitee_email} for household {self.household_id}>'

    def to_dict(self):
        """Convert invite to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'household_id': self.household_id,
            'household_name': self.household.name if self.household else None,
            'inviter_id': self.inviter_id,
            'inviter_name': self.inviter.name if self.inviter else None,
            'invitee_email': self.invitee_email,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

    def is_expired(self):
        """Check if invite has expired"""
        return datetime.utcnow() > self.expires_at
