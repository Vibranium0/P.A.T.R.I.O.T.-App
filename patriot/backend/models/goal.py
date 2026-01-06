# patriot/backend/models/goal.py
from datetime import datetime, date
from patriot.backend.database import db


class Goal(db.Model):
    """
    Goal model for tracking financial objectives and progress.
    Can be linked to funds or savings accounts.
    """

    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    target_amount = db.Column(db.Numeric(15, 2), nullable=False)
    current_amount = db.Column(db.Numeric(15, 2), default=0.00)
    target_date = db.Column(db.Date, nullable=True)  # Optional deadline
    start_date = db.Column(db.Date, default=date.today)
    category = db.Column(
        db.String(50)
    )  # emergency_fund, vacation, house, car, education, etc.
    priority = db.Column(
        db.String(20), default="medium"
    )  # low, medium, high, critical
    fund_id = db.Column(
        db.Integer, db.ForeignKey("funds.id"), nullable=True
    )  # Link to associated fund
    account_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id"), nullable=True
    )  # Link to dedicated account
    is_active = db.Column(db.Boolean, default=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    icon = db.Column(db.String(50))  # Icon name or emoji
    color = db.Column(db.String(20))  # Hex color code for UI
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    household = db.relationship("Household", backref=db.backref("goals", lazy=True))
    created_by = db.relationship(
        "User", backref=db.backref("goals", lazy=True), foreign_keys=[created_by_user_id]
    )
    fund = db.relationship(
        "Fund", backref=db.backref("goals", lazy=True), foreign_keys=[fund_id]
    )
    account = db.relationship(
        "Account", backref=db.backref("goals", lazy=True), foreign_keys=[account_id]
    )

    def __repr__(self):
        return f"<Goal {self.name}: ${self.current_amount}/${self.target_amount}>"

    def to_dict(self):
        """Convert goal to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "household_id": self.household_id,
            "created_by_user_id": self.created_by_user_id,
            "created_by_name": self.created_by.name if self.created_by else None,
            "name": self.name,
            "description": self.description,
            "target_amount": float(self.target_amount) if self.target_amount else 0.0,
            "current_amount": float(self.current_amount) if self.current_amount else 0.0,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "category": self.category,
            "priority": self.priority,
            "fund_id": self.fund_id,
            "fund_name": self.fund.name if self.fund else None,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "icon": self.icon,
            "color": self.color,
            "notes": self.notes,
            "progress_percentage": self.progress_percentage,
            "amount_remaining": self.amount_remaining,
            "days_remaining": self.days_remaining,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def progress_percentage(self):
        """Calculate progress towards goal as percentage"""
        if not self.target_amount or self.target_amount <= 0:
            return 0.0
        return min(
            (float(self.current_amount) / float(self.target_amount)) * 100, 100.0
        )

    @property
    def amount_remaining(self):
        """Calculate remaining amount needed to reach goal"""
        return max(float(self.target_amount) - float(self.current_amount), 0.0)

    @property
    def days_remaining(self):
        """Calculate days remaining until target date"""
        if not self.target_date:
            return None
        delta = self.target_date - date.today()
        return max(delta.days, 0)

    @property
    def days_elapsed(self):
        """Calculate days since goal started"""
        delta = date.today() - self.start_date
        return delta.days

    @property
    def recommended_monthly_contribution(self):
        """Calculate recommended monthly contribution to reach goal by target date"""
        if not self.target_date or self.is_completed:
            return 0.0

        remaining = self.amount_remaining
        months_remaining = max(self.days_remaining / 30, 1) if self.days_remaining else 1

        return remaining / months_remaining

    def add_contribution(self, amount):
        """Add a contribution to the goal"""
        if amount > 0:
            self.current_amount = float(self.current_amount) + amount

            # Check if goal is now completed
            if self.current_amount >= self.target_amount:
                self.is_completed = True
                self.completed_at = datetime.utcnow()

            return True
        return False

    def withdraw(self, amount):
        """Withdraw from goal (if needed)"""
        if amount > 0 and self.current_amount >= amount:
            self.current_amount = float(self.current_amount) - amount

            # Unmark as completed if we're below target again
            if self.current_amount < self.target_amount:
                self.is_completed = False
                self.completed_at = None

            return True
        return False

    @staticmethod
    def get_active_goals(household_id):
        """Get all active goals for a household"""
        return Goal.query.filter_by(
            household_id=household_id, is_active=True, is_completed=False
        ).all()

    @staticmethod
    def get_completed_goals(household_id):
        """Get all completed goals for a household"""
        return Goal.query.filter_by(
            household_id=household_id, is_completed=True
        ).all()
