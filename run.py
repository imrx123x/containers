import os

from app import create_app
from app.db import wait_for_db

app = create_app()


def should_wait_for_db() -> bool:
    return os.getenv("WAIT_FOR_DB_ON_START", "false").lower() == "true"


if should_wait_for_db():
    wait_for_db()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)