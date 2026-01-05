#!/usr/bin/env python3
import sys
import os

# Add the sentinel_login/backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sentinel_login', 'backend'))

from app import app
from database import db

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Database reset complete!")
