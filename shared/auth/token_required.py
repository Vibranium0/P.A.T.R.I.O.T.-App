from functools import wraps
from flask import request, jsonify
import jwt

# Example implementation, adjust as needed for your app


def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[-1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            # Replace 'your_secret_key' with your actual secret key
            data = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
            request.user_id = data["user_id"]
        except Exception as e:
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401
        return f(*args, **kwargs)

    return decorated
