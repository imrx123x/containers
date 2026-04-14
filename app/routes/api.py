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
    """
    Get users list
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: query
        name: q
        type: string
        required: false
        description: Search query by name or email
      - in: query
        name: page
        type: integer
        required: false
        default: 1
      - in: query
        name: limit
        type: integer
        required: false
        default: 10
    responses:
      200:
        description: Users list
        schema:
          type: object
          properties:
            data:
              type: array
              items:
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
            page:
              type: integer
              example: 1
            limit:
              type: integer
              example: 10
            total:
              type: integer
              example: 5
      401:
        description: Unauthorized
    """
    query = request.args.get("q")

    from app.utils_params import parse_positive_int
    page = parse_positive_int(
        request.args.get("page"),
        default=1,
        field_name="page",
    )

    limit = parse_positive_int(
        request.args.get("limit"),
        default=10,
        field_name="limit",
        min_value=1,
        max_value=100,
    )

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
    """
    Get single user
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: Single user
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
      404:
        description: User not found
    """
    log("info", "Fetching single user", user_id=user_id)

    user = get_user_by_id_service(user_id)

    return jsonify(_serialize_user(user)), 200


@api_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    security:
      - Bearer: []
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
          properties:
            name:
              type: string
              example: Anna
            email:
              type: string
              example: anna@example.com
    responses:
      201:
        description: User created
        schema:
          type: object
          properties:
            message:
              type: string
              example: User created
            user:
              type: object
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden
      409:
        description: Email already exists
    """
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
    """
    Update user
    ---
    tags:
      - Users
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: Anna Kowalska
            email:
              type: string
              example: anna@example.com
    responses:
      200:
        description: User updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: User updated
            user:
              type: object
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden
      404:
        description: User not found
      409:
        description: Email already exists
    """
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
    """
    Delete user
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User deleted
        schema:
          type: object
          properties:
            message:
              type: string
              example: User deleted
            id:
              type: integer
              example: 1
      401:
        description: Unauthorized
      403:
        description: Forbidden
      404:
        description: User not found
    """
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