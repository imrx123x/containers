from unittest.mock import patch

from app.exceptions import ConflictError, NotFoundError, ValidationError


def test_patch_me_success_name_only(client):
    updated_user = {
        "id": 0,
        "name": "Updated User",
        "email": "test@example.com",
        "role": "admin",
        "created_at": None,
        "updated_at": None,
    }

    with patch(
        "app.routes.auth.update_current_user_service",
        return_value=updated_user,
    ):
        response = client.patch(
            "/api/auth/me",
            json={"name": "Updated User"},
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Profile updated",
        "user": {
            "id": 0,
            "name": "Updated User",
            "email": "test@example.com",
            "role": "admin",
            "created_at": None,
            "updated_at": None,
        },
    }


def test_patch_me_success_email_only(client):
    updated_user = {
        "id": 0,
        "name": "Test User",
        "email": "updated@example.com",
        "role": "admin",
        "created_at": None,
        "updated_at": None,
    }

    with patch(
        "app.routes.auth.update_current_user_service",
        return_value=updated_user,
    ):
        response = client.patch(
            "/api/auth/me",
            json={"email": "updated@example.com"},
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Profile updated",
        "user": {
            "id": 0,
            "name": "Test User",
            "email": "updated@example.com",
            "role": "admin",
            "created_at": None,
            "updated_at": None,
        },
    }


def test_patch_me_success_name_and_email(client):
    updated_user = {
        "id": 0,
        "name": "Updated User",
        "email": "updated@example.com",
        "role": "admin",
        "created_at": None,
        "updated_at": None,
    }

    with patch(
        "app.routes.auth.update_current_user_service",
        return_value=updated_user,
    ):
        response = client.patch(
            "/api/auth/me",
            json={
                "name": "Updated User",
                "email": "updated@example.com",
            },
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Profile updated",
        "user": {
            "id": 0,
            "name": "Updated User",
            "email": "updated@example.com",
            "role": "admin",
            "created_at": None,
            "updated_at": None,
        },
    }


def test_patch_me_without_fields(client):
    with patch(
        "app.routes.auth.update_current_user_service",
        side_effect=ValidationError(
            "At least one field is required",
            code="no_fields_to_update",
        ),
    ):
        response = client.patch("/api/auth/me", json={})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "At least one field is required",
        "code": "no_fields_to_update",
    }


def test_patch_me_with_invalid_email(client):
    with patch(
        "app.routes.auth.update_current_user_service",
        side_effect=ValidationError("Email is invalid", code="invalid_email"),
    ):
        response = client.patch(
            "/api/auth/me",
            json={"email": "zly-email"},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email is invalid",
        "code": "invalid_email",
    }


def test_patch_me_with_blank_name(client):
    with patch(
        "app.routes.auth.update_current_user_service",
        side_effect=ValidationError("Name is required", code="name_required"),
    ):
        response = client.patch(
            "/api/auth/me",
            json={"name": "   "},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Name is required",
        "code": "name_required",
    }


def test_patch_me_with_existing_email(client):
    with patch(
        "app.routes.auth.update_current_user_service",
        side_effect=ConflictError("Email already exists", code="email_exists"),
    ):
        response = client.patch(
            "/api/auth/me",
            json={"email": "anna@example.com"},
        )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "Email already exists",
        "code": "email_exists",
    }


def test_patch_me_user_not_found(client):
    with patch(
        "app.routes.auth.update_current_user_service",
        side_effect=NotFoundError("User not found", code="user_not_found"),
    ):
        response = client.patch(
            "/api/auth/me",
            json={"name": "Updated User"},
        )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "User not found",
        "code": "user_not_found",
    }