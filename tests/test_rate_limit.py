from unittest.mock import patch

from app.exceptions import ForbiddenError


def test_register_rate_limit_success(client):
    fake_result = {
        "message": "Registration successful",
        "access_token": "fake-token",
        "user": {
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
            "created_at": None,
            "updated_at": None,
        },
    }

    with patch("app.routes.auth.enforce_rate_limit") as mocked_rate_limit:
        with patch(
            "app.routes.auth.register_user_service",
            return_value=fake_result,
        ):
            response = client.post(
                "/api/auth/register",
                json={
                    "name": "Anna",
                    "email": "anna@example.com",
                    "password": "supersecret",
                },
            )

    assert response.status_code == 201
    mocked_rate_limit.assert_called_once_with(
        action="auth_register",
        limit=5,
        window_seconds=60,
    )


def test_register_rate_limit_exceeded(client):
    with patch(
        "app.routes.auth.enforce_rate_limit",
        side_effect=ForbiddenError(
            "Too many requests, try again later",
            code="rate_limit_exceeded",
        ),
    ):
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Anna",
                "email": "anna@example.com",
                "password": "supersecret",
            },
        )

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "Too many requests, try again later",
        "code": "rate_limit_exceeded",
    }


def test_login_rate_limit_success(client):
    fake_result = {
        "message": "Login successful",
        "access_token": "fake-token",
        "user": {
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
            "created_at": None,
            "updated_at": None,
        },
    }

    with patch("app.routes.auth.enforce_rate_limit") as mocked_rate_limit:
        with patch(
            "app.routes.auth.login_user_service",
            return_value=fake_result,
        ):
            response = client.post(
                "/api/auth/login",
                json={
                    "email": "anna@example.com",
                    "password": "supersecret",
                },
            )

    assert response.status_code == 200
    mocked_rate_limit.assert_called_once_with(
        action="auth_login",
        limit=10,
        window_seconds=60,
    )


def test_login_rate_limit_exceeded(client):
    with patch(
        "app.routes.auth.enforce_rate_limit",
        side_effect=ForbiddenError(
            "Too many requests, try again later",
            code="rate_limit_exceeded",
        ),
    ):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "anna@example.com",
                "password": "supersecret",
            },
        )

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "Too many requests, try again later",
        "code": "rate_limit_exceeded",
    }


def test_change_password_rate_limit_success(client):
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

    with patch("app.routes.auth.enforce_rate_limit") as mocked_rate_limit:
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
    mocked_rate_limit.assert_called_once_with(
        action="auth_change_password",
        limit=5,
        window_seconds=60,
        identifier="0",
    )


def test_change_password_rate_limit_exceeded(client):
    with patch(
        "app.routes.auth.enforce_rate_limit",
        side_effect=ForbiddenError(
            "Too many requests, try again later",
            code="rate_limit_exceeded",
        ),
    ):
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "oldpass123",
                "new_password": "newpass123",
            },
        )

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "Too many requests, try again later",
        "code": "rate_limit_exceeded",
    }