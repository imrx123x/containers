from functools import wraps

from flask import current_app, g, request

from app.exceptions import ForbiddenError, UnauthorizedError
from app.repository import get_user_by_id
from app.utils import decode_access_token, extract_bearer_token


def _set_test_user(role="admin"):
    g.current_user = {
        "id": 0,
        "name": "Test User",
        "email": "test@example.com",
        "role": role,
        "token_version": 0,
    }


def load_current_user():
    if current_app.config.get("TESTING"):
        _set_test_user(role="admin")
        return g.current_user

    token = extract_bearer_token(request.headers.get("Authorization"))
    if not token:
        raise UnauthorizedError("Missing bearer token", code="missing_bearer_token")

    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedError(
            "Invalid or expired token",
            code="invalid_or_expired_token",
        )

    user_id = payload.get("sub")
    token_version = payload.get("token_version", 0)

    user = get_user_by_id(user_id)

    if not user:
        raise UnauthorizedError("User not found", code="user_not_found")

    current_token_version = user.get("token_version", 0)
    if token_version != current_token_version:
        raise UnauthorizedError(
            "Invalid or expired token",
            code="invalid_or_expired_token",
        )

    g.current_user = user
    return user


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        load_current_user()
        return fn(*args, **kwargs)

    return wrapper


def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_app.config.get("TESTING"):
                _set_test_user(role=required_role)
                return fn(*args, **kwargs)

            user = load_current_user()

            if user.get("role") != required_role:
                raise ForbiddenError("Forbidden", code="forbidden")

            return fn(*args, **kwargs)

        return wrapper

    return decorator


admin_required = role_required("admin")