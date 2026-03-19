import os
import time
import psycopg2


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "mydatabase"),
        user=os.getenv("DB_USER", "myuser"),
        password=os.getenv("DB_PASSWORD", "mypassword"),
    )


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


def wait_for_db():
    for i in range(10):
        try:
            conn = get_db_connection()
            conn.close()
            print("Database is ready")
            return
        except psycopg2.OperationalError:
            print(f"Database not ready yet, retrying... ({i + 1}/10)")
            time.sleep(2)

    raise Exception("Database is not available")