from unittest.mock import patch

from app.exceptions import NotFoundError, UnauthorizedError, ValidationError


def test_change_password_success(client):
    fake_result = {
        "message": "Password changed successfully",
        "user": {
            "id": 0,
            "name": "Test User",
            "email": "test@example.com",
            "role": "admin",
            "created_at": None,
            "updated_at": None,
        },
    }

    with patch(
        "app.routes.auth.change_password_service",
        return_value=fake_result,
    ):
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "oldpass123",
                "new_password": "newpass123",
            },
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Password changed successfully",
        "user": {
            "id": 0,
            "name": "Test User",
            "email": "test@example.com",
            "role": "admin",
            "created_at": None,
            "updated_at": None,
        },
    }


def test_change_password_requires_current_password(client):
    with patch(
        "app.routes.auth.change_password_service",
        side_effect=ValidationError(
            "Current password is required",
            code="current_password_required",
        ),
    ):
        response = client.post(
            "/api/auth/change-password",
            json={"new_password": "newpass123"},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Current password is required",
        "code": "current_password_required",
    }


def test_change_password_requires_strong_new_password(client):
    with patch(
        "app.routes.auth.change_password_service",
        side_effect=ValidationError(
            "New password must be at least 8 characters",
            code="weak_new_password",
        ),
    ):
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "oldpass123",
                "new_password": "123",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "New password must be at least 8 characters",
        "code": "weak_new_password",
    }


def test_change_password_rejects_same_password(client):
    with patch(
        "app.routes.auth.change_password_service",
        side_effect=ValidationError(
            "New password must be different from current password",
            code="same_password",
        ),
    ):
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "samepass123",
                "new_password": "samepass123",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "New password must be different from current password",
        "code": "same_password",
    }


def test_change_password_rejects_wrong_current_password(client):
    with patch(
        "app.routes.auth.change_password_service",
        side_effect=UnauthorizedError(
            "Current password is incorrect",
            code="invalid_current_password",
        ),
    ):
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "wrongpass123",
                "new_password": "newpass123",
            },
        )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Current password is incorrect",
        "code": "invalid_current_password",
    }


def test_change_password_user_not_found(client):
    with patch(
        "app.routes.auth.change_password_service",
        side_effect=NotFoundError("User not found", code="user_not_found"),
    ):
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "oldpass123",
                "new_password": "newpass123",
            },
        )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "User not found",
        "code": "user_not_found",
    }