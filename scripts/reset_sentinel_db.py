#!/usr/bin/env python3
import sys
import os

# Add the sentinel_login/backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sentinel_login', 'backend'))

from flask import Flask
from config import Config
from database import db

# Create app and initialize db
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Database reset complete!")
