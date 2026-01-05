#!/usr/bin/env python3
import os

db_path = "/workspaces/P.A.T.R.I.O.T.-App/sentinel_login/backend/instance/sentinel-login.db"

if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Deleted {db_path}")
else:
    print(f"ℹ️  Database file doesn't exist: {db_path}")

print("\nNow restart the servers with: bash start_all_fixed.sh")
