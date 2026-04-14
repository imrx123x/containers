from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.repository import (
    add_user_to_db,
    get_user_by_email,
    get_user_by_id,
    search_users_paginated,
    get_users_paginated,
    update_user_in_db,
    delete_user_from_db,
)
from app.utils import normalize_email


def validate_user_name(name: str) -> str:
    normalized_name = (name or "").strip()

    if not normalized_name:
        raise ValidationError("Name is required", code="name_required")

    if len(normalized_name) > 100:
        raise ValidationError("Name too long", code="name_too_long")

    return normalized_name


def validate_user_email(raw_email):
    email = normalize_email(raw_email)

    if raw_email is not None and email is None:
        raise ValidationError("Email is invalid", code="invalid_email")

    return email


def get_users_service(query, page: int, limit: int):
    if query:
        return search_users_paginated(query, page, limit)
    return get_users_paginated(page, limit)


def get_user_by_id_service(user_id: int):
    user = get_user_by_id(user_id)

    if not user:
        raise NotFoundError("User not found", code="user_not_found")

    return user


def create_user_service(name, raw_email, password_hash=None, role="user"):
    validated_name = validate_user_name(name)
    email = validate_user_email(raw_email)

    if email:
        existing_user = get_user_by_email(email)
        if existing_user:
            raise ConflictError("Email already exists", code="email_exists")

    user = add_user_to_db(
        name=validated_name,
        email=email,
        password_hash=password_hash,
        role=role,
    )

    return user


def update_user_service(user_id: int, name, raw_email):
    validated_name = validate_user_name(name)
    email = validate_user_email(raw_email)

    existing_user = get_user_by_id(user_id)
    if not existing_user:
        raise NotFoundError("User not found", code="user_not_found")

    if email:
        other_user = get_user_by_email(email)
        if other_user and other_user["id"] != user_id:
            raise ConflictError("Email already exists", code="email_exists")

    updated_user = update_user_in_db(
        user_id=user_id,
        name=validated_name,
        email=email,
    )

    if not updated_user:
        raise NotFoundError("User not found", code="user_not_found")

    return updated_user


def delete_user_service(user_id: int):
    deleted_user = delete_user_from_db(user_id)

    if not deleted_user:
        raise NotFoundError("User not found", code="user_not_found")

    return deleted_user