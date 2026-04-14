from unittest.mock import patch

from app.exceptions import ConflictError, NotFoundError, ValidationError


def test_get_users(client):
    fake_users = [
        (1, "Anna", "anna@example.com"),
        (2, "Jan", None),
    ]

    with patch(
        "app.routes.api.get_users_service",
        return_value=(fake_users, len(fake_users)),
    ):
        response = client.get("/api/users")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Anna", "email": "anna@example.com"},
            {"id": 2, "name": "Jan", "email": None},
        ],
        "page": 1,
        "limit": 10,
        "total": 2,
    }


def test_get_user_found(client):
    with patch(
        "app.routes.api.get_user_by_id_service",
        return_value=(1, "Anna", "anna@example.com"),
    ):
        response = client.get("/api/users/1")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "name": "Anna",
        "email": "anna@example.com",
    }


def test_get_user_not_found(client):
    with patch(
        "app.routes.api.get_user_by_id_service",
        side_effect=NotFoundError("User not found", code="user_not_found"),
    ):
        response = client.get("/api/users/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "User not found",
        "code": "user_not_found",
    }


def test_create_user_success(client):
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
        "user": {"id": 1, "name": "Anna", "email": "anna@example.com"},
    }


def test_create_user_without_name(client):
    with patch(
        "app.routes.api.create_user_service",
        side_effect=ValidationError("Name is required", code="name_required"),
    ):
        response = client.post("/api/users", json={})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Name is required",
        "code": "name_required",
    }


def test_create_user_with_blank_name(client):
    with patch(
        "app.routes.api.create_user_service",
        side_effect=ValidationError("Name is required", code="name_required"),
    ):
        response = client.post("/api/users", json={"name": "   "})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Name is required",
        "code": "name_required",
    }


def test_create_user_with_invalid_email(client):
    with patch(
        "app.routes.api.create_user_service",
        side_effect=ValidationError("Email is invalid", code="invalid_email"),
    ):
        response = client.post(
            "/api/users",
            json={"name": "Anna", "email": "zly-email"},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email is invalid",
        "code": "invalid_email",
    }


def test_create_user_with_existing_email(client):
    with patch(
        "app.routes.api.create_user_service",
        side_effect=ConflictError("Email already exists", code="email_exists"),
    ):
        response = client.post(
            "/api/users",
            json={"name": "Anna", "email": "anna@example.com"},
        )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "Email already exists",
        "code": "email_exists",
    }


def test_update_user_success(client):
    with patch(
        "app.routes.api.update_user_service",
        return_value=(1, "Kasia", "kasia@example.com"),
    ):
        response = client.put(
            "/api/users/1",
            json={"name": "Kasia", "email": "kasia@example.com"},
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "User updated",
        "user": {"id": 1, "name": "Kasia", "email": "kasia@example.com"},
    }


def test_update_user_without_name_field(client):
    response = client.put("/api/users/1", json={"email": "kasia@example.com"})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Name is required",
        "code": "name_required",
    }


def test_update_user_not_found(client):
    with patch(
        "app.routes.api.update_user_service",
        side_effect=NotFoundError("User not found", code="user_not_found"),
    ):
        response = client.put(
            "/api/users/999",
            json={"name": "Kasia", "email": "kasia@example.com"},
        )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "User not found",
        "code": "user_not_found",
    }


def test_update_user_with_invalid_email(client):
    with patch(
        "app.routes.api.update_user_service",
        side_effect=ValidationError("Email is invalid", code="invalid_email"),
    ):
        response = client.put(
            "/api/users/1",
            json={"name": "Kasia", "email": "zly-email"},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email is invalid",
        "code": "invalid_email",
    }


def test_update_user_with_existing_email(client):
    with patch(
        "app.routes.api.update_user_service",
        side_effect=ConflictError("Email already exists", code="email_exists"),
    ):
        response = client.put(
            "/api/users/1",
            json={"name": "Kasia", "email": "anna@example.com"},
        )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "Email already exists",
        "code": "email_exists",
    }


def test_delete_user_success(client):
    with patch("app.routes.api.delete_user_service", return_value=(1,)):
        response = client.delete("/api/users/1")

    assert response.status_code == 200
    assert response.get_json() == {"message": "User deleted", "id": 1}


def test_delete_user_not_found(client):
    with patch(
        "app.routes.api.delete_user_service",
        side_effect=NotFoundError("User not found", code="user_not_found"),
    ):
        response = client.delete("/api/users/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "User not found",
        "code": "user_not_found",
    }


def test_search_users(client):
    fake_users = [(1, "Anna", "anna@example.com")]

    with patch(
        "app.routes.api.get_users_service",
        return_value=(fake_users, 1),
    ):
        response = client.get("/api/users?q=anna")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Anna", "email": "anna@example.com"},
        ],
        "page": 1,
        "limit": 10,
        "total": 1,
    }


def test_pagination(client):
    fake_users = [(1, "Anna", "anna@example.com")]

    with patch(
        "app.routes.api.get_users_service",
        return_value=(fake_users, 1),
    ):
        response = client.get("/api/users?page=1&limit=10")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Anna", "email": "anna@example.com"},
        ],
        "page": 1,
        "limit": 10,
        "total": 1,
    }


def test_pagination_with_custom_limit(client):
    fake_users = [(1, "Anna", "anna@example.com")]

    with patch(
        "app.routes.api.get_users_service",
        return_value=(fake_users, 1),
    ):
        response = client.get("/api/users?page=2&limit=5")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Anna", "email": "anna@example.com"},
        ],
        "page": 2,
        "limit": 5,
        "total": 1,
    }


def test_limit_is_capped_to_100(client):
    fake_users = [(1, "Anna", "anna@example.com")]

    with patch(
        "app.routes.api.get_users_service",
        return_value=(fake_users, 1),
    ) as mocked_service:
        response = client.get("/api/users?limit=999")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Anna", "email": "anna@example.com"},
        ],
        "page": 1,
        "limit": 100,
        "total": 1,
    }

    mocked_service.assert_called_once_with(query=None, page=1, limit=100)


def test_page_lower_than_1_is_normalized_to_1(client):
    fake_users = [(1, "Anna", "anna@example.com")]

    with patch(
        "app.routes.api.get_users_service",
        return_value=(fake_users, 1),
    ) as mocked_service:
        response = client.get("/api/users?page=0")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Anna", "email": "anna@example.com"},
        ],
        "page": 1,
        "limit": 10,
        "total": 1,
    }

    mocked_service.assert_called_once_with(query=None, page=1, limit=10)