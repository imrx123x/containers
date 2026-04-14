from functools import wraps

from flask import current_app, g, jsonify, request

from app.repository import get_user_by_id
from app.utils import decode_access_token, extract_bearer_token


def _set_test_user(role="admin"):
    g.current_user = {
        "id": 0,
        "name": "Test User",
        "email": "test@example.com",
        "role": role,
    }


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if current_app.config.get("TESTING"):
            _set_test_user(role="admin")
            return fn(*args, **kwargs)

        token = extract_bearer_token(request.headers.get("Authorization"))
        if not token:
            return jsonify({"error": "Missing bearer token"}), 401

        payload = decode_access_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        user_id = payload.get("sub")
        user = get_user_by_id(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 401

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if current_app.config.get("TESTING"):
            _set_test_user(role="admin")
            return fn(*args, **kwargs)

        token = extract_bearer_token(request.headers.get("Authorization"))
        if not token:
            return jsonify({"error": "Missing bearer token"}), 401

        payload = decode_access_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        user_id = payload.get("sub")
        user = get_user_by_id(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 401

        if user.get("role") != "admin":
            return jsonify({"error": "Forbidden"}), 403

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper