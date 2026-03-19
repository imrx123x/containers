from flask import Flask
import os
import psycopg2

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "mydatabase"),
        user=os.getenv("DB_USER", "myuser"),
        password=os.getenv("DB_PASSWORD", "mypassword"),
    )


@app.route("/")
def hello():
    return "flask + psql"


@app.route("/db")
def test_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"connected with db: {db_version}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)