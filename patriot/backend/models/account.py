from patriot.backend.database import db

"""
Account model for financial accounts (checking, savings, credit cards, etc.)
"""


class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(
        db.String(50), nullable=False
    )  # checking, savings, credit, investment
    institution = db.Column(db.String(100))
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    last_four = db.Column(db.String(4))  # Last 4 digits of account number
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    household = db.relationship("Household", backref="accounts")
    owner = db.relationship(
        "User", foreign_keys=[owner_user_id], backref="owned_accounts"
    )

    def to_dict(self):
        """Convert account to dictionary"""
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
            "created_at": str(self.created_at),
        }

    def __repr__(self):
        return f"<Account {self.id} {self.name}>"
