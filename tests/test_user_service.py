import pytest

from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.services.user_service import (
    create_user_service,
    delete_user_service,
    get_user_by_id_service,
    get_users_service,
    update_current_user_service,
    update_user_service,
    validate_user_email,
    validate_user_name,
)


def test_validate_user_name_success():
    assert validate_user_name("  Anna  ") == "Anna"


def test_validate_user_name_requires_value():
    with pytest.raises(ValidationError) as exc:
        validate_user_name("   ")

    assert exc.value.code == "name_required"


def test_validate_user_name_rejects_too_long():
    with pytest.raises(ValidationError) as exc:
        validate_user_name("a" * 101)

    assert exc.value.code == "name_too_long"


def test_validate_user_email_success(mocker):
    mocker.patch("app.services.user_service.normalize_email", return_value="anna@example.com")

    assert validate_user_email("anna@example.com") == "anna@example.com"


def test_validate_user_email_allows_none(mocker):
    mocker.patch("app.services.user_service.normalize_email", return_value=None)

    assert validate_user_email(None) is None


def test_validate_user_email_rejects_invalid_value(mocker):
    mocker.patch("app.services.user_service.normalize_email", return_value=None)

    with pytest.raises(ValidationError) as exc:
        validate_user_email("bad-email")

    assert exc.value.code == "invalid_email"


def test_get_users_service_with_query(mocker):
    search_mock = mocker.patch(
        "app.services.user_service.search_users_paginated",
        return_value=(["u1"], 1),
    )

    result = get_users_service("anna", 2, 5)

    assert result == (["u1"], 1)
    search_mock.assert_called_once_with("anna", 2, 5)


def test_get_users_service_without_query(mocker):
    list_mock = mocker.patch(
        "app.services.user_service.get_users_paginated",
        return_value=(["u1"], 1),
    )

    result = get_users_service(None, 1, 10)

    assert result == (["u1"], 1)
    list_mock.assert_called_once_with(1, 10)


def test_get_user_by_id_service_success(mocker):
    mocker.patch(
        "app.services.user_service.get_user_by_id",
        return_value={"id": 1, "name": "Anna"},
    )

    result = get_user_by_id_service(1)

    assert result == {"id": 1, "name": "Anna"}


def test_get_user_by_id_service_not_found(mocker):
    mocker.patch("app.services.user_service.get_user_by_id", return_value=None)

    with pytest.raises(NotFoundError) as exc:
        get_user_by_id_service(999)

    assert exc.value.code == "user_not_found"


def test_create_user_service_success(mocker):
    mocker.patch("app.services.user_service.validate_user_name", return_value="Anna")
    mocker.patch("app.services.user_service.validate_user_email", return_value="anna@example.com")
    mocker.patch("app.services.user_service.get_user_by_email", return_value=None)
    add_mock = mocker.patch(
        "app.services.user_service.add_user_to_db",
        return_value={"id": 1, "name": "Anna", "email": "anna@example.com", "role": "user"},
    )

    result = create_user_service("Anna", "anna@example.com")

    assert result == {"id": 1, "name": "Anna", "email": "anna@example.com", "role": "user"}
    add_mock.assert_called_once_with(
        name="Anna",
        email="anna@example.com",
        password_hash=None,
        role="user",
    )


def test_create_user_service_without_email_success(mocker):
    mocker.patch("app.services.user_service.validate_user_name", return_value="Anna")
    mocker.patch("app.services.user_service.validate_user_email", return_value=None)
    add_mock = mocker.patch(
        "app.services.user_service.add_user_to_db",
        return_value={"id": 1, "name": "Anna", "email": None, "role": "user"},
    )

    result = create_user_service("Anna", None)

    assert result["email"] is None
    add_mock.assert_called_once_with(
        name="Anna",
        email=None,
        password_hash=None,
        role="user",
    )


def test_create_user_service_rejects_existing_email(mocker):
    mocker.patch("app.services.user_service.validate_user_name", return_value="Anna")
    mocker.patch("app.services.user_service.validate_user_email", return_value="anna@example.com")
    mocker.patch(
        "app.services.user_service.get_user_by_email",
        return_value={"id": 5, "email": "anna@example.com"},
    )

    with pytest.raises(ConflictError) as exc:
        create_user_service("Anna", "anna@example.com")

    assert exc.value.code == "email_exists"


def test_update_user_service_success(mocker):
    mocker.patch("app.services.user_service.validate_user_name", return_value="Kasia")
    mocker.patch("app.services.user_service.validate_user_email", return_value="kasia@example.com")
    mocker.patch(
        "app.services.user_service.get_user_by_id",
        return_value={"id": 1, "name": "Anna", "email": "anna@example.com"},
    )
    mocker.patch(
        "app.services.user_service.get_user_by_email",
        return_value=None,
    )
    update_mock = mocker.patch(
        "app.services.user_service.update_user_in_db",
        return_value={"id": 1, "name": "Kasia", "email": "kasia@example.com", "role": "user"},
    )

    result = update_user_service(1, "Kasia", "kasia@example.com")

    assert result["name"] == "Kasia"
    update_mock.assert_called_once_with(
        user_id=1,
        name="Kasia",
        email="kasia@example.com",
    )


