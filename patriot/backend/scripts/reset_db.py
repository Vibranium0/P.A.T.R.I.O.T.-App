#!/usr/bin/env python3
"""Simple database reset script"""

import os
import sqlite3

def main():
    # Path to the database file (relative to backend directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    db_path = os.path.join(backend_dir, "instance", "patriot.db")
    
    try:
        # Check if database exists
        if os.path.exists(db_path):
            print(f"Removing existing database: {db_path}")
            os.remove(db_path)
        
        print("✅ Database file removed. The Flask app will recreate it with the new schema on next startup.")
        print("Make sure to restart your Flask server to apply the changes.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())