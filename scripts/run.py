#!/usr/bin/env python
"""Simple run script for the Flask application."""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate them to ensure fresh schema
        print("🔄 Resetting database...")
        db.drop_all()
        db.create_all()
        print("✅ Database tables created with fresh schema.")
    
    print("🚀 Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)