# backend/models/transaction.py
from datetime import datetime, date
from backend.database import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Track who created it
    date = db.Column(db.Date, default=date.today)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # Use Numeric for precision
    category = db.Column(db.String(100), nullable=False)
    
    # Optional relationships - transaction can be linked to account, fund, and/or bill
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)  # Source account
    fund_id = db.Column(db.Integer, db.ForeignKey('funds.id'), nullable=True)  # Source fund
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=True)
    
    # For transfers: destination account or fund
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)  # Destination account
    to_fund_id = db.Column(db.Integer, db.ForeignKey('funds.id'), nullable=True)  # Destination fund
    
    # Transaction type for better categorization
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income', 'expense', 'transfer'
    
    # Recurring transaction fields
    is_recurring = db.Column(db.Boolean, default=False)
    frequency = db.Column(db.String(20), nullable=True)  # 'weekly', 'biweekly', 'monthly', 'yearly'
    next_occurrence = db.Column(db.Date, nullable=True)  # Next scheduled occurrence
    parent_transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)  # Links to recurring parent
    is_skipped = db.Column(db.Boolean, default=False)  # Mark instance as skipped
    
    # Additional flags and metadata
    is_autopay = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    household = db.relationship('Household', backref=db.backref('transactions', lazy=True))
    created_by = db.relationship('User', foreign_keys=[created_by_user_id], backref='created_transactions')
    account = db.relationship('Account', foreign_keys=[account_id], backref=db.backref('account_transactions', lazy=True))
    to_account = db.relationship('Account', foreign_keys=[to_account_id], backref=db.backref('received_transactions', lazy=True))
    fund = db.relationship('Fund', foreign_keys=[fund_id], backref=db.backref('fund_transactions', lazy=True))
    to_fund = db.relationship('Fund', foreign_keys=[to_fund_id], backref=db.backref('received_fund_transactions', lazy=True))
    bill = db.relationship('Bill', backref=db.backref('bill_transactions', lazy=True))
    
    # Self-referencing for recurring transaction parent/child relationship
    parent_transaction = db.relationship('Transaction', remote_side=[id], backref='child_transactions')

    def __repr__(self):
        return f'<Transaction {self.id}: {self.description} - ${self.amount}>'

    @property
    def is_income(self):
        """Check if transaction is income"""
        return self.transaction_type == 'income'

    @property
    def is_expense(self):
        """Check if transaction is expense"""
        return self.transaction_type == 'expense'

    @property
    def is_transfer(self):
        """Check if transaction is a transfer"""
        return self.transaction_type == 'transfer'

    def calculate_next_occurrence(self, from_date=None):
        """Calculate the next occurrence date for recurring transaction"""
        if not self.is_recurring or not self.frequency:
            return None
        
        from dateutil.relativedelta import relativedelta
        
        if from_date is None:
            from_date = self.date or date.today()
        
        if self.frequency == 'weekly':
            return from_date + relativedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return from_date + relativedelta(weeks=2)
        elif self.frequency == 'monthly':
            return from_date + relativedelta(months=1)
        elif self.frequency == 'yearly':
            return from_date + relativedelta(years=1)
        
        return None

    def to_dict(self):
        """Convert transaction to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'household_id': self.household_id,
            'created_by_user_id': self.created_by_user_id,
            'created_by_name': self.created_by.name if self.created_by else None,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'amount': float(self.amount) if self.amount else 0.0,
            'category': self.category,
            'account_id': self.account_id,
            'fund_id': self.fund_id,
            'bill_id': self.bill_id,
            'to_account_id': self.to_account_id,
            'to_fund_id': self.to_fund_id,
            'transaction_type': self.transaction_type,
            'is_recurring': self.is_recurring,
            'frequency': self.frequency,
            'next_occurrence': self.next_occurrence.isoformat() if self.next_occurrence else None,
            'parent_transaction_id': self.parent_transaction_id,
            'is_skipped': self.is_skipped,
            'is_autopay': self.is_autopay,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }