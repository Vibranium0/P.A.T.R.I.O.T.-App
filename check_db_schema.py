#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sentinel_login.backend.app import app
from sentinel_login.backend.database import db
from sqlalchemy import text

with app.app_context():
    print("\n=== USERS TABLE SCHEMA ===")
    result = db.session.execute(text("PRAGMA table_info(users)"))
    for row in result:
        print(f"  {row[1]:25} {row[2]:15} NOT NULL: {row[3]} DEFAULT: {row[4]}")
    
    print("\n=== HOUSEHOLDS TABLE SCHEMA ===")
    result = db.session.execute(text("PRAGMA table_info(households)"))
    for row in result:
        print(f"  {row[1]:25} {row[2]:15} NOT NULL: {row[3]} DEFAULT: {row[4]}")
