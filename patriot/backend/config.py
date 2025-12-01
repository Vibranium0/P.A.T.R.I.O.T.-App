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
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7")))

    # Application Settings
    APP_NAME = "Patriot"
    APP_URL = os.getenv("APP_URL", "http://localhost:5173")

    @property
    def is_development(self):
        return self.ENV == "development"

    @property
    def is_production(self):
        return self.ENV == "production"
