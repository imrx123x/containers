from app.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from app.repository import get_user_by_email, get_user_by_id, update_user_password_in_db
from app.services.user_service import create_user_service, validate_user_name
from app.utils import (
    decode_password_reset_token,
    generate_access_token,
    generate_password_reset_token,
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


def change_password_service(user_id: int, current_password: str, new_password: str):
    if not current_password:
        raise ValidationError("Current password is required", code="current_password_required")

    if not validate_password(new_password):
        raise ValidationError(
            "New password must be at least 8 characters",
            code="weak_new_password",
        )

    user = get_user_by_id(user_id)
    if not user:
        raise NotFoundError("User not found", code="user_not_found")

    auth_user = get_user_by_email(user["email"], include_password=True)
    if not auth_user:
        raise NotFoundError("User not found", code="user_not_found")

    if not verify_password(auth_user.get("password_hash"), current_password):
        raise UnauthorizedError(
            "Current password is incorrect",
            code="invalid_current_password",
        )

    if verify_password(auth_user.get("password_hash"), new_password):
        raise ValidationError(
            "New password must be different from current password",
            code="same_password",
        )

    updated_user = update_user_password_in_db(
        user_id=user_id,
        password_hash=hash_password(new_password),
    )

    if not updated_user:
        raise NotFoundError("User not found", code="user_not_found")

    return {
        "message": "Password changed successfully",
        "user": updated_user,
    }


def request_password_reset_service(raw_email: str):
    email = normalize_email(raw_email)

    if not email:
        raise ValidationError("Email is invalid", code="invalid_email")

    user = get_user_by_email(email, include_password=True)

    if not user:
        raise NotFoundError("User not found", code="user_not_found")

    reset_token = generate_password_reset_token(user)

    return {
        "message": "Password reset link generated",
        "user": user,
        "reset_token": reset_token,
    }


def reset_password_with_token_service(token: str, new_password: str):
    if not token:
        raise ValidationError("Reset token is required", code="reset_token_required")

    if not validate_password(new_password):
        raise ValidationError(
            "New password must be at least 8 characters",
            code="weak_new_password",
        )

    payload = decode_password_reset_token(token)
    if not payload:
        raise UnauthorizedError("Invalid or expired reset token", code="invalid_reset_token")

    user_id = payload.get("sub")
    email = payload.get("email")

    if user_id is None or not email:
        raise UnauthorizedError("Invalid or expired reset token", code="invalid_reset_token")

    user = get_user_by_id(user_id)
    if not user:
        raise NotFoundError("User not found", code="user_not_found")

    auth_user = get_user_by_email(email, include_password=True)
    if not auth_user:
        raise NotFoundError("User not found", code="user_not_found")

    if auth_user["id"] != user_id:
        raise UnauthorizedError("Invalid or expired reset token", code="invalid_reset_token")

    if verify_password(auth_user.get("password_hash"), new_password):
        raise ValidationError(
            "New password must be different from current password",
            code="same_password",
        )

    updated_user = update_user_password_in_db(
        user_id=user_id,
        password_hash=hash_password(new_password),
    )

    if not updated_user:
        raise NotFoundError("User not found", code="user_not_found")

    return {
        "message": "Password has been reset successfully",
        "user": updated_user,
    }