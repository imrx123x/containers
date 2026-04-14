from app.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.repository import get_user_by_email
from app.services.user_service import create_user_service, validate_user_name
from app.utils import (
    generate_access_token,
    hash_password,
    normalize_email,
    validate_password,
    verify_password,
)


def register_user_service(name, raw_email, password):
    validate_user_name(name)

    email = normalize_email(raw_email)
    if raw_email is not None and email is None:
        raise ValidationError("Email is invalid", code="invalid_email")

    if not email:
        raise ValidationError("Email is required", code="email_required")

    if not validate_password(password):
        raise ValidationError(
            "Password must be at least 8 characters",
            code="weak_password",
        )

    if get_user_by_email(email):
        raise ConflictError("Email already exists", code="email_exists")

    user = create_user_service(
        name=name,
        raw_email=email,
        password_hash=hash_password(password),
        role="user",
    )

    token = generate_access_token(user)

    return {
        "message": "Registration successful",
        "access_token": token,
        "user": user,
    }


def login_user_service(raw_email, password):
    email = normalize_email(raw_email)
    if not email:
        raise UnauthorizedError("Invalid credentials", code="invalid_credentials")

    user = get_user_by_email(email, include_password=True)

    if not user:
        raise UnauthorizedError("Invalid credentials", code="invalid_credentials")

    if not verify_password(user.get("password_hash"), password):
        raise UnauthorizedError("Invalid credentials", code="invalid_credentials")

    token = generate_access_token(user)

    return {
        "message": "Login successful",
        "access_token": token,
        "user": user,
    }