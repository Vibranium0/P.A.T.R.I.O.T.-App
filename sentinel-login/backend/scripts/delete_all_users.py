# scripts/delete_all_users.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
from database import db
from sentinel_login.backend.models.user import User

with app.app_context():
    num_deleted = User.query.delete()
    db.session.commit()
    print(f"Deleted {num_deleted} users.")
