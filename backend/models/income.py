from datetime import date
from backend.database import db


class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Paycheck')  # Paycheck, Bonus, Gift, Other
    description = db.Column(db.Text)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)  # Link to account
    
    # Relationships
    household = db.relationship('Household', backref='incomes')
    account = db.relationship('Account', backref='incomes')
    
    def __repr__(self):
        return f'<Income {self.id}: {self.source} - ${self.amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'household_id': self.household_id,
            'date': self.date.isoformat() if self.date else None,
            'amount': float(self.amount) if self.amount else 0.0,
            'source': self.source,
            'category': self.category,
            'description': self.description,
            'account_id': self.account_id
        }