import os
from flask import Flask, request, redirect, url_for, render_template, flash, jsonify
from db import init_db, wait_for_db
from repository import (
    get_all_users,
    add_user_to_db,
    update_user_in_db,
    delete_user_from_db,
    get_user_by_id,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")


@app.route("/", methods=["GET"])
def home():
    users = get_all_users()
    return render_template("index.html", users=users)


@app.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name", "").strip()

    if not name:
        flash("Name is required", "error")
        return redirect(url_for("home"))

    if len(name) > 100:
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("home"))

    try:
        add_user_to_db(name)
        flash("User added successfully", "success")
    except Exception:
        flash("Database error while adding user", "error")

    return redirect(url_for("home"))


@app.route("/edit-user/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    name = request.form.get("name", "").strip()

    if not name:
        flash("Name is required", "error")
        return redirect(url_for("home"))

    if len(name) > 100:
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("home"))

    try:
        update_user_in_db(user_id, name)
        flash("User updated successfully", "success")
    except Exception:
        flash("Database error while updating user", "error")

    return redirect(url_for("home"))


@app.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    try:
        delete_user_from_db(user_id)
        flash("User deleted successfully", "success")
    except Exception:
        flash("Database error while deleting user", "error")

    return redirect(url_for("home"))


@app.route("/users", methods=["GET"])
def list_users():
    users = get_all_users()
    users_data = [{"id": user_id, "name": name} for user_id, name in users]
    return jsonify(users_data)

#------- API -----
@app.route("/api/users", methods=["GET"])
def api_get_users():
    users = get_all_users()
    users_data = [{"id": user_id, "name": name} for user_id, name in users]
    return jsonify(users_data), 200

@app.route("/api/users", methods=["POST"])
def api_create_user():
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if len(name) > 100:
        return jsonify({"error": "Name too long"}), 400

    try:
        add_user_to_db(name)
        return jsonify({"message": "User created"}), 201
    except Exception:
        return jsonify({"error": "Database error"}), 500

@app.route("/api/users/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    user = get_user_by_id(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {"id": user[0], "name": user[1]}
    return jsonify(user_data), 200

@app.route("/api/users/<int:user_id>", methods=["PUT"])
def api_update_user(user_id):
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if len(name) > 100:
        return jsonify({"error": "Name too long"}), 400

    if not get_user_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    try:
        update_user_in_db(user_id, name)
        return jsonify({"message": "User updated"}), 200
    except Exception:
        return jsonify({"error": "Database error"}), 500

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    if not get_user_by_id(user_id):
        return jsonify({"error": "User not found"}), 404

    try:
        delete_user_from_db(user_id)
        return jsonify({"message": "User deleted"}), 200
    except Exception:
        return jsonify({"error": "Database error"}), 500

if __name__ == "__main__":
    wait_for_db()
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)