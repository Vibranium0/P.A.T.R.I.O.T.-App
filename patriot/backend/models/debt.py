# backend/models/debt.py
from datetime import datetime, date
from backend.database import db


class Debt(db.Model):
    __tablename__ = "debts"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    owner_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # Optional: track whose debt this is
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)  # Original debt amount
    current_balance = db.Column(db.Numeric(15, 2), nullable=False)  # Remaining balance
    minimum_payment = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(
        db.Float, default=0.0
    )  # Annual interest rate as percentage
    due_date = db.Column(db.Date, nullable=False)  # Monthly due date
    category = db.Column(
        db.String(100), nullable=False
    )  # Credit Card, Student Loan, Mortgage, etc.
    account_number = db.Column(db.String(50))  # Last 4 digits or masked account number
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    household = db.relationship("Household", backref=db.backref("debts", lazy=True))
    owner = db.relationship("User", foreign_keys=[owner_user_id], backref="owned_debts")

    def __repr__(self):
        return f"<Debt {self.name}: ${self.current_balance} / ${self.total_amount}>"

    def to_dict(self):
        """Convert debt to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "household_id": self.household_id,
            "owner_user_id": self.owner_user_id,
            "owner_name": self.owner.name if self.owner else None,
            "name": self.name,
            "description": self.description,
            "total_amount": float(self.total_amount) if self.total_amount else 0.0,
            "current_balance": (
                float(self.current_balance) if self.current_balance else 0.0
            ),
            "minimum_payment": (
                float(self.minimum_payment) if self.minimum_payment else 0.0
            ),
            "interest_rate": self.interest_rate,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "category": self.category,
            "account_number": self.account_number,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def progress_percentage(self):
        """Calculate payoff progress as percentage"""
        if self.total_amount <= 0:
            return 100.0
        paid_amount = float(self.total_amount) - float(self.current_balance)
        return min((paid_amount / float(self.total_amount)) * 100, 100.0)

    @property
    def remaining_percentage(self):
        """Calculate remaining debt as percentage"""
        return 100.0 - self.progress_percentage

    def make_payment(self, amount):
        """Make a payment towards the debt"""
        if amount > 0 and amount <= self.current_balance:
            self.current_balance -= amount
            return True
        return False

    @property
    def is_paid_off(self):
        """Check if debt is fully paid off"""
        return (
            float(self.current_balance) <= 0.01
        )  # Account for floating point precision

    @staticmethod
    def get_total_debt(household_id):
        """Get total current debt balance for a household"""
        return (
            db.session.query(db.func.sum(Debt.current_balance))
            .filter_by(household_id=household_id, is_active=True)
            .scalar()
            or 0.0
        )

    @staticmethod
    def get_total_minimum_payments(household_id):
        """Get total minimum payments for all active debts"""
        return (
            db.session.query(db.func.sum(Debt.minimum_payment))
            .filter_by(household_id=household_id, is_active=True)
            .scalar()
            or 0.0
        )
