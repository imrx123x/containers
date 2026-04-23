from flask import Blueprint, jsonify

from app import create_app


def build_app():
    app = create_app()
    app.config["TESTING"] = False
    app.config["SECRET_KEY"] = "test-secret"

    from app.auth import auth_required

    test_bp = Blueprint("test_token_lifecycle", __name__)

    @test_bp.route("/test/token-lifecycle", methods=["GET"])
    @auth_required
    def token_lifecycle_route():
        return jsonify({"message": "ok"}), 200

    app.register_blueprint(test_bp)
    return app


def test_old_token_becomes_invalid_when_token_version_changes(mocker):
    app = build_app()
    client = app.test_client()

    from app.utils import generate_access_token

    with app.app_context():
        token = generate_access_token(
            {
                "id": 1,
                "email": "anna@example.com",
                "role": "user",
                "token_version": 0,
            }
        )

    mocker.patch(
        "app.auth.get_user_by_id",
        return_value={
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
            "token_version": 1,
        },
    )

    response = client.get(
        "/test/token-lifecycle",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid or expired token",
        "code": "invalid_or_expired_token",
    }


def test_current_token_is_valid_when_token_version_matches(mocker):
    app = build_app()
    client = app.test_client()

    from app.utils import generate_access_token

    with app.app_context():
        token = generate_access_token(
            {
                "id": 1,
                "email": "anna@example.com",
                "role": "user",
                "token_version": 2,
            }
        )

    mocker.patch(
        "app.auth.get_user_by_id",
        return_value={
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
            "token_version": 2,
        },
    )

    response = client.get(
        "/test/token-lifecycle",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "ok"}