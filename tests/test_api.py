from unittest.mock import patch


def test_get_users(client):
    fake_users = [(1, "Anna"), (2, "Jan")]

    with patch("app.routes.api.get_all_users", return_value=fake_users):
        response = client.get("/api/users")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "name": "Anna"},
        {"id": 2, "name": "Jan"},
    ]


def test_get_user_found(client):
    with patch("app.routes.api.get_user_by_id", return_value=(1, "Anna")):
        response = client.get("/api/users/1")

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "name": "Anna"}


def test_get_user_not_found(client):
    with patch("app.routes.api.get_user_by_id", return_value=None):
        response = client.get("/api/users/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}


def test_create_user_success(client):
    with patch("app.routes.api.add_user_to_db", return_value=(1, "Anna")):
        response = client.post("/api/users", json={"name": "Anna"})

    assert response.status_code == 201
    assert response.get_json() == {
        "message": "User created",
        "user": {"id": 1, "name": "Anna"},
    }


def test_create_user_without_name(client):
    response = client.post("/api/users", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Name is required"}


def test_create_user_with_blank_name(client):
    response = client.post("/api/users", json={"name": "   "})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Name is required"}


def test_update_user_success(client):
    with patch("app.routes.api.update_user_in_db", return_value=(1, "Kasia")):
        response = client.put("/api/users/1", json={"name": "Kasia"})

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "User updated",
        "user": {"id": 1, "name": "Kasia"},
    }


def test_update_user_not_found(client):
    with patch("app.routes.api.update_user_in_db", return_value=None):
        response = client.put("/api/users/999", json={"name": "Kasia"})

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