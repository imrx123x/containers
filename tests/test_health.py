from unittest.mock import patch


def test_health_ok(client):
    with patch("app.routes.web.check_db_health", return_value=True):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "database": "up",
    }


def test_health_db_down(client):
    with patch("app.routes.web.check_db_health", return_value=False):
        response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json() == {
        "status": "degraded",
        "database": "down",
    }