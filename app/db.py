import os
from urllib.parse import urlparse

import psycopg2


def parse_database_url(database_url: str) -> dict:
    parsed = urlparse(database_url)
    return {
        "host": parsed.hostname,
        "database": parsed.path.lstrip("/"),
        "user": parsed.username,
        "password": parsed.password,
        "port": parsed.port or 5432,
        "sslmode": "require" if parsed.hostname and "render.com" in parsed.hostname else "prefer",
    }


def get_db_config():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return parse_database_url(database_url)

    return {
        "host": os.getenv("DB_HOST", "db"),
        "database": os.getenv("DB_NAME", "mydatabase"),
        "user": os.getenv("DB_USER", "myuser"),
        "password": os.getenv("DB_PASSWORD", "mypassword"),
        "port": os.getenv("DB_PORT", "5432"),
    }


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        if database_url.startswith("postgresql://"):
            return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return database_url

    user = os.getenv("DB_USER", "myuser")
    password = os.getenv("DB_PASSWORD", "mypassword")
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("DB_PORT", "5432")
    db = os.getenv("DB_NAME", "mydatabase")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def get_db_connection():
    return psycopg2.connect(**get_db_config())


def check_db_health() -> bool:
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False