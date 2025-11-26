import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Environment
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "1").lower() in ("1", "true", "yes", "on")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///patriot.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7")))
    
    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ("true", "1", "yes", "on")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in ("true", "1", "yes", "on")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME", ""))
    
    # Application Settings
    APP_NAME = "Patriot"
    APP_URL = os.getenv("APP_URL", "http://localhost:5173")
    
    # Sentinel Systems - User Sync Configuration
    # Comma-separated list of other Sentinel app API URLs
    SENTINEL_APPS = os.getenv("SENTINEL_APPS", "")
    # Current app's API URL (used to exclude self from sync)
    CURRENT_APP_URL = os.getenv("CURRENT_APP_URL", "http://localhost:5001")
    
    @property
    def is_development(self):
        return self.ENV == "development"
    
    @property
    def is_production(self):
        return self.ENV == "production"
