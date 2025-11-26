# backend/app.py
import logging
from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from backend.config import Config
from backend.database import db

# Import blueprints
from backend.routes.auth_routes import auth_bp
from backend.routes.accounts_routes import accounts_bp
from backend.routes.financial_accounts_routes import financial_accounts_bp
from backend.routes.bills_routes import bills_bp
from backend.routes.funds_routes import funds_bp
from backend.routes.transactions_routes import tx_bp
from backend.routes.income_routes import income_bp
from backend.routes.reports_routes import reports_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.debts_routes import debts_bp
from backend.routes.households_routes import households_bp

# Import models to ensure they're registered with SQLAlchemy
from backend.models.user import User
from backend.models.household import Household, HouseholdInvite, user_household
from backend.models.bill import Bill
from backend.models.fund import Fund
from backend.models.transaction import Transaction
from backend.models.income import Income
from backend.models.debt import Debt
from backend.models.account import Account

from flask_migrate import Migrate

bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)
    CORS(app)

    # Configure logging
    if not app.config.get('TESTING'):
        logging.basicConfig(
            level=logging.INFO if app.config['DEBUG'] else logging.WARNING,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(households_bp, url_prefix="/api/households")
    app.register_blueprint(accounts_bp, url_prefix="/api/accounts")
    app.register_blueprint(financial_accounts_bp, url_prefix="/api/financial-accounts")
    app.register_blueprint(bills_bp, url_prefix="/api/bills")
    app.register_blueprint(funds_bp, url_prefix="/api/funds")
    app.register_blueprint(tx_bp, url_prefix="/api/transactions")
    app.register_blueprint(income_bp, url_prefix="/api/income")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(debts_bp, url_prefix="/api/debts")

    # CLI command for database setup
    @app.cli.command("init-db")
    def init_db():
        """Initialize the database (drop and recreate all tables)."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("✅ Database tables created.")

    @app.cli.command("reset-db")
    def reset_db():
        """Reset the database (drop and recreate all tables)."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("✅ Database reset complete.")
    
    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database with sample data."""
        from scripts.seed_db import seed_database
        seed_database()
    
    @app.cli.command("reset-and-seed")
    def reset_and_seed():
        """Reset database and seed with sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("✅ Database reset complete.")
        from scripts.seed_db import seed_database
        seed_database()

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database tables created.")
    app.run(debug=True, host='0.0.0.0', port=5001)
