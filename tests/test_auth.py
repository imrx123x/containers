from unittest.mock import patch

from app.exceptions import ConflictError, UnauthorizedError, ValidationError


def test_register_success(client):
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
    assert response.get_json() == {
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


def test_register_without_name(client):
    with patch(
        "app.routes.auth.register_user_service",
        side_effect=ValidationError("Name is required", code="name_required"),
    ):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "anna@example.com",
                "password": "supersecret",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Name is required",
        "code": "name_required",
    }


def test_register_with_invalid_email(client):
    with patch(
        "app.routes.auth.register_user_service",
        side_effect=ValidationError("Email is invalid", code="invalid_email"),
    ):
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Anna",
                "email": "zly-email",
                "password": "supersecret",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email is invalid",
        "code": "invalid_email",
    }


def test_register_without_email(client):
    with patch(
        "app.routes.auth.register_user_service",
        side_effect=ValidationError("Email is required", code="email_required"),
    ):
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Anna",
                "password": "supersecret",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email is required",
        "code": "email_required",
    }


def test_register_with_weak_password(client):
    with patch(
        "app.routes.auth.register_user_service",
        side_effect=ValidationError(
            "Password must be at least 8 characters",
            code="weak_password",
        ),
    ):
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Anna",
                "email": "anna@example.com",
                "password": "123",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Password must be at least 8 characters",
        "code": "weak_password",
    }


def test_register_with_existing_email(client):
    with patch(
        "app.routes.auth.register_user_service",
        side_effect=ConflictError("Email already exists", code="email_exists"),
    ):
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Anna",
                "email": "anna@example.com",
                "password": "supersecret",
            },
        )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "Email already exists",
        "code": "email_exists",
    }


def test_login_success(client):
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
    assert response.get_json() == {
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


def test_login_with_invalid_credentials(client):
    with patch(
        "app.routes.auth.login_user_service",
        side_effect=UnauthorizedError(
            "Invalid credentials",
            code="invalid_credentials",
        ),
    ):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "anna@example.com",
                "password": "wrong-password",
            },
        )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid credentials",
        "code": "invalid_credentials",
    }


def test_login_with_invalid_email(client):
    with patch(
        "app.routes.auth.login_user_service",
        side_effect=UnauthorizedError(
            "Invalid credentials",
            code="invalid_credentials",
        ),
    ):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "zly-email",
                "password": "whatever123",
            },
        )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid credentials",
        "code": "invalid_credentials",
    }


def test_me_success(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 0,
        "name": "Test User",
        "email": "test@example.com",
        "role": "admin",
        "created_at": None,
        "updated_at": None,
    }


def test_users_endpoint_requires_auth_but_testing_bypasses_it(client):
    with patch(
        "app.routes.api.get_users_service",
        return_value=([], 0),
    ):
        response = client.get("/api/users")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [],
        "page": 1,
        "limit": 10,
        "total": 0,
    }


def test_admin_endpoint_in_testing_mode_allows_access(client):
    with patch(
        "app.routes.api.create_user_service",
        return_value=(1, "Anna", "anna@example.com"),
    ):
        response = client.post(
            "/api/users",
            json={"name": "Anna", "email": "anna@example.com"},
        )

    assert response.status_code == 201
    assert response.get_json() == {
        "message": "User created",
        "user": {
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
        },
    }


def test_me_contains_test_admin_in_testing_mode(client):
    response = client.get("/api/auth/me")

    body = response.get_json()

    assert response.status_code == 200
    assert body["id"] == 0
    assert body["name"] == "Test User"
    assert body["email"] == "test@example.com"
    assert body["role"] == "admin"