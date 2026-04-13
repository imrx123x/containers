import os
import pytest

from app import create_app


@pytest.fixture
def app():
    os.environ["APP_ENV"] = "test"
    os.environ["INIT_DB_ON_START"] = "false"

    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"

    return app


@pytest.fixture
def client(app):
    return app.test_client()