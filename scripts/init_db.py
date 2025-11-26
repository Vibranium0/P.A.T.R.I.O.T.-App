#!/usr/bin/env python3
"""
Database initialization script for the Patriot App backend.

This script provides an alternative way to initialize the database
if Flask CLI has environment issues.
"""

import sys
import os

# Add the backend directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

from backend.app import create_app
from backend.database import db


def init_database():
    """Initialize the database by dropping and recreating all tables."""
    app = create_app()

    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()

        print(
            "Creating all tables for models: User, Bill, Fund, Transaction, Income..."
        )
        db.create_all()

        print("✅ Database tables created.")

        # Verify tables were created
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")


if __name__ == "__main__":
    init_database()
