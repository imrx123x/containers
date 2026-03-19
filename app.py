from flask import Flask, request, redirect, url_for, render_template
from db import get_db_connection, init_db, wait_for_db

app = Flask(__name__)


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