from flask import Flask
from flask_cors import CORS
from sentinel_login.backend.config import Config
from sentinel_login.backend.database import db
from sentinel_login.backend.routes.auth_routes import auth_bp
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Sentinel database tables created.")
    app.run(debug=True, host="0.0.0.0", port=5001)
