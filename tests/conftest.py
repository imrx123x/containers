import os
import pytest

from app import create_app


@pytest.fixture
def app():
    os.environ["APP_ENV"] = "test"
    os.environ["WAIT_FOR_DB_ON_START"] = "false"

    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"

    return app


@pytest.fixture(autouse=True)
def reset_rate_limit_storage():
    from app.utils_rate_limit import _RATE_LIMIT_STORAGE
    _RATE_LIMIT_STORAGE.clear()


@pytest.fixture
def client(app):
    return app.test_client()