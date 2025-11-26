# backend/models/bill.py
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from backend.database import db


class Bill(db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    frequency = db.Column(db.String(20), default='monthly')  # monthly, weekly, yearly, etc.
    category = db.Column(db.String(100), nullable=False)
    is_autopay = db.Column(db.Boolean, default=False)
    next_due_date = db.Column(db.Date, nullable=True)  # Automatically calculated next due date
    is_active = db.Column(db.Boolean, default=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)  # Link to account for autopay
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    household = db.relationship('Household', backref=db.backref('bills', lazy=True))
    account = db.relationship('Account', backref=db.backref('bills', lazy=True))

    def __repr__(self):
        return f'<Bill {self.name}: ${self.amount}>'

    def to_dict(self):
        """Convert bill to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'household_id': self.household_id,
            'name': self.name,
            'description': self.description,
            'amount': float(self.amount) if self.amount else 0.0,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'frequency': self.frequency,
            'category': self.category,
            'is_autopay': self.is_autopay,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'is_active': self.is_active,
            'account_id': self.account_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def calculate_next_due_date(self, from_date=None):
        """Calculate the next due date based on frequency"""
        if from_date is None:
            from_date = date.today()
        
        current_due = self.due_date
        
        # If current due date is in the future, return it
        if current_due > from_date:
            return current_due
            
        # Calculate next occurrence based on frequency
        if self.frequency == 'weekly':
            days_to_add = 7
        elif self.frequency == 'biweekly':
            days_to_add = 14
        elif self.frequency == 'monthly':
            # Handle monthly by adding months, preserving day
            from dateutil.relativedelta import relativedelta
            next_date = current_due
            while next_date <= from_date:
                next_date += relativedelta(months=1)
            return next_date
        elif self.frequency == 'quarterly':
            from dateutil.relativedelta import relativedelta
            next_date = current_due
            while next_date <= from_date:
                next_date += relativedelta(months=3)
            return next_date
        elif self.frequency == 'yearly':
            from dateutil.relativedelta import relativedelta
            next_date = current_due
            while next_date <= from_date:
                next_date += relativedelta(years=1)
            return next_date
        else:
            # Default to monthly for unknown frequencies
            from dateutil.relativedelta import relativedelta
            next_date = current_due
            while next_date <= from_date:
                next_date += relativedelta(months=1)
            return next_date
            
        # For weekly/biweekly, calculate using days
        next_date = current_due
        while next_date <= from_date:
            next_date += timedelta(days=days_to_add)
        return next_date

    def update_next_due_date(self):
        """Update the next_due_date field"""
        self.next_due_date = self.calculate_next_due_date()

    def mark_as_paid(self):
        """Mark bill as paid and update next due date"""
        self.update_next_due_date()
        db.session.commit()