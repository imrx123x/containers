import pytest


from app.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from app.services.auth_service import (
    change_password_service,
    login_user_service,
    register_user_service,
    request_password_reset_service,
    reset_password_with_token_service,
)


def test_register_user_service_success(mocker):
    mocker.patch("app.services.auth_service.validate_user_name", return_value="Anna")
    mocker.patch("app.services.auth_service.normalize_email", return_value="anna@example.com")
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch("app.services.auth_service.get_user_by_email", return_value=None)
    mocker.patch("app.services.auth_service.hash_password", return_value="hashed-password")
    mocker.patch(
        "app.services.auth_service.create_user_service",
        return_value={
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
        },
    )
    mocker.patch("app.services.auth_service.generate_access_token", return_value="access-token")

    result = register_user_service("Anna", "anna@example.com", "supersecret123")

    assert result == {
        "message": "Registration successful",
        "access_token": "access-token",
        "user": {
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": "user",
        },
    }


def test_register_user_service_rejects_invalid_email(mocker):
    mocker.patch("app.services.auth_service.validate_user_name", return_value="Anna")
    mocker.patch("app.services.auth_service.normalize_email", return_value=None)

    with pytest.raises(ValidationError) as exc:
        register_user_service("Anna", "bad-email", "supersecret123")

    assert exc.value.code == "invalid_email"


def test_register_user_service_requires_email(mocker):
    mocker.patch("app.services.auth_service.validate_user_name", return_value="Anna")
    mocker.patch("app.services.auth_service.normalize_email", return_value=None)

    with pytest.raises(ValidationError) as exc:
        register_user_service("Anna", None, "supersecret123")

    assert exc.value.code == "email_required"


def test_register_user_service_requires_strong_password(mocker):
    mocker.patch("app.services.auth_service.validate_user_name", return_value="Anna")
    mocker.patch("app.services.auth_service.normalize_email", return_value="anna@example.com")
    mocker.patch("app.services.auth_service.validate_password", return_value=False)

    with pytest.raises(ValidationError) as exc:
        register_user_service("Anna", "anna@example.com", "123")

    assert exc.value.code == "weak_password"


def test_register_user_service_rejects_existing_email(mocker):
    mocker.patch("app.services.auth_service.validate_user_name", return_value="Anna")
    mocker.patch("app.services.auth_service.normalize_email", return_value="anna@example.com")
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value={"id": 1, "email": "anna@example.com"},
    )

    with pytest.raises(ConflictError) as exc:
        register_user_service("Anna", "anna@example.com", "supersecret123")

    assert exc.value.code == "email_exists"


def test_login_user_service_success(mocker):
    user = {
        "id": 1,
        "name": "Anna",
        "email": "anna@example.com",
        "password_hash": "hashed-password",
        "role": "user",
    }

    mocker.patch("app.services.auth_service.normalize_email", return_value="anna@example.com")
    mocker.patch("app.services.auth_service.get_user_by_email", return_value=user)
    mocker.patch("app.services.auth_service.verify_password", return_value=True)
    mocker.patch("app.services.auth_service.generate_access_token", return_value="login-token")

    result = login_user_service("anna@example.com", "supersecret123")

    assert result == {
        "message": "Login successful",
        "access_token": "login-token",
        "user": user,
    }


def test_login_user_service_rejects_invalid_email(mocker):
    mocker.patch("app.services.auth_service.normalize_email", return_value=None)

    with pytest.raises(UnauthorizedError) as exc:
        login_user_service("bad-email", "whatever123")

    assert exc.value.code == "invalid_credentials"


def test_login_user_service_rejects_missing_user(mocker):
    mocker.patch("app.services.auth_service.normalize_email", return_value="anna@example.com")
    mocker.patch("app.services.auth_service.get_user_by_email", return_value=None)

    with pytest.raises(UnauthorizedError) as exc:
        login_user_service("anna@example.com", "whatever123")

    assert exc.value.code == "invalid_credentials"


