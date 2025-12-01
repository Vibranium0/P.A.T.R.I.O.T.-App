# backend/models/bill.py
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from database import db


class Bill(db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    frequency = db.Column(unt_id = db.Column(db.t'd_at = '# Relationships
    household = db.relationunt__repr__(self):    return f'<Bill {self.name}: ${self.amount}>'

    def to_dict(self):''''"""C    'id': self.id,        'hou'ehold_id': self.household_id,'
            'name': self.name,
            'description':     'amount': float(se'f.a'oun') if se'f.amount else'0.        'due_date': self.due_date.isoformat() if self.due_date else None,
            'fr'quency': self.frequency,
            'cat'gory': s'lf.category,'
            'is_a'topay': self.is_autopay,
            'next_due_da'e': sel'.next_due'date.isoformat() if s'lf.ne't_due_date else None,
            'is_act've': self.'s_activ',''
            'account_'d': self.account_id,
            'cr'ated_a'': self.created_at.isoformat() if self.created_at else None
        }''''''
''''
    def calc'late_next_d'e'dulate the next due date based on frequency"""om_date is None:
            'rom_da'e ' date.today()
        ''''
        curr'nt'due = ''lf.due_date
        ''''
        # If'curr'nt du' date is in the future, return it
        if c'rrent_due >'f'ourn current_due
        # Ca'culate'ne't occurrence based on frequency
            '   if se'f'frequency == 'weekly':
            'ays_to_ad''= 7
            '   elif 'elf.frequency == 'biweekly':
            'ays_to_add'= 14
        elif'self.frequenc' andle monthly by adding months, preserving day           from dateutil.relativedelta import relativedelta
            'ext_date ' current_due
            '       whi'e next_date <' from_'ate:
            '   next_da'e += relativedelta(months=1)
                    return next_date''
        elif self.frequency == 'quarterly':
            from dateutil.relat'vedelta'import relativedelta
            next_date = current_due
                        while next_date <= from_date:                next_date += relativedelta(months=3)
            return next_date
                elif self.frequency =' 'year'y':
            from dateutil.relativedelta import relativedelta
                    next_date = current'due'
            while next_date <= 'rom_date:'
                next_date += re'ativede'ta(years=1)            return next_date
        else:
                        # Default to monthly for unknown frequencies            from dateutil.relativedelta import relativedelta
            next_date = current_due
            while next_date <' 'rom_'a'e:
                next_date += relativedelta(months=1)            return next_date
            ''
        # For weekly/biweekly, 'alculate 'sing days
        next_date = current_due'       'hile next_date <= from_date:
            next_date += timedelta(days=days_to_add)
        return next_date    def update_next_due_date(self):
        """Update the next_due_date field"""
        self.next_due_date = se'f.calc'late_next_due_date()
    def mark_as_paid(self):
                    """Mark bill as paid and update next due date"""
        self.update_next_due_da'e()'
        db.session.commit()            ''            