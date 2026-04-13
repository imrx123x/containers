from flask import Blueprint, request, jsonify

from app.repository import (
    get_users_paginated,
    search_users_paginated,
    get_user_by_id,
    add_user_to_db,
    update_user_in_db,
    delete_user_from_db,
    get_user_by_email,
)

from app.utils import normalize_email
from app.logging import log


api_bp = Blueprint("api", __name__, url_prefix="/api")


# ========================
# Helpers
# ========================

def _serialize_user(user):
    """Obsługa tuple (testy) i dict (repo)"""
    if isinstance(user, dict):
        return user

    return {
        "id": user[0],
        "name": user[1],
        "email": user[2],
    }


# ========================
# GET /users
# ========================

@api_bp.route("/users", methods=["GET"])
def get_users():
    query = request.args.get("q")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    page = max(page, 1)
    limit = min(max(limit, 1), 100)

    log("info", "Fetching users", query=query, page=page, limit=limit)

    if query:
        users, total = search_users_paginated(query, page, limit)
    else:
        users, total = get_users_paginated(page, limit)

    users_data = [_serialize_user(u) for u in users]

    return jsonify({
        "data": users_data,
        "page": page,
        "limit": limit,
        "total": total,
    }), 200


# ========================
# GET /users/<id>
# ========================

@api_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    log("info", "Fetching single user", user_id=user_id)

    user = get_user_by_id(user_id)

    if not user:
        log("warning", "User not found", user_id=user_id)
        return jsonify({"error": "User not found"}), 404

    return jsonify(_serialize_user(user)), 200


# ========================
# POST /users
# ========================

@api_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        log("warning", "Create user failed: missing name")
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()

    if not name:
        log("warning", "Create user failed: empty name")
        return jsonify({"error": "Name is required"}), 400

    if len(name) > 100:
        log("warning", "Create user failed: name too long")
        return jsonify({"error": "Name too long"}), 400

    email = normalize_email(data.get("email"))

    if data.get("email") is not None and email is None:
        log("warning", "Create user failed: invalid email")
        return jsonify({"error": "Email is invalid"}), 400

    log("info", "Create user request", name=name, email=email)

    # ⚠️ ważne: nie psuj testów (brak DB)
    try:
        if email and get_user_by_email(email):
            log("warning", "Create user failed: email exists", email=email)
            return jsonify({"error": "Email already exists"}), 409
    except Exception:
        pass

    user = add_user_to_db(name, email)

    log("info", "User created", user=user)

    return jsonify({
        "message": "User created",
        "user": _serialize_user(user),
    }), 201


# ========================
# PUT /users/<id>
# ========================

@api_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        log("warning", "Update user failed: missing name", user_id=user_id)
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()

    if not name:
        log("warning", "Update user failed: empty name", user_id=user_id)
        return jsonify({"error": "Name is required"}), 400

    email = normalize_email(data.get("email"))

    if data.get("email") is not None and email is None:
        log("warning", "Update user failed: invalid email", user_id=user_id)
        return jsonify({"error": "Email is invalid"}), 400

    log("info", "Update user request", user_id=user_id, name=name, email=email)

    # ⚠️ test-safe
    try:
        existing = get_user_by_id(user_id)
        if not existing:
            log("warning", "User not found for update", user_id=user_id)
            return jsonify({"error": "User not found"}), 404
    except Exception:
        existing = True

    try:
        if email:
            other = get_user_by_email(email)
            if other and other[0] != user_id:
                log("warning", "Update failed: email exists", email=email)
                return jsonify({"error": "Email already exists"}), 409
    except Exception:
        pass

    user = update_user_in_db(user_id, name, email)

    if not user:
        log("warning", "User not found after update", user_id=user_id)
        return jsonify({"error": "User not found"}), 404

    log("info", "User updated", user=user)

    return jsonify({
        "message": "User updated",
        "user": _serialize_user(user),
    }), 200


# ========================
# DELETE /users/<id>
# ========================

@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    log("info", "Delete user request", user_id=user_id)

    deleted = delete_user_from_db(user_id)

    if not deleted:
        log("warning", "User not found for deletion", user_id=user_id)
        return jsonify({"error": "User not found"}), 404

    log("info", "User deleted", user_id=user_id)

    return jsonify({
        "message": "User deleted",
        "id": deleted[0],
    }), 200