def test_login_user_service_rejects_wrong_password(mocker):
    mocker.patch("app.services.auth_service.normalize_email", return_value="anna@example.com")
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value={"id": 1, "email": "anna@example.com", "password_hash": "hashed"},
    )
    mocker.patch("app.services.auth_service.verify_password", return_value=False)

    with pytest.raises(UnauthorizedError) as exc:
        login_user_service("anna@example.com", "wrongpass")

    assert exc.value.code == "invalid_credentials"


def test_change_password_service_success(mocker):
    user = {"id": 1, "email": "anna@example.com"}
    auth_user = {
        "id": 1,
        "email": "anna@example.com",
        "password_hash": "hashed-old",
    }
    updated_user = {
        "id": 1,
        "name": "Anna",
        "email": "anna@example.com",
        "role": "user",
    }

    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch("app.services.auth_service.get_user_by_id", return_value=user)
    mocker.patch("app.services.auth_service.get_user_by_email", return_value=auth_user)

    verify = mocker.patch(
        "app.services.auth_service.verify_password",
        side_effect=[True, False],  # current ok, new != current
    )
    mocker.patch("app.services.auth_service.hash_password", return_value="hashed-new")
    update_mock = mocker.patch(
        "app.services.auth_service.update_user_password_in_db",
        return_value=updated_user,
    )

    result = change_password_service(1, "oldpass123", "newpass123")

    assert result == {
        "message": "Password changed successfully",
        "user": updated_user,
    }
    assert verify.call_count == 2
    update_mock.assert_called_once_with(user_id=1, password_hash="hashed-new")


def test_change_password_service_requires_current_password():
    with pytest.raises(ValidationError) as exc:
        change_password_service(1, "", "newpass123")

    assert exc.value.code == "current_password_required"


def test_change_password_service_requires_strong_new_password(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=False)

    with pytest.raises(ValidationError) as exc:
        change_password_service(1, "oldpass123", "123")

    assert exc.value.code == "weak_new_password"


