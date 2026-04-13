import os
import time
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


def get_db_connection():
    return psycopg2.connect(**get_db_config())


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def wait_for_db(max_retries: int = 10, delay_seconds: int = 2):
    for i in range(max_retries):
        try:
            conn = get_db_connection()
            conn.close()
            print("Database is ready")
            return
        except psycopg2.OperationalError:
            print(f"Database not ready yet, retrying... ({i + 1}/{max_retries})")
            time.sleep(delay_seconds)

    raise Exception("Database is not available")


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