def test_update_user_service_rejects_missing_user(mocker):
    mocker.patch("app.services.user_service.validate_user_name", return_value="Kasia")
    mocker.patch("app.services.user_service.validate_user_email", return_value="kasia@example.com")
    mocker.patch("app.services.user_service.get_user_by_id", return_value=None)

    with pytest.raises(NotFoundError) as exc:
        update_user_service(999, "Kasia", "kasia@example.com")

    assert exc.value.code == "user_not_found"


def test_update_user_service_rejects_email_of_other_user(mocker):
    mocker.patch("app.services.user_service.validate_user_name", return_value="Kasia")
    mocker.patch("app.services.user_service.validate_user_email", return_value="anna@example.com")
    mocker.patch(
        "app.services.user_service.get_user_by_id",
        return_value={"id": 1, "name": "Kasia", "email": "kasia@example.com"},
    )
    mocker.patch(
        "app.services.user_service.get_user_by_email",
        return_value={"id": 2, "email": "anna@example.com"},
    )

    with pytest.raises(ConflictError) as exc:
        update_user_service(1, "Kasia", "anna@example.com")

    assert exc.value.code == "email_exists"


def test_update_current_user_service_success_name_only(mocker):
    mocker.patch(
        "app.services.user_service.get_user_by_id",
        return_value={"id": 1, "name": "Anna", "email": "anna@example.com"},
    )
    mocker.patch("app.services.user_service.validate_user_name", return_value="Updated Anna")
    update_mock = mocker.patch(
        "app.services.user_service.update_user_in_db",
        return_value={"id": 1, "name": "Updated Anna", "email": "anna@example.com", "role": "user"},
    )

    result = update_current_user_service(1, name="Updated Anna")

    assert result["name"] == "Updated Anna"
    update_mock.assert_called_once_with(
        user_id=1,
        name="Updated Anna",
        email="anna@example.com",
    )


def test_update_current_user_service_success_email_only(mocker):
    mocker.patch(
        "app.services.user_service.get_user_by_id",
        return_value={"id": 1, "name": "Anna", "email": "anna@example.com"},
    )
    mocker.patch("app.services.user_service.validate_user_email", return_value="updated@example.com")
    mocker.patch("app.services.user_service.get_user_by_email", return_value=None)
    update_mock = mocker.patch(
        "app.services.user_service.update_user_in_db",
        return_value={"id": 1, "name": "Anna", "email": "updated@example.com", "role": "user"},
    )

    result = update_current_user_service(1, raw_email="updated@example.com")

    assert result["email"] == "updated@example.com"
    update_mock.assert_called_once_with(
        user_id=1,
        name="Anna",
        email="updated@example.com",
    )


def test_update_current_user_service_requires_at_least_one_field(mocker):
    mocker.patch(
        "app.services.user_service.get_user_by_id",
        return_value={"id": 1, "name": "Anna", "email": "anna@example.com"},
    )

    with pytest.raises(ValidationError) as exc:
        update_current_user_service(1)

    assert exc.value.code == "no_fields_to_update"


def test_update_current_user_service_rejects_missing_user(mocker):
    mocker.patch("app.services.user_service.get_user_by_id", return_value=None)

    with pytest.raises(NotFoundError) as exc:
        update_current_user_service(999, name="Updated")

    assert exc.value.code == "user_not_found"


def test_update_current_user_service_rejects_email_of_other_user(mocker):
    mocker.patch(
        "app.services.user_service.get_user_by_id",
        return_value={"id": 1, "name": "Anna", "email": "anna@example.com"},
    )
    mocker.patch("app.services.user_service.validate_user_email", return_value="taken@example.com")
    mocker.patch(
        "app.services.user_service.get_user_by_email",
        return_value={"id": 2, "email": "taken@example.com"},
    )

    with pytest.raises(ConflictError) as exc:
        update_current_user_service(1, raw_email="taken@example.com")

    assert exc.value.code == "email_exists"


def test_delete_user_service_success(mocker):
    mocker.patch(
        "app.services.user_service.delete_user_from_db",
        return_value={"id": 1, "name": "Anna"},
    )

    result = delete_user_service(1)

    assert result == {"id": 1, "name": "Anna"}


def test_delete_user_service_not_found(mocker):
    mocker.patch("app.services.user_service.delete_user_from_db", return_value=None)

    with pytest.raises(NotFoundError) as exc:
        delete_user_service(999)

    assert exc.value.code == "user_not_found"