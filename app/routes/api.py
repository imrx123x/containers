from flask import Blueprint, request, jsonify
from app.repository import (
    get_all_users,
    get_user_by_id,
    add_user_to_db,
    update_user_in_db,
    delete_user_from_db,
    search_users,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def normalize_email(email_value):
    if email_value is None:
        return None

    email = email_value.strip().lower()

    if not email:
        return None

    if "@" not in email or "." not in email.split("@")[-1]:
        return None

    if len(email) > 255:
        return None

    return email


@api_bp.route("/users", methods=["GET"])
def get_users():
    query = request.args.get("q")

    if query:
        users = search_users(query)
    else:
        users = get_all_users()

    users_data = [
        {"id": user_id, "name": name, "email": email}
        for user_id, name, email in users
    ]

    return jsonify(users_data), 200


@api_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = get_user_by_id(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user[0], "name": user[1], "email": user[2]}), 200


@api_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if len(name) > 100:
        return jsonify({"error": "Name must be at most 100 characters"}), 400

    email = normalize_email(data.get("email"))

    if data.get("email") is not None and email is None:
        return jsonify({"error": "Email is invalid"}), 400

    try:
        user = add_user_to_db(name, email)
        return jsonify({
            "message": "User created",
            "user": {"id": user[0], "name": user[1], "email": user[2]}
        }), 201
    except Exception:
        return jsonify({"error": "Database error"}), 500


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if len(name) > 100:
        return jsonify({"error": "Name must be at most 100 characters"}), 400

    email = normalize_email(data.get("email"))

    if data.get("email") is not None and email is None:
        return jsonify({"error": "Email is invalid"}), 400

    try:
        updated_user = update_user_in_db(user_id, name, email)

        if not updated_user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "message": "User updated",
            "user": {"id": updated_user[0], "name": updated_user[1], "email": updated_user[2]}
        }), 200
    except Exception:
        return jsonify({"error": "Database error"}), 500


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        deleted_user = delete_user_from_db(user_id)

        if not deleted_user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User deleted", "id": deleted_user[0]}), 200
    except Exception:
        return jsonify({"error": "Database error"}), 500
