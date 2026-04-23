import os
import re

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash


EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


def normalize_email(email_value):
    if email_value is None:
        return None

    email = email_value.strip().lower()

    if not email:
        return None

    if not EMAIL_REGEX.match(email):
        return None

    if len(email) > 255:
        return None

    return email


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    if not password_hash:
        return False
    return check_password_hash(password_hash, password)


def validate_password(password: str) -> bool:
    return isinstance(password, str) and len(password) >= 8


def _get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _get_access_token_max_age() -> int:
    raw_value = os.getenv("ACCESS_TOKEN_MAX_AGE_SECONDS", "3600")

    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return 3600

    if value <= 0:
        return 3600

    return value


def generate_access_token(user: dict) -> str:
    serializer = _get_serializer()
    return serializer.dumps(
        {
            "sub": user["id"],
            "role": user.get("role", "user"),
            "email": user.get("email"),
            "token_version": user.get("token_version", 0),
        },
        salt="access-token",
    )


def decode_access_token(token: str, max_age: int | None = None):
    serializer = _get_serializer()

    if max_age is None:
        max_age = _get_access_token_max_age()

    try:
        return serializer.loads(token, salt="access-token", max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


def generate_password_reset_token(user: dict) -> str:
    serializer = _get_serializer()
    return serializer.dumps(
        {
            "sub": user["id"],
            "email": user.get("email"),
            "purpose": "password-reset",
        },
        salt="password-reset-token",
    )


def decode_password_reset_token(token: str, max_age: int = 60 * 30):
    serializer = _get_serializer()

    try:
        payload = serializer.loads(
            token,
            salt="password-reset-token",
            max_age=max_age,
        )
    except (BadSignature, SignatureExpired):
        return None

    if payload.get("purpose") != "password-reset":
        return None

    return payload


def extract_bearer_token(auth_header: str | None):
    if not auth_header:
        return None

    parts = auth_header.split()

    if len(parts) != 2:
        return None

    scheme, token = parts

    if scheme.lower() != "bearer":
        return None

    return token