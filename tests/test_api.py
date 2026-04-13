from unittest.mock import patch


def test_get_users(client):
    fake_users = [
        (1, "Anna", "anna@example.com"),
        (2, "Jan", None),
    ]

    with patch("app.routes.api.get_all_users", return_value=fake_users):
        response = client.get("/api/users")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "name": "Anna", "email": "anna@example.com"},
        {"id": 2, "name": "Jan", "email": None},
    ]


def test_get_user_found(client):
    with patch("app.routes.api.get_user_by_id", return_value=(1, "Anna", "anna@example.com")):
        response = client.get("/api/users/1")

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "name": "Anna", "email": "anna@example.com"}


def test_get_user_not_found(client):
    with patch("app.routes.api.get_user_by_id", return_value=None):
        response = client.get("/api/users/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}


def test_create_user_success(client):
    with patch("app.routes.api.add_user_to_db", return_value=(1, "Anna", "anna@example.com")):
        response = client.post("/api/users", json={"name": "Anna", "email": "anna@example.com"})

    assert response.status_code == 201
    assert response.get_json() == {
        "message": "User created",
        "user": {"id": 1, "name": "Anna", "email": "anna@example.com"},
    }


def test_create_user_without_name(client):
    response = client.post("/api/users", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Name is required"}


def test_create_user_with_blank_name(client):
    response = client.post("/api/users", json={"name": "   "})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Name is required"}


def test_create_user_with_invalid_email(client):
    response = client.post("/api/users", json={"name": "Anna", "email": "zly-email"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Email is invalid"}


def test_update_user_success(client):
    with patch("app.routes.api.update_user_in_db", return_value=(1, "Kasia", "kasia@example.com")):
        response = client.put("/api/users/1", json={"name": "Kasia", "email": "kasia@example.com"})

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "User updated",
        "user": {"id": 1, "name": "Kasia", "email": "kasia@example.com"},
    }


def test_update_user_not_found(client):
    with patch("app.routes.api.update_user_in_db", return_value=None):
        response = client.put("/api/users/999", json={"name": "Kasia", "email": "kasia@example.com"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}


def test_delete_user_success(client):
    with patch("app.routes.api.delete_user_from_db", return_value=(1,)):
        response = client.delete("/api/users/1")

    assert response.status_code == 200
    assert response.get_json() == {"message": "User deleted", "id": 1}


def test_delete_user_not_found(client):
    with patch("app.routes.api.delete_user_from_db", return_value=None):
        response = client.delete("/api/users/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}


def test_search_users(client):
    fake_users = [(1, "Anna", "anna@example.com")]

    with patch("app.routes.api.search_users", return_value=fake_users):
        response = client.get("/api/users?q=anna")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "name": "Anna", "email": "anna@example.com"}
    ]


def test_pagination(client):
    from unittest.mock import patch

    fake_users = [(1, "Anna", "anna@example.com")]

    with patch("app.routes.api.get_users_paginated", return_value=(fake_users, 1)):
        response = client.get("/api/users?page=1&limit=10")

    assert response.status_code == 200