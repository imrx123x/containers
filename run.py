import os

from app import create_app
from app.db import init_db, wait_for_db

app = create_app()


def should_init_db() -> bool:
    """
    Pozwala sterować inicjalizacją bazy przez env.
    Domyślnie włączone, ale można wyłączyć np. w testach.
    """
    return os.getenv("INIT_DB_ON_START", "true").lower() == "true"


if should_init_db():
    wait_for_db()
    init_db()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)