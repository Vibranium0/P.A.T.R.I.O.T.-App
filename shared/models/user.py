
# Module-level cache to prevent double creation per db instance
_user_model_cache = {}

def create_user_model(db):
    if id(db) in _user_model_cache:
        return _user_model_cache[id(db)]
    class User(db.Model):
        __tablename__ = "users"
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        name = db.Column(db.String(120), nullable=True)
        theme = db.Column(db.String(50), default="light")
        password_hash = db.Column(db.String(128), nullable=False)
        is_active = db.Column(db.Boolean, default=True)

        def to_dict(self):
            return {
                "id": self.id,
                "username": self.username,
                "email": self.email,
                "name": self.name,
                "theme": self.theme,
                "is_active": self.is_active,
            }

    _user_model_cache[id(db)] = User
    return User
