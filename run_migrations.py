#!/usr/bin/env python3
"""
Run database migrations for sentinel_login
"""
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))

from sentinel_login.backend.app import app
from sentinel_login.backend.database import db
from sqlalchemy import text

def run_migrations():
    with app.app_context():
        print("Running database migrations...")
        
        try:
            # Check if users table exists and has the required columns
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
            table_exists = result.fetchone() is not None
            
            if table_exists:
                result = db.session.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                print(f"Current columns in users table: {columns}")
                
                # Check if required columns exist
                required_columns = ['default_household_id', 'security_question', 'security_answer']
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    print(f"❌ Missing columns detected: {missing_columns}")
                    print("🔄 Dropping and recreating all tables with correct schema...")
                    db.drop_all()
                    db.create_all()
                    print("✅ Database recreated with complete schema")
                else:
                    print("✅ All required columns exist")
            else:
                print("Creating tables for the first time...")
                db.create_all()
                print("✅ Database tables created")
            
            print("\n✅ All migrations completed successfully!")
            
        except Exception as e:
            print(f"❌ Error running migrations: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)
            
            print("\n✅ All migrations completed successfully!")
            
        except Exception as e:
            print(f"❌ Error running migrations: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    run_migrations()
