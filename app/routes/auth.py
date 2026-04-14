from flask import Blueprint, g, jsonify, request

from app.auth import auth_required
from app.logging import log
from app.services.auth_service import (
    change_password_service,
    login_user_service,
    register_user_service,
)
from app.services.user_service import update_current_user_service
from app.utils_rate_limit import enforce_rate_limit


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
    """
    Register a new user
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: Anna
            email:
              type: string
              example: anna@example.com
            password:
              type: string
              example: supersecret123
    responses:
      201:
        description: Registration successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Registration successful
            access_token:
              type: string
              example: some-generated-token
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Anna
                email:
                  type: string
                  example: anna@example.com
                role:
                  type: string
                  example: user
      400:
        description: Validation error
      409:
        description: Email already exists
    """
    enforce_rate_limit(
        action="auth_register",
        limit=5,
        window_seconds=60,
    )

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
    """
    Login user
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: anna@example.com
            password:
              type: string
              example: supersecret123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            access_token:
              type: string
              example: some-generated-token
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Anna
                email:
                  type: string
                  example: anna@example.com
                role:
                  type: string
                  example: user
      401:
        description: Invalid credentials
    """
    enforce_rate_limit(
        action="auth_login",
        limit=10,
        window_seconds=60,
    )

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
    """
    Get current user profile
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    responses:
      200:
        description: Current authenticated user
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: Anna
            email:
              type: string
              example: anna@example.com
            role:
              type: string
              example: user
      401:
        description: Unauthorized
    """
    log("info", "Fetched current user", user_id=g.current_user["id"])
    return jsonify(_serialize_user(g.current_user)), 200


@auth_bp.route("/me", methods=["PATCH"])
@auth_required
def update_me():
    """
    Update current user profile
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Anna Kowalska
            email:
              type: string
              example: anna@example.com
    responses:
      200:
        description: Profile updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Profile updated
            user:
              type: object
      400:
        description: Validation error
      401:
        description: Unauthorized
      409:
        description: Email already exists
    """
    data = request.get_json(silent=True) or {}

    user = update_current_user_service(
        user_id=g.current_user["id"],
        name=data.get("name") if "name" in data else None,
        raw_email=data.get("email") if "email" in data else None,
    )

    g.current_user = user

    log("info", "Current user updated", user_id=user["id"], email=user["email"])

    return jsonify(
        {
            "message": "Profile updated",
            "user": _serialize_user(user),
        }
    ), 200


@auth_bp.route("/change-password", methods=["POST"])
@auth_required
def change_password():
    """
    Change current user password
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
              example: oldpass123
            new_password:
              type: string
              example: newpass123
    responses:
      200:
        description: Password changed successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Password changed successfully
            user:
              type: object
      400:
        description: Validation error
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    enforce_rate_limit(
        action="auth_change_password",
        limit=5,
        window_seconds=60,
        identifier=str(g.current_user["id"]),
    )

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