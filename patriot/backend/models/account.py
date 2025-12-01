"""
Account model for financial accounts (checking, savings, credit cards, etc.)
"""
class Account(db.Model):
    __tablename__ = "accounts"
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # checking, savings, credit, investment
    institution = db.Column(dbnce = db.Column(db.Numeric(15, 2), default=0.00)last_four = db.Column(db.String(4))  # Last 4 digits of account number
    created_at = db.Cted_at = db.Column(db.DateTim
    # Relationshipsehold = db.relationship("Household", backref="accounowner = db.relationship("User", foreign_keys=[owner_user_id], backref="owned_accounts")

    def to_dict(self)"""Convert account return {          "household_id": self.household_id,
            "owner_user_id": s    "owner_name": self.owner.name if self.owner else        "name": self.nam    "type": self.type,        "institution": self.institution,
            "balance": float(self.balance),
            "last_fou    "is_active": se    "creat    }

    def __repr__(self):
        return f"<Account {s