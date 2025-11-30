#!/usr/bin/env python3
"""Database migration script to update Fund model with user_id and fund_type"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from database import db
# Import models to ensure they're registered
import models

def main():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Drop and recreate all tables
            print("Dropping all tables...")
            db.drop_all()
            
            print("Creating all tables with new schema...")
            db.create_all()
            
            print("✅ Database migration complete!")
            print("The Fund model now includes user_id and fund_type fields.")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())