from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from patriot.backend.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Import and register blueprints
    from routes.financial_accounts_routes import financial_accounts_bp
    from routes.funds_routes import funds_bp
    from routes.transactions_routes import tx_bp
    from routes.reports_routes import reports_bp

    app.register_blueprint(financial_accounts_bp, url_prefix="/api/financial-accounts")
    app.register_blueprint(funds_bp, url_prefix="/api/funds")
    app.register_blueprint(tx_bp, url_prefix="/api/transactions")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    return app
