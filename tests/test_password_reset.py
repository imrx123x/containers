from unittest.mock import patch

from app.exceptions import ValidationError


def test_forgot_password_page_get(client):
    response = client.get("/forgot-password")

    assert response.status_code == 200
    assert b"Zapomnia" in response.data


def test_forgot_password_post_success_sends_email_and_redirects(client):
    fake_result = {
        "user": {
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
        },
        "reset_token": "reset-token-123",
    }

    with patch(
        "app.routes.web.request_password_reset_service",
        return_value=fake_result,
    ) as mocked_service, patch(
        "app.routes.web.send_password_reset_email"
    ) as mocked_send_email, patch(
        "app.routes.web.add_audit_log"
    ) as mocked_add_audit_log:
        response = client.post(
            "/forgot-password",
            data={"email": "anna@example.com"},
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    mocked_service.assert_called_once_with("anna@example.com")
    mocked_send_email.assert_called_once()

    send_kwargs = mocked_send_email.call_args.kwargs
    assert send_kwargs["to_email"] == "anna@example.com"
    assert "/reset-password?token=reset-token-123" in send_kwargs["reset_link"]

    mocked_add_audit_log.assert_called_once_with(
        action="request_password_reset",
        actor_id=1,
        actor_email="anna@example.com",
        target_user_id=1,
        target_email="anna@example.com",
        details="Password reset email sent",
    )


def test_forgot_password_post_success_without_user_or_token_does_not_send_email(client):
    fake_result = {
        "user": None,
        "reset_token": None,
    }

    with patch(
        "app.routes.web.request_password_reset_service",
        return_value=fake_result,
    ) as mocked_service, patch(
        "app.routes.web.send_password_reset_email"
    ) as mocked_send_email, patch(
        "app.routes.web.add_audit_log"
    ) as mocked_add_audit_log:
        response = client.post(
            "/forgot-password",
            data={"email": "ghost@example.com"},
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    mocked_service.assert_called_once_with("ghost@example.com")
    mocked_send_email.assert_not_called()
    mocked_add_audit_log.assert_not_called()


def test_forgot_password_post_failure_renders_form_with_400(client):
    with patch(
        "app.routes.web.request_password_reset_service",
        side_effect=ValidationError(
            "Email is required",
            code="email_required",
        ),
    ):
        response = client.post(
            "/forgot-password",
            data={"email": ""},
            follow_redirects=False,
        )

    assert response.status_code == 400
    assert b"Zapomnia" in response.data


def test_reset_password_page_get_without_token(client):
    response = client.get("/reset-password")

    assert response.status_code == 200
    assert b"Reset has" in response.data
    assert b"Brak tokenu resetuj" in response.data


def test_reset_password_page_get_with_token(client):
    response = client.get("/reset-password?token=abc123")

    assert response.status_code == 200
    assert b"Reset has" in response.data
    assert b'value="abc123"' in response.data


def test_reset_password_post_success_redirects_and_adds_audit_log(client):
    fake_result = {
        "message": "Password has been reset successfully",
        "user": {
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
        },
    }

    with patch(
        "app.routes.web.reset_password_with_token_service",
        return_value=fake_result,
    ) as mocked_service, patch(
        "app.routes.web.add_audit_log"
    ) as mocked_add_audit_log:
        response = client.post(
            "/reset-password",
            data={
                "token": "valid-reset-token",
                "new_password": "newpass123",
            },
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    mocked_service.assert_called_once_with(
        token="valid-reset-token",
        new_password="newpass123",
    )

    mocked_add_audit_log.assert_called_once_with(
        action="reset_password",
        actor_id=1,
        actor_email="anna@example.com",
        target_user_id=1,
        target_email="anna@example.com",
        details="Password reset completed via token",
    )


def test_reset_password_post_failure_renders_form_with_400_and_keeps_token(client):
    with patch(
        "app.routes.web.reset_password_with_token_service",
        side_effect=ValidationError(
            "Reset token is invalid or expired",
            code="invalid_reset_token",
        ),
    ):
        response = client.post(
            "/reset-password",
            data={
                "token": "expired-token",
                "new_password": "newpass123",
            },
            follow_redirects=False,
        )

    assert response.status_code == 400
    assert b"Reset has" in response.data
    assert b'value="expired-token"' in response.data