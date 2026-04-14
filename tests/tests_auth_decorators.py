from flask import Blueprint, jsonify

from app import create_app


def build_app():
    app = create_app()
    app.config["TESTING"] = False
    app.config["SECRET_KEY"] = "test-secret"

    from app.auth import admin_required, auth_required

    test_bp = Blueprint("test_auth_decorators", __name__)

    @test_bp.route("/test/protected", methods=["GET"])
    @auth_required
    def protected():
        return jsonify({"message": "ok"}), 200

    @test_bp.route("/test/admin-only", methods=["GET"])
    @admin_required
    def admin_only():
        return jsonify({"message": "ok"}), 200

    app.register_blueprint(test_bp)
    return app


def test_auth_required_returns_401_when_missing_bearer_token():
    app = build_app()
    client = app.test_client()

    response = client.get("/test/protected")

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Missing bearer token",
        "code": "missing_bearer_token",
    }


def test_auth_required_returns_401_when_token_is_invalid():
    app = build_app()
    client = app.test_client()

    response = client.get(
        "/test/protected",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid or expired token",
        "code": "invalid_or_expired_token",
    }


def test_auth_required_returns_401_when_user_from_token_does_not_exist():
    app = build_app()
    client = app.test_client()

    from app.utils import generate_access_token

    with app.app_context():
        token = generate_access_token(
            {
                "id": 999,
                "email": "ghost@example.com",
                "role": "user",
            }
        )

    response = client.get(
        "/test/protected",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "User not found",
        "code": "user_not_found",
    }


def test_auth_required_returns_200_for_valid_user_token(mocker):
    app = build_app()
    client = app.test_client()

    from app.utils import generate_access_token

    with app.app_context():
        token = generate_access_token(
            {
                "id": 1,
                "email": "anna@example.com",
                "role": "user",
            }
        )

    mocker.patch(
        "app.auth.get_user_by_id",
        return_value={
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
        },
    )

    response = client.get(
        "/test/protected",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "ok"}


def test_admin_required_returns_401_when_missing_bearer_token():
    app = build_app()
    client = app.test_client()

    response = client.get("/test/admin-only")

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Missing bearer token",
        "code": "missing_bearer_token",
    }


def test_admin_required_returns_403_for_non_admin_user(mocker):
    app = build_app()
    client = app.test_client()

    from app.utils import generate_access_token

    with app.app_context():
        token = generate_access_token(
            {
                "id": 2,
                "email": "user@example.com",
                "role": "user",
            }
        )

    mocker.patch(
        "app.auth.get_user_by_id",
        return_value={
            "id": 2,
            "name": "Regular User",
            "email": "user@example.com",
            "role": "user",
        },
    )

    response = client.get(
        "/test/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "Forbidden",
        "code": "forbidden",
    }


def test_admin_required_returns_200_for_admin_user(mocker):
    app = build_app()
    client = app.test_client()

    from app.utils import generate_access_token

    with app.app_context():
        token = generate_access_token(
            {
                "id": 3,
                "email": "admin@example.com",
                "role": "admin",
            }
        )

    mocker.patch(
        "app.auth.get_user_by_id",
        return_value={
            "id": 3,
            "name": "Admin",
            "email": "admin@example.com",
            "role": "admin",
        },
    )

    response = client.get(
        "/test/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "ok"}


def test_admin_required_returns_401_when_token_valid_but_user_missing():
    app = build_app()
    client = app.test_client()

    from app.utils import generate_access_token

    with app.app_context():
        token = generate_access_token(
            {
                "id": 404,
                "email": "missing@example.com",
                "role": "admin",
            }
        )

    response = client.get(
        "/test/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "User not found",
        "code": "user_not_found",
    }


def test_auth_required_rejects_wrong_authorization_scheme():
    app = build_app()
    client = app.test_client()

    response = client.get(
        "/test/protected",
        headers={"Authorization": "Basic abc123"},
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Missing bearer token",
        "code": "missing_bearer_token",
    }