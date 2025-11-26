# backend/models/fund.py
from datetime import datetime, date, timedelta
from backend.database import db


class Fund(db.Model):
    __tablename__ = "funds"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    goal = db.Column(db.Float, default=0.0)
    fund_type = db.Column(
        db.String(20), default="Expenses", nullable=False
    )  # Expenses, Savings, Cash
    recurring_amount = db.Column(
        db.Float, nullable=True
    )  # Optional recurring deposit amount
    next_deposit_date = db.Column(db.Date, nullable=True)  # Next scheduled deposit date
    skip_next = db.Column(db.Boolean, default=False)  # Skip next deposit
    account_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id"), nullable=True
    )  # Link to account (null for cash funds)
    description = db.Column(db.String(255), nullable=True)  # Optional description
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    household = db.relationship("Household", backref=db.backref("funds", lazy=True))
    account = db.relationship("Account", backref=db.backref("funds", lazy=True))

    def __repr__(self):
        return f"<Fund {self.name} ({self.fund_type}): ${self.balance}>"

    def to_dict(self):
        """Convert fund to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "household_id": self.household_id,
            "name": self.name,
            "balance": self.balance,
            "goal": self.goal,
            "fund_type": self.fund_type,
            "recurring_amount": self.recurring_amount,
            "next_deposit_date": (
                self.next_deposit_date.isoformat() if self.next_deposit_date else None
            ),
            "skip_next": self.skip_next,
            "account_id": self.account_id,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def progress_percentage(self):
        """Calculate progress towards goal as percentage"""
        if self.goal <= 0:
            return 0.0
        return min((self.balance / self.goal) * 100, 100.0)

    @property
    def amount_to_goal(self):
        """Calculate remaining amount needed to reach goal"""
        return max(self.goal - self.balance, 0.0)

    def add_funds(self, amount):
        """Add funds to the balance"""
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw_funds(self, amount):
        """Withdraw funds from the balance if sufficient funds available"""
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def is_due_for_deposit(self):
        """Check if fund is due for recurring deposit"""
        if not self.recurring_amount or self.skip_next:
            return False
        if not self.next_deposit_date:
            return True  # If no date set, assume due
        return date.today() >= self.next_deposit_date

    def process_recurring_deposit(self):
        """Process recurring deposit and update next deposit date"""
        if not self.is_due_for_deposit():
            return False

        if self.skip_next:
            # Reset skip flag and update next deposit date
            self.skip_next = False
            self.next_deposit_date = date.today() + timedelta(days=14)
            return False

        # Add recurring amount to balance
        self.balance += self.recurring_amount
        # Set next deposit date to 14 days from now (biweekly)
        self.next_deposit_date = date.today() + timedelta(days=14)
        return True

    @staticmethod
    def get_total_by_type(household_id, fund_type):
        """Get total balance for all funds of a specific type for a household"""
        return (
            db.session.query(db.func.sum(Fund.balance))
            .filter_by(household_id=household_id, fund_type=fund_type)
            .scalar()
            or 0.0
        )

    @staticmethod
    def get_total_recurring_amount(household_id):
        """Get total recurring amount across all funds for a household"""
        return (
            db.session.query(db.func.sum(Fund.recurring_amount))
            .filter(
                Fund.household_id == household_id,
                Fund.recurring_amount.isnot(None),
                Fund.skip_next == False,
            )
            .scalar()
            or 0.0
        )
