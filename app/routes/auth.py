from flask import Blueprint, g, jsonify, request

from app.logging import log
from app.auth import auth_required
from app.repository import add_user_to_db, get_user_by_email
from app.utils import (
    generate_access_token,
    hash_password,
    normalize_email,
    validate_password,
    verify_password,
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

    name = data.get("name", "").strip()
    raw_email = data.get("email")
    password = data.get("password", "")

    if not name:
        log("warning", "Register failed: missing name")
        return jsonify({"error": "Name is required"}), 400

    if len(name) > 100:
        log("warning", "Register failed: name too long")
        return jsonify({"error": "Name too long"}), 400

    email = normalize_email(raw_email)
    if raw_email is not None and email is None:
        log("warning", "Register failed: invalid email")
        return jsonify({"error": "Email is invalid"}), 400

    if not email:
        log("warning", "Register failed: missing email")
        return jsonify({"error": "Email is required"}), 400

    if not validate_password(password):
        log("warning", "Register failed: weak password")
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if get_user_by_email(email):
        log("warning", "Register failed: email exists", email=email)
        return jsonify({"error": "Email already exists"}), 409

    user = add_user_to_db(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="user",
    )

    token = generate_access_token(user)

    log("info", "User registered", user_id=user["id"], email=user["email"])

    return jsonify(
        {
            "message": "Registration successful",
            "access_token": token,
            "user": _serialize_user(user),
        }
    ), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    raw_email = data.get("email")
    password = data.get("password", "")

    email = normalize_email(raw_email)
    if not email:
        log("warning", "Login failed: invalid email")
        return jsonify({"error": "Invalid credentials"}), 401

    user = get_user_by_email(email, include_password=True)

    if not user:
        log("warning", "Login failed: user not found", email=email)
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(user.get("password_hash"), password):
        log("warning", "Login failed: invalid password", email=email)
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_access_token(user)

    log("info", "User logged in", user_id=user["id"], email=user["email"])

    return jsonify(
        {
            "message": "Login successful",
            "access_token": token,
            "user": _serialize_user(user),
        }
    ), 200


@auth_bp.route("/me", methods=["GET"])
@auth_required
def me():
    log("info", "Fetched current user", user_id=g.current_user["id"])
    return jsonify(_serialize_user(g.current_user)), 200