#!/usr/bin/env python3
"""
Generate migration for new P.A.T.R.I.O.T. models
(Category, Expense, Goal, Saving)
"""
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "patriot", "backend"))

from patriot.backend.app import create_app
from patriot.backend.database import db
from flask_migrate import Migrate, upgrade, migrate as flask_migrate

# Import all models to ensure they're registered
from patriot.backend.models import (
    Account, Bill, Debt, Fund, Income, Transaction,
    Category, Expense, Goal, Saving, User,
    Household, HouseholdInvite
)

def generate_migration():
    """Generate a new migration for the updated models"""
    app = create_app()
    migrate = Migrate(app, db, directory='patriot/backend/migrations')
    
    with app.app_context():
        print("=" * 80)
        print("Generating migration for new P.A.T.R.I.O.T. models")
        print("=" * 80)
        print("\nNew models being added:")
        print("  - Category: Financial categorization system")
        print("  - Expense: Detailed expense tracking")
        print("  - Goal: Financial goals management")
        print("  - Saving: Savings transactions and progress")
        print("\n" + "=" * 80)
        
        try:
            # Import flask_migrate directly to call the migrate command
            from flask_migrate import migrate as generate_migration_command
            import subprocess
            
            # Use subprocess to run flask db migrate command
            result = subprocess.run(
                [
                    sys.executable, "-m", "flask", "db", "migrate",
                    "-m", "Add Category, Expense, Goal, and Saving models",
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
                print("\n✅ Migration generated successfully!")
                print("\nTo apply this migration, run:")
                print("  python apply_new_migration.py")
            else:
                print(f"\n❌ Migration generation failed with return code {result.returncode}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error generating migration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    success = generate_migration()
    sys.exit(0 if success else 1)
