# patriot/backend/models/transaction.py
from datetime import datetime
from patriot.backend.database import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    fund_id = db.Column(db.Integer, db.ForeignKey("funds.id"), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    to_fund_id = db.Column(db.Integer, db.ForeignKey("funds.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    transaction_type = db.Column(
        db.String(20), nullable=False
    )  # e.g. 'expense', 'income', 'transfer'
    is_autopay = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    household = db.relationship("Household", backref="transactions")
    created_by = db.relationship(
        "User", backref="transactions", foreign_keys=[created_by_user_id]
    )
    account = db.relationship("Account", foreign_keys=[account_id])
    fund = db.relationship("Fund", foreign_keys=[fund_id])
    bill = db.relationship("Bill", foreign_keys=[bill_id])
    to_account = db.relationship("Account", foreign_keys=[to_account_id])
    to_fund = db.relationship("Fund", foreign_keys=[to_fund_id])

    def __repr__(self):
        return f"<Transaction {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "household_id": self.household_id,
            "created_by_user_id": self.created_by_user_id,
            "account_id": self.account_id,
            "fund_id": self.fund_id,
            "bill_id": self.bill_id,
            "to_account_id": self.to_account_id,
            "to_fund_id": self.to_fund_id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "transaction_type": self.transaction_type,
            "is_autopay": self.is_autopay,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
