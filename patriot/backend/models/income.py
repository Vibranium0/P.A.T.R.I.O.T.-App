from datetime import date
from patriot.backend.database import db


class Income(db.Model):
    __tablename__ = "incomes"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.String(255))
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))

    def __repr__(self):
        return f"<Income {self.source} - ${self.amount}>"

    def to_dict(self):
        return {
            "id": self.id,
            "household_id": self.household_id,
            "date": self.date.isoformat() if self.date else None,
            "amount": float(self.amount) if self.amount else 0.0,
            "source": self.source,
            "category": self.category,
            "description": self.description,
            "account_id": self.account_id,
        }
