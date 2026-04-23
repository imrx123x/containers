from app.utils import (
    decode_access_token,
    decode_password_reset_token,
    extract_bearer_token,
    generate_access_token,
    generate_password_reset_token,
    hash_password,
    normalize_email,
    validate_password,
    verify_password,
)


def test_normalize_email_returns_lowercased_trimmed_email():
    assert normalize_email("  ANNA@EXAMPLE.COM  ") == "anna@example.com"


def test_normalize_email_returns_none_for_none():
    assert normalize_email(None) is None


def test_normalize_email_returns_none_for_blank_string():
    assert normalize_email("   ") is None


def test_normalize_email_returns_none_for_invalid_email_without_at():
    assert normalize_email("annaexample.com") is None


def test_normalize_email_returns_none_for_invalid_email_without_domain():
    assert normalize_email("anna@") is None


def test_normalize_email_returns_none_for_too_long_email():
    too_long_local = "a" * 250
    email = f"{too_long_local}@x.com"
    assert len(email) > 255
    assert normalize_email(email) is None


def test_hash_password_and_verify_password_success():
    password = "supersecret123"
    password_hash = hash_password(password)

    assert isinstance(password_hash, str)
    assert password_hash != password
    assert verify_password(password_hash, password) is True


def test_verify_password_returns_false_for_wrong_password():
    password_hash = hash_password("supersecret123")

    assert verify_password(password_hash, "wrong-password") is False


def test_verify_password_returns_false_when_hash_is_missing():
    assert verify_password("", "whatever123") is False
    assert verify_password(None, "whatever123") is False


def test_validate_password_accepts_password_with_minimum_length():
    assert validate_password("12345678") is True


def test_validate_password_rejects_short_password():
    assert validate_password("1234567") is False


def test_validate_password_rejects_non_string():
    assert validate_password(None) is False
    assert validate_password(12345678) is False


def test_extract_bearer_token_success():
    token = extract_bearer_token("Bearer abc.def.ghi")
    assert token == "abc.def.ghi"


def test_extract_bearer_token_accepts_lowercase_scheme():
    token = extract_bearer_token("bearer my-token")
    assert token == "my-token"


def test_extract_bearer_token_returns_none_for_missing_header():
    assert extract_bearer_token(None) is None


def test_extract_bearer_token_returns_none_for_wrong_scheme():
    assert extract_bearer_token("Basic abc123") is None


def test_extract_bearer_token_returns_none_for_invalid_header_shape():
    assert extract_bearer_token("Bearer") is None
    assert extract_bearer_token("Bearer too many parts here") is None


def test_access_token_roundtrip(app):
    user = {
        "id": 123,
        "email": "anna@example.com",
        "role": "admin",
        "token_version": 3,
    }

    with app.app_context():
        token = generate_access_token(user)
        payload = decode_access_token(token)

    assert isinstance(token, str)
    assert payload["sub"] == 123
    assert payload["email"] == "anna@example.com"
    assert payload["role"] == "admin"
    assert payload["token_version"] == 3


def test_decode_access_token_returns_none_for_invalid_token(app):
    with app.app_context():
        payload = decode_access_token("definitely-invalid-token")

    assert payload is None


def test_password_reset_token_roundtrip(app):
    user = {
        "id": 55,
        "email": "reset@example.com",
        "role": "user",
    }

    with app.app_context():
        token = generate_password_reset_token(user)
        payload = decode_password_reset_token(token)

    assert isinstance(token, str)
    assert payload["sub"] == 55
    assert payload["email"] == "reset@example.com"
    assert payload["purpose"] == "password-reset"


def test_decode_password_reset_token_returns_none_for_invalid_token(app):
    with app.app_context():
        payload = decode_password_reset_token("totally-invalid-reset-token")

    assert payload is None


def test_decode_password_reset_token_rejects_access_token(app):
    user = {
        "id": 9,
        "email": "anna@example.com",
        "role": "user",
    }

    with app.app_context():
        access_token = generate_access_token(user)
        payload = decode_password_reset_token(access_token)

    assert payload is None


def test_decode_access_token_rejects_password_reset_token(app):
    user = {
        "id": 9,
        "email": "anna@example.com",
        "role": "user",
    }

    with app.app_context():
        reset_token = generate_password_reset_token(user)
        payload = decode_access_token(reset_token)

    assert payload is None