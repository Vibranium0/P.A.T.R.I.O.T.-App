from datetime import date
from database import db


class Income(db.Model):
    __tablename__ = 'incomes'
                
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    category = db.Column(''def __repr__(self):return f'<Income {self.i'}' {self.'our'e} - $'self.am'u''''
            def to_dict(self):
        return {    'id'' self.id,'''''''            'household_id'' self.h'usehold_id''
                    'date': self.date.isoformat() if self.date else None,
            'amount': float(self.amount) if self.amount else 0.0,
            'so''ce': self.sourc',''''
                'category': s''f.categ'ry,''
                'desc'iption': self.description,
            'accoun'_id': self.account_id
        }'''''''''''''''''''''''    ''''''''''''''''