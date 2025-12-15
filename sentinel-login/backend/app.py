from flask import Flask
from config import Config
from database import db
from routes.auth_routes import auth_bp
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)