import logging
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify

from app.db import check_db_health
from app.repository import (
    get_users_paginated,
    add_user_to_db,
    update_user_in_db,
    delete_user_from_db,
    search_users_paginated,
)
from app.utils import normalize_email


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

web_bp = Blueprint("web", __name__)


# ========================
# Logging helpers
# ========================

def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr


def get_actor():
    return "anonymous"


def build_request_context():
    request_id = getattr(g, "request_id", None)
    if not request_id:
        request_id = str(uuid.uuid4())
        g.request_id = request_id

    return {
        "request_id": request_id,
        "method": request.method,
        "path": request.path,
        "ip": get_client_ip(),
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "referer": request.headers.get("Referer", "-"),
        "actor": get_actor(),
    }


def log_with_context(level, message, **extra):
    ctx = build_request_context()
    payload = {
        **ctx,
        **extra,
    }

    formatted = (
        f"[request_id={payload['request_id']}] "
        f"actor={payload['actor']} | "
        f"{payload['method']} {payload['path']} | "
        f"ip={payload['ip']} | "
        f"referer={payload['referer']} | "
        f"user_agent={payload['user_agent']} | "
        f"{message}"
    )

    reserved_keys = {
        "request_id", "method", "path", "ip", "referer", "user_agent", "actor"
    }

    extra_parts = [
        f"{key}={value}" for key, value in payload.items() if key not in reserved_keys
    ]

    if extra_parts:
        formatted += " | " + " | ".join(extra_parts)

    if level == "info":
        logger.info(formatted)
    elif level == "warning":
        logger.warning(formatted)
    elif level == "error":
        logger.error(formatted)
    elif level == "exception":
        logger.exception(formatted)
    else:
        logger.info(formatted)


@web_bp.before_app_request
def assign_request_id():
    g.request_id = str(uuid.uuid4())


# ========================
# Health
# ========================

@web_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@web_bp.route("/health/db", methods=["GET"])
def health_db():
    db_ok = check_db_health()

    if db_ok:
        return jsonify({"status": "ok", "database": "up"}), 200

    return jsonify({"status": "degraded", "database": "down"}), 503


# ========================
# Home
# ========================

@web_bp.route("/", methods=["GET"])
def home():
    query = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    limit = 10

    try:
        if query:
            users, total = search_users_paginated(query, page, limit)
        else:
            users, total = get_users_paginated(page, limit)

        # 🔥 kluczowe: normalize (tuple → dict)
        users = [
            user if isinstance(user, dict) else {
                "id": user[0],
                "name": user[1],
                "email": user[2],
            }
            for user in users
        ]

        total_pages = (total + limit - 1) // limit

        return render_template(
            "index.html",
            users=users,
            query=query,
            page=page,
            total_pages=total_pages,
        )

    except Exception:
        log_with_context("exception", "Database error on home page")
        flash("Database error", "error")

        return render_template(
            "index.html",
            users=[],
            query=query,
            page=1,
            total_pages=1,
        )


# ========================
# Create
# ========================

@web_bp.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name", "").strip()
    raw_email = request.form.get("email", "")
    email = normalize_email(raw_email)

    log_with_context(
        "info",
        "Received add user request",
        submitted_name=name,
        submitted_email=raw_email
    )

    if not name:
        log_with_context("warning", "Add user failed: empty name")
        flash("Name is required", "error")
        return redirect(url_for("web.home"))

    if len(name) > 100:
        log_with_context("warning", "Add user failed: name too long")
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("web.home"))

    if raw_email.strip() and email is None:
        log_with_context("warning", "Add user failed: invalid email")
        flash("Email is invalid", "error")
        return redirect(url_for("web.home"))

    try:
        user = add_user_to_db(name, email)

        log_with_context("info", "User added successfully", user=user)
        flash("User added successfully", "success")

    except Exception:
        log_with_context("exception", "Database error while adding user")
        flash("Database error while adding user", "error")

    return redirect(url_for("web.home"))


# ========================
# Update
# ========================

@web_bp.route("/edit-user/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    name = request.form.get("name", "").strip()
    raw_email = request.form.get("email", "")
    email = normalize_email(raw_email)

    log_with_context(
        "info",
        "Received edit user request",
        target_user_id=user_id,
        new_name=name,
        new_email=raw_email,
    )

    if not name:
        log_with_context("warning", "Edit user failed: empty name")
        flash("Name is required", "error")
        return redirect(url_for("web.home"))

    if len(name) > 100:
        log_with_context("warning", "Edit user failed: name too long")
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("web.home"))

    if raw_email.strip() and email is None:
        log_with_context("warning", "Edit user failed: invalid email")
        flash("Email is invalid", "error")
        return redirect(url_for("web.home"))

    try:
        updated_user = update_user_in_db(user_id, name, email)

        if not updated_user:
            log_with_context("warning", "User not found for update")
            flash("User not found", "error")
        else:
            log_with_context("info", "User updated successfully", user=updated_user)
            flash("User updated successfully", "success")

    except Exception:
        log_with_context("exception", "Database error while updating user")
        flash("Database error while updating user", "error")

    return redirect(url_for("web.home"))


# ========================
# Delete
# ========================

@web_bp.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    log_with_context("info", "Received delete user request", target_user_id=user_id)

    try:
        deleted_user = delete_user_from_db(user_id)

        if not deleted_user:
            log_with_context("warning", "User not found for deletion")
            flash("User not found", "error")
        else:
            deleted_user_id = (
                deleted_user["id"]
                if isinstance(deleted_user, dict)
                else deleted_user[0]
            )

            log_with_context(
                "info",
                "User deleted successfully",
                deleted_user_id=deleted_user_id
            )

            flash("User deleted successfully", "success")

    except Exception:
        log_with_context("exception", "Database error while deleting user")
        flash("Database error while deleting user", "error")

    return redirect(url_for("web.home"))