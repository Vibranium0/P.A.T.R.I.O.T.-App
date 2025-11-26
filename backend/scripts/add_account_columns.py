#!/usr/bin/env python3
"""
Add account_id and transfer columns to transactions and bills tables
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database import db

def add_columns():
    """Add account_id and transfer columns using raw SQL"""
    app = create_app()
    
    with app.app_context():
        try:
            # Add account_id to transactions table
            print("Adding account_id to transactions table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE transactions ADD COLUMN account_id INTEGER REFERENCES accounts(id)"
                ))
                print("✓ Added account_id to transactions")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ account_id already exists in transactions")
                else:
                    raise
            
            # Add to_account_id to transactions table
            print("Adding to_account_id to transactions table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE transactions ADD COLUMN to_account_id INTEGER REFERENCES accounts(id)"
                ))
                print("✓ Added to_account_id to transactions")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ to_account_id already exists in transactions")
                else:
                    raise
            
            # Add to_fund_id to transactions table
            print("Adding to_fund_id to transactions table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE transactions ADD COLUMN to_fund_id INTEGER REFERENCES funds(id)"
                ))
                print("✓ Added to_fund_id to transactions")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ to_fund_id already exists in transactions")
                else:
                    raise
            
            # Add recurring transaction fields
            print("Adding is_recurring to transactions table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE transactions ADD COLUMN is_recurring BOOLEAN DEFAULT 0"
                ))
                print("✓ Added is_recurring to transactions")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ is_recurring already exists in transactions")
                else:
                    raise
            
            print("Adding frequency to transactions table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE transactions ADD COLUMN frequency VARCHAR(20)"
                ))
                print("✓ Added frequency to transactions")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ frequency already exists in transactions")
                else:
                    raise
            
            print("Adding next_occurrence to transactions table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE transactions ADD COLUMN next_occurrence DATE"
                ))
                print("✓ Added next_occurrence to transactions")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ next_occurrence already exists in transactions")
                else:
                    raise
            
            print("Adding parent_transaction_id to transactions table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE transactions ADD COLUMN parent_transaction_id INTEGER REFERENCES transactions(id)"
                ))
                print("✓ Added parent_transaction_id to transactions")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ parent_transaction_id already exists in transactions")
                else:
                    raise
            
            print("Adding is_skipped to transactions table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE transactions ADD COLUMN is_skipped BOOLEAN DEFAULT 0"
                ))
                print("✓ Added is_skipped to transactions")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ is_skipped already exists in transactions")
                else:
                    raise
            
            # Add account_id to bills table
            print("Adding account_id to bills table...")
            try:
                db.session.execute(db.text(
                    "ALTER TABLE bills ADD COLUMN account_id INTEGER REFERENCES accounts(id)"
                ))
                print("✓ Added account_id to bills")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("⚠ account_id already exists in bills")
                else:
                    raise
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    add_columns()
