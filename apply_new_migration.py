#!/usr/bin/env python3
"""
Apply the new models migration to the P.A.T.R.I.O.T. database
"""
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "patriot", "backend"))

from patriot.backend.app import create_app
from patriot.backend.database import db
from flask_migrate import Migrate, upgrade
import subprocess

def apply_migration():
    """Apply pending migrations to the database"""
    app = create_app()
    migrate = Migrate(app, db, directory='patriot/backend/migrations')
    
    with app.app_context():
        print("=" * 80)
        print("Applying P.A.T.R.I.O.T. Database Migrations")
        print("=" * 80)
        
        try:
            # Use subprocess to run flask db upgrade command
            result = subprocess.run(
                [
                    sys.executable, "-m", "flask", "db", "upgrade",
                    "--directory", "patriot/backend/migrations"
                ],
                env={**os.environ, "FLASK_APP": "patriot.backend.app:create_app"},
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            
            print("\n" + result.stdout)
            if result.stderr:
                print("Errors/Warnings:", result.stderr)
            
            if result.returncode == 0:
                print("\n✅ Migrations applied successfully!")
                print("\nNew tables created:")
                print("  - categories: Financial categorization")
                print("  - expenses: Expense tracking")
                print("  - goals: Financial goals")
                print("  - savings: Savings transactions")
            else:
                print(f"\n❌ Migration failed with return code {result.returncode}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error applying migration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
