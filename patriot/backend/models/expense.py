# patriot/backend/models/expense.py
from datetime import datetime, date
from patriot.backend.database import db


class Expense(db.Model):
    """
    Expense model for tracking all household expenditures.
    Can be linked to accounts, categories, and bills.
    """

    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    bill_id = db.Column(
        db.Integer, db.ForeignKey("bills.id"), nullable=True
    )  # Link to recurring bill if applicable
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    merchant = db.Column(db.String(100))  # Store or vendor name
    payment_method = db.Column(
        db.String(50)
    )  # cash, credit, debit, check, electronic transfer
    is_recurring = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(255))  # Comma-separated tags for flexible categorization
    receipt_url = db.Column(db.String(500))  # Link to receipt image/document
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    household = db.relationship("Household", backref=db.backref("expenses", lazy=True))
    created_by = db.relationship(
        "User", backref=db.backref("expenses", lazy=True), foreign_keys=[created_by_user_id]
    )
    account = db.relationship(
        "Account", backref=db.backref("expenses", lazy=True), foreign_keys=[account_id]
    )
    category = db.relationship(
        "Category",
        backref=db.backref("expenses", lazy=True),
        foreign_keys=[category_id],
    )
    bill = db.relationship(
        "Bill", backref=db.backref("expenses", lazy=True), foreign_keys=[bill_id]
    )

    def __repr__(self):
        return f"<Expense {self.description}: ${self.amount}>"

    def to_dict(self):
        """Convert expense to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "household_id": self.household_id,
            "created_by_user_id": self.created_by_user_id,
            "created_by_name": self.created_by.name if self.created_by else None,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "bill_id": self.bill_id,
            "bill_name": self.bill.name if self.bill else None,
            "date": self.date.isoformat() if self.date else None,
            "amount": float(self.amount) if self.amount else 0.0,
            "description": self.description,
            "merchant": self.merchant,
            "payment_method": self.payment_method,
            "is_recurring": self.is_recurring,
            "tags": self.tags.split(",") if self.tags else [],
            "receipt_url": self.receipt_url,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def get_total_by_category(household_id, start_date=None, end_date=None):
        """Get total expenses grouped by category for a date range"""
        query = db.session.query(
            db.func.sum(Expense.amount).label("total"), Expense.category_id
        ).filter_by(household_id=household_id)

        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        return query.group_by(Expense.category_id).all()

    @staticmethod
    def get_total_for_period(household_id, start_date, end_date):
        """Get total expenses for a specific period"""
        result = (
            db.session.query(db.func.sum(Expense.amount))
            .filter_by(household_id=household_id)
            .filter(Expense.date >= start_date, Expense.date <= end_date)
            .scalar()
        )
        return float(result) if result else 0.0

    @staticmethod
    def get_monthly_average(household_id, months=6):
        """Calculate average monthly expenses over the last N months"""
        from dateutil.relativedelta import relativedelta

        end_date = date.today()
        start_date = end_date - relativedelta(months=months)

        total = Expense.get_total_for_period(household_id, start_date, end_date)
        return total / months if months > 0 else 0.0
