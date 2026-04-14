from flask import Blueprint, g, jsonify, request

from app.auth import auth_required
from app.logging import log
from app.services.auth_service import (
    change_password_service,
    login_user_service,
    register_user_service,
)


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _serialize_user(user):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    result = register_user_service(
        name=data.get("name", ""),
        raw_email=data.get("email"),
        password=data.get("password", ""),
    )

    user = result["user"]

    log("info", "User registered", user_id=user["id"], email=user["email"])

    return jsonify(
        {
            "message": result["message"],
            "access_token": result["access_token"],
            "user": _serialize_user(user),
        }
    ), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    result = login_user_service(
        raw_email=data.get("email"),
        password=data.get("password", ""),
    )

    user = result["user"]

    log("info", "User logged in", user_id=user["id"], email=user["email"])

    return jsonify(
        {
            "message": result["message"],
            "access_token": result["access_token"],
            "user": _serialize_user(user),
        }
    ), 200


@auth_bp.route("/me", methods=["GET"])
@auth_required
def me():
    log("info", "Fetched current user", user_id=g.current_user["id"])
    return jsonify(_serialize_user(g.current_user)), 200


@auth_bp.route("/change-password", methods=["POST"])
@auth_required
def change_password():
    data = request.get_json(silent=True) or {}

    result = change_password_service(
        user_id=g.current_user["id"],
        current_password=data.get("current_password", ""),
        new_password=data.get("new_password", ""),
    )

    log("info", "Password changed", user_id=g.current_user["id"])

    return jsonify(
        {
            "message": result["message"],
            "user": _serialize_user(result["user"]),
        }
    ), 200