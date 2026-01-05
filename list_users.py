#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sentinel_login.backend.app import app
from sentinel_login.backend.database import db
from sentinel_login.backend.models.user import User

with app.app_context():
    users = User.query.all()
    
    if not users:
        print("No users found in database.")
    else:
        print(f"Found {len(users)} user(s):\n")
        for user in users:
            print(f"  - Username: {user.username}")
            print(f"    Email: {user.email}")
            print(f"    Security Question: {user.security_question}")
            print()
