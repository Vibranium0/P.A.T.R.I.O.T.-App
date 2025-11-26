# Database Initialization Guide

## Overview
The Patriot App backend includes Flask CLI commands to initialize the database with all models (User, Bill, Fund, Transaction, Income).

## Available Methods

### Method 1: Flask CLI Command (Recommended)
The `init-db` command is registered as a Flask CLI command that drops and recreates all database tables.

```bash
# From the backend directory
cd /Users/christian/Documents/Projects/patriot-app/backend
source .venv/bin/activate
flask --app app:create_app init-db
```

**Note**: If you encounter import path issues with the Flask CLI, use Method 2 below.

### Method 2: Python Script (Alternative)
We've provided a standalone Python script for database initialization:

```bash
# From the backend directory
cd /Users/christian/Documents/Projects/patriot-app/backend
source .venv/bin/activate
python init_db.py
```

### Method 3: Direct Python Execution
You can also initialize the database directly via Python:

```bash
cd /Users/christian/Documents/Projects/patriot-app/backend
source .venv/bin/activate
python -c "
from app import create_app
from database import db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print('✅ Database tables created.')
"
```

## What Gets Created

The initialization process creates the following tables:

1. **users** - User accounts and authentication
2. **bills** - Recurring bill definitions for autopay
3. **funds** - User savings funds with goals
4. **transactions** - Financial transactions linked to funds
5. **incomes** - Income tracking entries

## CLI Command Details

The `init-db` command is defined in `app.py`:

```python
@app.cli.command("init-db")
def init_db():
    """Initialize the database (drop and recreate all tables)."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Database tables created.")
```

## Available CLI Commands

To see all available Flask CLI commands:

```bash
flask --app app:create_app --help
```

Current custom commands:
- `init-db`: Initialize the database (drop and recreate all tables)
- `reset-db`: Reset the database (drop and recreate all tables) - same functionality as init-db

## Troubleshooting

### Import Path Issues
If Flask CLI has trouble with import paths, use the alternative Python script method:

```bash
python init_db.py
```

### Module Not Found Errors
Ensure you're running from the backend directory and have activated the virtual environment:

```bash
cd /Users/christian/Documents/Projects/patriot-app/backend
source .venv/bin/activate
```

### Database Permission Issues
Ensure the SQLite database file is writable and the instance directory exists.

## Verification

After running any initialization method, you should see:
```
✅ Database tables created.
Created tables: bills, funds, incomes, transactions, users
```

The database file will be created at `backend/instance/app.db` (SQLite default).