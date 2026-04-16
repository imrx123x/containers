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
        return database_url

    user = os.getenv("DB_USER", "myuser")
    password = os.getenv("DB_PASSWORD", "mypassword")
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("DB_PORT", "5432")
    db = os.getenv("DB_NAME", "mydatabase")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def get_db_connection():
    return psycopg2.connect(**get_db_config())


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255),
            password_hash TEXT,
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        );
    """)

    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS email VARCHAR(255);
    """)

    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS password_hash TEXT;
    """)

    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user';
    """)

    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """)

    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """)

    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;
    """)

    cur.execute("""
        UPDATE users
        SET role = 'user'
        WHERE role IS NULL;
    """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS users_email_unique_idx
        ON users (LOWER(email))
        WHERE email IS NOT NULL AND deleted_at IS NULL;
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            action VARCHAR(100) NOT NULL,
            actor_id INTEGER,
            actor_email VARCHAR(255),
            target_user_id INTEGER,
            target_email VARCHAR(255),
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS actor_id INTEGER;
    """)

    cur.execute("""
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS actor_email VARCHAR(255);
    """)

    cur.execute("""
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS target_user_id INTEGER;
    """)

    cur.execute("""
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS target_email VARCHAR(255);
    """)

    cur.execute("""
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS details TEXT;
    """)

    cur.execute("""
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """)

    conn.commit()
    cur.close()
    conn.close()


def ensure_db_ready():
    if os.getenv("APP_ENV") == "test":
        return
    init_db()


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