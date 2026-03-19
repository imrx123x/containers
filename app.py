from flask import Flask, request, redirect, url_for, render_template
import os
import psycopg2
import time

app = Flask(__name__)


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


@app.route("/", methods=["GET"])
def home():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM users ORDER BY id;")
    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", users=users)


@app.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name")

    if not name:
        return "Name is required", 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name) VALUES (%s);", (name,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("home"))


@app.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("home"))


@app.route("/users", methods=["GET"])
def list_users():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM users ORDER BY id;")
    users = cur.fetchall()

    cur.close()
    conn.close()

    if not users:
        return "no users in db"

    html = "<h1>Users</h1><ul>"
    for user_id, name in users:
        html += f"<li>{user_id}: {name}</li>"
    html += "</ul>"

    return html


if __name__ == "__main__":
    wait_for_db()
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)