# backend/models/user.py
from datetime import datetime
from backend.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120))
    theme = db.Column(db.String(50), default="light")
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    token_expiration = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Default household - automatically created for single users
    default_household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=True)

    # Relationships
    default_household = db.relationship('Household', foreign_keys=[default_household_id], backref='default_for_users')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self, include_households=False):
        """Convert user to dictionary for JSON serialization"""
        result = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'theme': self.theme,
            'is_verified': self.is_verified,
            'default_household_id': self.default_household_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_households:
            result['households'] = [
                {
                    'id': h.id,
                    'name': h.name,
                    'is_default': h.id == self.default_household_id
                }
                for h in self.households
            ]
        
        return result