# Backend API Server

Flask-based REST API server for the Patriot personal finance management application.

## Directory Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── database.py            # Database initialization
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .env.example          # Environment template
├── routes/               # API route handlers
│   ├── auth_routes.py    # Authentication endpoints
│   ├── user_routes.py    # User management
│   ├── funds_routes.py   # Funds management
│   ├── transactions_routes.py # Transaction endpoints
│   ├── accounts_routes.py # Account management
│   └── reports_routes.py # Reporting endpoints
├── models/               # Database models
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── fund.py          # Fund model
│   ├── transaction.py   # Transaction model
│   └── ...
├── utils/               # Utility functions
│   └── email_service.py # Email utilities
├── scripts/             # Database and utility scripts
│   ├── init_db.py       # Database initialization
│   ├── seed_db.py       # Sample data seeding
│   ├── migrate_db.py    # Database migrations
│   ├── reset_db.py      # Database reset
│   ├── run.py           # Development server
│   └── run_server.py    # Production server
├── docs/                # API documentation
│   ├── PROJECT_COMPLETE.md
│   ├── FUNDS_API.md
│   ├── TRANSACTIONS_API.md
│   ├── INCOME_API.md
│   └── ...
├── logs/                # Log files and backups
└── instance/            # Flask instance folder
```

## Quick Start

1. **Setup Virtual Environment**
   ```bash
   cd backend
   source .venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize Database**
   ```bash
   python scripts/init_db.py
   python scripts/seed_db.py
   ```

5. **Start Development Server**
   ```bash
   python app.py
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/verify` - Token verification

### Funds Management
- `GET /api/funds/` - List user funds
- `POST /api/funds/` - Create new fund
- `GET /api/funds/{id}` - Get fund details
- `PUT /api/funds/{id}` - Update fund
- `DELETE /api/funds/{id}` - Delete fund

### Transactions
- `GET /api/transactions/` - List transactions
- `POST /api/transactions/` - Create transaction
- `GET /api/transactions/{id}` - Get transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### User Management
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/stats` - Get user statistics

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Operations
```bash
# Reset database
python scripts/reset_db.py

# Seed with sample data
python scripts/seed_db.py

# Initialize fresh database
python scripts/init_db.py
```

### Environment Variables
Create a `.env` file with:
```
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///patriot.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Production Deployment

1. **Configure Production Environment**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

2. **Use Production Server**
   ```bash
   python scripts/run_server.py
   ```

3. **Setup Database**
   ```bash
   python scripts/init_db.py
   ```

## Security Features

- JWT authentication with automatic token refresh
- Password hashing with Werkzeug
- CORS protection
- Input validation and sanitization
- SQL injection prevention via SQLAlchemy ORM

## Database Models

- **User**: User accounts and authentication
- **Fund**: Savings funds and goals
- **Transaction**: Income and expense records
- **Account**: Financial accounts
- **Bill**: Recurring bills and payments

## API Documentation

Detailed API documentation is available in the `docs/` directory:
- [Funds API](docs/FUNDS_API.md)
- [Transactions API](docs/TRANSACTIONS_API.md)
- [Income API](docs/INCOME_API.md)
- [Complete Project Guide](docs/PROJECT_COMPLETE.md)