from flask import Blueprint, jsonify, request

from app.auth import admin_required, auth_required
from app.logging import log
from app.services.user_service import (
    create_user_service,
    delete_user_service,
    get_user_by_id_service,
    get_users_service,
    update_user_service,
)


api_bp = Blueprint("api", __name__, url_prefix="/api")


def _serialize_user(user):
    if isinstance(user, dict):
        return {
            "id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
            "created_at": user.get("created_at"),
            "updated_at": user.get("updated_at"),
        }

    return {
        "id": user[0],
        "name": user[1],
        "email": user[2],
    }


@api_bp.route("/users", methods=["GET"])
@auth_required
def get_users():
    query = request.args.get("q")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    page = max(page, 1)
    limit = min(max(limit, 1), 100)

    log("info", "Fetching users", query=query, page=page, limit=limit)

    users, total = get_users_service(query=query, page=page, limit=limit)
    users_data = [_serialize_user(user) for user in users]

    return jsonify(
        {
            "data": users_data,
            "page": page,
            "limit": limit,
            "total": total,
        }
    ), 200


@api_bp.route("/users/<int:user_id>", methods=["GET"])
@auth_required
def get_user(user_id):
    log("info", "Fetching single user", user_id=user_id)

    user = get_user_by_id_service(user_id)

    return jsonify(_serialize_user(user)), 200


@api_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json(silent=True) or {}

    user = create_user_service(
        name=data.get("name", ""),
        raw_email=data.get("email"),
    )

    log("info", "User created by admin", user=_serialize_user(user))

    return jsonify(
        {
            "message": "User created",
            "user": _serialize_user(user),
        }
    ), 201


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    data = request.get_json(silent=True) or {}

    if "name" not in data:
        return jsonify({"error": "Name is required", "code": "name_required"}), 400

    user = update_user_service(
        user_id=user_id,
        name=data.get("name", ""),
        raw_email=data.get("email"),
    )

    log("info", "User updated by admin", user=_serialize_user(user))

    return jsonify(
        {
            "message": "User updated",
            "user": _serialize_user(user),
        }
    ), 200


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    log("info", "Delete user request", user_id=user_id)

    deleted = delete_user_service(user_id)
    deleted_id = deleted["id"] if isinstance(deleted, dict) else deleted[0]

    log("info", "User deleted by admin", user_id=deleted_id)

    return jsonify(
        {
            "message": "User deleted",
            "id": deleted_id,
        }
    ), 200