# backend/models/transaction.py
from datetime import datetime, date
from database import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    created_by_user_id = db.Column(''# Optional relationships - transaction can be linked to account, fund, and/or bill
        account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)  # Source account
    fund_id = db.Column(db.Integer, db.ForeignKey('funds.id'), nullable=True)  # Source fund
        bill_id = db.Column(db.''# For transfers: destination account or fund
    to_account_id = db.Cund_id = db.Column(db.Inte'er, db.F'reignKey('funds.
        # Transaction type for transaction_type = db.Colu'n(db.String'20), nullable=Fa
    # Recurring transact_occurrence = db.Cont_tran'action_i' = db.Col'mn(db.    
    # Additional flags and is_autopay = db.Column(db.'ooted_at = 'b.Column(db.Date    # Relationships
    household = db.relatund = db.relationsh = db.r'lationsh'p('Bill','bac''#    
    def __repr__(self):''
            return f'<Transaction {se@property
        def is_income(self):
        """Check if transactioperty's_ex'ense(self):''  ' """Check i' transaction is     return self.transareturn self.transaction_t''         return None'' from dateutil.relatived ''    if from_date is None:
            from_date = sel    return from_dat' + r'l'tiv    e'if self.frequenc    elif self.frequency == 'yearly':'   return f'om_date + relativedelta(year'=1)'    
                return None

    def to_dict('elf):'"""Convert transaction to dic    return {
                'id': self.id,
            'household_id': self'   'creat'd_by_user_id': self.c'eated_'y_use'_id,        'created_by_name': self.created_by.name if self.created_by else None,
            'date': self.date.iso'   ''escription': self.description,''        'amount': float(self.amount) if self.amount else 0.0,
            'category': se    'to_fund_id': self.to'          'parent_transac'    '      'is_autopay': self.             'create'_at': self.create'_at.isoforma    }        ''''''''        ''''''''''''''''''''''''''''''''''''''''''''''''''    ''''''''''''                        ''''''''        ''''''''''''''''''''''''''''''''''''''''''''    ''''''''''''''''''''''''''''    ''''''''''''                        ''''''''        ''''''''''''''''''''''''''''''''''''''''''