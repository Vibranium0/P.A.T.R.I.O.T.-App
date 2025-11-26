"""
Account model for financial accounts (checking, savings, credit cards, etc.)
"""
from backend.database import db
from datetime import datetime

class Account(db.Model):
    """Model for financial accounts."""
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Optional: track which partner owns this account
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # checking, savings, credit, investment
    institution = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    last_four = db.Column(db.String(4))  # Last 4 digits of account number
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    household = db.relationship("Household", backref="accounts")
    owner = db.relationship("User", foreign_keys=[owner_user_id], backref="owned_accounts")

    def to_dict(self):
        """Convert account to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "household_id": self.household_id,
            "owner_user_id": self.owner_user_id,
            "owner_name": self.owner.name if self.owner else None,
            "name": self.name,
            "type": self.type,
            "institution": self.institution,
            "balance": float(self.balance),
            "last_four": self.last_four,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Account {self.name} ({self.type}) - {self.institution}>"