def test_change_password_service_requires_existing_user(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch("app.services.auth_service.get_user_by_id", return_value=None)

    with pytest.raises(NotFoundError) as exc:
        change_password_service(1, "oldpass123", "newpass123")

    assert exc.value.code == "user_not_found"


def test_change_password_service_rejects_wrong_current_password(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch("app.services.auth_service.get_user_by_id", return_value={"id": 1, "email": "anna@example.com"})
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value={"id": 1, "email": "anna@example.com", "password_hash": "hashed-old"},
    )
    mocker.patch("app.services.auth_service.verify_password", return_value=False)

    with pytest.raises(UnauthorizedError) as exc:
        change_password_service(1, "wrongpass", "newpass123")

    assert exc.value.code == "invalid_current_password"


def test_change_password_service_rejects_same_password(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch("app.services.auth_service.get_user_by_id", return_value={"id": 1, "email": "anna@example.com"})
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value={"id": 1, "email": "anna@example.com", "password_hash": "hashed-old"},
    )
    mocker.patch(
        "app.services.auth_service.verify_password",
        side_effect=[True, True],  # current ok, new same
    )

    with pytest.raises(ValidationError) as exc:
        change_password_service(1, "samepass123", "samepass123")

    assert exc.value.code == "same_password"


def test_request_password_reset_service_success(mocker):
    user = {
        "id": 1,
        "email": "anna@example.com",
        "password_hash": "hashed",
    }

    mocker.patch("app.services.auth_service.normalize_email", return_value="anna@example.com")
    mocker.patch("app.services.auth_service.get_user_by_email", return_value=user)
    mocker.patch("app.services.auth_service.generate_password_reset_token", return_value="reset-token")

    result = request_password_reset_service("anna@example.com")

    assert result == {
        "message": "If the account exists, a password reset email has been sent",
        "user": user,
        "reset_token": "reset-token",
    }


def test_request_password_reset_service_rejects_invalid_email(mocker):
    mocker.patch("app.services.auth_service.normalize_email", return_value=None)

    with pytest.raises(ValidationError) as exc:
        request_password_reset_service("bad-email")

    assert exc.value.code == "invalid_email"


def test_request_password_reset_service_for_missing_user_returns_neutral_response(mocker):
    mocker.patch("app.services.auth_service.normalize_email", return_value="ghost@example.com")
    mocker.patch("app.services.auth_service.get_user_by_email", return_value=None)

    result = request_password_reset_service("ghost@example.com")

    assert result == {
        "message": "If the account exists, a password reset email has been sent",
        "user": None,
        "reset_token": None,
    }


def test_reset_password_with_token_service_success(mocker):
    payload = {"sub": 1, "email": "anna@example.com", "purpose": "password-reset"}
    user = {"id": 1, "email": "anna@example.com"}
    auth_user = {"id": 1, "email": "anna@example.com", "password_hash": "hashed-old"}
    updated_user = {"id": 1, "name": "Anna", "email": "anna@example.com", "role": "user"}

    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch("app.services.auth_service.decode_password_reset_token", return_value=payload)
    mocker.patch("app.services.auth_service.get_user_by_id", return_value=user)
    mocker.patch("app.services.auth_service.get_user_by_email", return_value=auth_user)
    mocker.patch("app.services.auth_service.verify_password", return_value=False)
    mocker.patch("app.services.auth_service.hash_password", return_value="hashed-new")
    update_mock = mocker.patch(
        "app.services.auth_service.update_user_password_in_db",
        return_value=updated_user,
    )

    result = reset_password_with_token_service("valid-token", "newpass123")

    assert result == {
        "message": "Password has been reset successfully",
        "user": updated_user,
    }
    update_mock.assert_called_once_with(user_id=1, password_hash="hashed-new")


def test_reset_password_with_token_service_requires_token():
    with pytest.raises(ValidationError) as exc:
        reset_password_with_token_service("", "newpass123")

    assert exc.value.code == "reset_token_required"


def test_reset_password_with_token_service_requires_strong_password(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=False)

    with pytest.raises(ValidationError) as exc:
        reset_password_with_token_service("token", "123")

    assert exc.value.code == "weak_new_password"


def test_reset_password_with_token_service_rejects_invalid_token(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch("app.services.auth_service.decode_password_reset_token", return_value=None)

    with pytest.raises(UnauthorizedError) as exc:
        reset_password_with_token_service("bad-token", "newpass123")

    assert exc.value.code == "invalid_reset_token"


def test_reset_password_with_token_service_rejects_token_with_missing_fields(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch("app.services.auth_service.decode_password_reset_token", return_value={"sub": None, "email": None})

    with pytest.raises(UnauthorizedError) as exc:
        reset_password_with_token_service("bad-token", "newpass123")

    assert exc.value.code == "invalid_reset_token"


def test_reset_password_with_token_service_rejects_missing_user(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch(
        "app.services.auth_service.decode_password_reset_token",
        return_value={"sub": 1, "email": "anna@example.com"},
    )
    mocker.patch("app.services.auth_service.get_user_by_id", return_value=None)

    with pytest.raises(NotFoundError) as exc:
        reset_password_with_token_service("token", "newpass123")

    assert exc.value.code == "user_not_found"


def test_reset_password_with_token_service_rejects_email_user_id_mismatch(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch(
        "app.services.auth_service.decode_password_reset_token",
        return_value={"sub": 1, "email": "anna@example.com"},
    )
    mocker.patch("app.services.auth_service.get_user_by_id", return_value={"id": 1, "email": "anna@example.com"})
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value={"id": 999, "email": "anna@example.com", "password_hash": "hashed"},
    )

    with pytest.raises(UnauthorizedError) as exc:
        reset_password_with_token_service("token", "newpass123")

    assert exc.value.code == "invalid_reset_token"


def test_reset_password_with_token_service_rejects_same_password(mocker):
    mocker.patch("app.services.auth_service.validate_password", return_value=True)
    mocker.patch(
        "app.services.auth_service.decode_password_reset_token",
        return_value={"sub": 1, "email": "anna@example.com"},
    )
    mocker.patch("app.services.auth_service.get_user_by_id", return_value={"id": 1, "email": "anna@example.com"})
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value={"id": 1, "email": "anna@example.com", "password_hash": "hashed"},
    )
    mocker.patch("app.services.auth_service.verify_password", return_value=True)

    with pytest.raises(ValidationError) as exc:
        reset_password_with_token_service("token", "samepass123")

    assert exc.value.code == "same_password"