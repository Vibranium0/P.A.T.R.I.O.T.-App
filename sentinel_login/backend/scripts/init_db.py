# scripts/init_db.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
from database import db
from sentinel_login.backend import models  # ensure all models are imported

with app.app_context():
    db.create_all()
    print("Database tables created.")
