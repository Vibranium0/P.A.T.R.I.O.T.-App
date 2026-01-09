from flask import Flask
from flask_cors import CORS
from sentinel_login.backend.config import Config
from sentinel_login.backend.database import db
from sentinel_login.backend.routes.auth_routes import auth_bp
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS to allow credentials (for HttpOnly cookies)
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "https://curly-chainsaw-xrw5w677gjxc65gg-5173.app.github.dev",
        "https://curly-chainsaw-xrw5w677gjxc65gg-5175.app.github.dev",
    ],
)

# Initialize extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    with app.app_context():
        # Only create tables if they don't exist (migration script handles schema updates)
        from sqlalchemy import text

        result = db.session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        )
        if not result.fetchone():
            db.create_all()
            print("✅ Sentinel database tables created.")
        else:
            print("✅ Sentinel database tables already exist.")
    app.run(debug=True, host="0.0.0.0", port=5001)
