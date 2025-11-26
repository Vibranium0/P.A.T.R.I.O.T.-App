from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from backend.config import Config

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
    from backend.routes.auth_routes import auth_bp
    from backend.routes.accounts_routes import accounts_bp
    from backend.routes.funds_routes import funds_bp
    from backend.routes.transactions_routes import tx_bp
    from backend.routes.reports_routes import reports_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(accounts_bp, url_prefix="/api/accounts")
    app.register_blueprint(funds_bp, url_prefix="/api/funds")
    app.register_blueprint(tx_bp, url_prefix="/api/transactions")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    return app
