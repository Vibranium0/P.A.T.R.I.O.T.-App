# patriot/backend/models/saving.py
from datetime import datetime, date
from patriot.backend.database import db


class Saving(db.Model):
    """
    Saving model for tracking savings deposits and withdrawals.
    Works in conjunction with Funds and Goals to track savings progress.
    """

    __tablename__ = "savings"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    account_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id"), nullable=True
    )  # Savings account
    fund_id = db.Column(
        db.Integer, db.ForeignKey("funds.id"), nullable=True
    )  # Associated fund
    goal_id = db.Column(
        db.Integer, db.ForeignKey("goals.id"), nullable=True
    )  # Associated goal
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=True
    )  # Savings category
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_type = db.Column(
        db.String(20), nullable=False
    )  # deposit, withdrawal, interest
    source = db.Column(db.String(100))  # Where the savings came from
    description = db.Column(db.String(255))
    is_recurring = db.Column(db.Boolean, default=False)
    is_automatic = db.Column(
        db.Boolean, default=False
    )  # Auto-transferred from checking
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    household = db.relationship("Household", backref=db.backref("savings", lazy=True))
    created_by = db.relationship(
        "User", backref=db.backref("savings", lazy=True), foreign_keys=[created_by_user_id]
    )
    account = db.relationship(
        "Account", backref=db.backref("savings", lazy=True), foreign_keys=[account_id]
    )
    fund = db.relationship(
        "Fund", backref=db.backref("savings_records", lazy=True), foreign_keys=[fund_id]
    )
    goal = db.relationship(
        "Goal", backref=db.backref("savings_records", lazy=True), foreign_keys=[goal_id]
    )
    category = db.relationship(
        "Category",
        backref=db.backref("savings", lazy=True),
        foreign_keys=[category_id],
    )

    def __repr__(self):
        return f"<Saving {self.transaction_type}: ${self.amount}>"

    def to_dict(self):
        """Convert saving to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "household_id": self.household_id,
            "created_by_user_id": self.created_by_user_id,
            "created_by_name": self.created_by.name if self.created_by else None,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None,
            "fund_id": self.fund_id,
            "fund_name": self.fund.name if self.fund else None,
            "goal_id": self.goal_id,
            "goal_name": self.goal.name if self.goal else None,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "date": self.date.isoformat() if self.date else None,
            "amount": float(self.amount) if self.amount else 0.0,
            "transaction_type": self.transaction_type,
            "source": self.source,
            "description": self.description,
            "is_recurring": self.is_recurring,
            "is_automatic": self.is_automatic,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def get_total_for_period(household_id, start_date, end_date, transaction_type=None):
        """Get total savings for a specific period, optionally filtered by transaction type"""
        query = (
            db.session.query(db.func.sum(Saving.amount))
            .filter_by(household_id=household_id)
            .filter(Saving.date >= start_date, Saving.date <= end_date)
        )

        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)

        result = query.scalar()
        return float(result) if result else 0.0

    @staticmethod
    def get_net_savings(household_id, start_date, end_date):
        """Calculate net savings (deposits - withdrawals) for a period"""
        deposits = Saving.get_total_for_period(
            household_id, start_date, end_date, "deposit"
        )
        withdrawals = Saving.get_total_for_period(
            household_id, start_date, end_date, "withdrawal"
        )
        return deposits - withdrawals

    @staticmethod
    def get_savings_rate(household_id, start_date, end_date):
        """
        Calculate savings rate as percentage of income.
        Requires income data to be available.
        """
        from patriot.backend.models.income import Income

        total_savings = Saving.get_total_for_period(
            household_id, start_date, end_date, "deposit"
        )
        total_income = Income.get_total_for_period(household_id, start_date, end_date)

        if total_income > 0:
            return (total_savings / total_income) * 100
        return 0.0

    @staticmethod
    def get_monthly_average(household_id, months=6):
        """Calculate average monthly savings over the last N months"""
        from dateutil.relativedelta import relativedelta

        end_date = date.today()
        start_date = end_date - relativedelta(months=months)

        total = Saving.get_net_savings(household_id, start_date, end_date)
        return total / months if months > 0 else 0.0

    @staticmethod
    def get_by_goal(household_id, goal_id):
        """Get all savings transactions for a specific goal"""
        return Saving.query.filter_by(
            household_id=household_id, goal_id=goal_id
        ).order_by(Saving.date.desc()).all()

    @staticmethod
    def get_by_fund(household_id, fund_id):
        """Get all savings transactions for a specific fund"""
        return Saving.query.filter_by(
            household_id=household_id, fund_id=fund_id
        ).order_by(Saving.date.desc()).all()
