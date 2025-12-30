from sentinel_login.backend.database import db
from shared.models.user import create_user_model

User = create_user_model(db)
