from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.logging import log
from app.db import check_db_health
from app.repository import (
    add_user_to_db,
    delete_user_from_db,
    get_users_paginated,
    search_users_paginated,
    update_user_in_db,
)
from app.utils import normalize_email


web_bp = Blueprint("web", __name__)


@web_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@web_bp.route("/health/db", methods=["GET"])
def health_db():
    db_ok = check_db_health()

    if db_ok:
        return jsonify({"status": "ok", "database": "up"}), 200

    return jsonify({"status": "degraded", "database": "down"}), 503


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
        log("exception", "Database error on home page")
        flash("Database error", "error")

        return render_template(
            "index.html",
            users=[],
            query=query,
            page=1,
            total_pages=1,
        )


@web_bp.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name", "").strip()
    raw_email = request.form.get("email", "")
    email = normalize_email(raw_email)

    log(
        "info",
        "Received add user request",
        submitted_name=name,
        submitted_email=raw_email,
    )

    if not name:
        log("warning", "Add user failed: empty name")
        flash("Name is required", "error")
        return redirect(url_for("web.home"))

    if len(name) > 100:
        log("warning", "Add user failed: name too long")
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("web.home"))

    if raw_email.strip() and email is None:
        log("warning", "Add user failed: invalid email")
        flash("Email is invalid", "error")
        return redirect(url_for("web.home"))

    try:
        user = add_user_to_db(name, email)

        log("info", "User added successfully", user=user)
        flash("User added successfully", "success")

    except Exception:
        log("exception", "Database error while adding user")
        flash("Database error while adding user", "error")

    return redirect(url_for("web.home"))


@web_bp.route("/edit-user/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    name = request.form.get("name", "").strip()
    raw_email = request.form.get("email", "")
    email = normalize_email(raw_email)

    log(
        "info",
        "Received edit user request",
        target_user_id=user_id,
        new_name=name,
        new_email=raw_email,
    )

    if not name:
        log("warning", "Edit user failed: empty name")
        flash("Name is required", "error")
        return redirect(url_for("web.home"))

    if len(name) > 100:
        log("warning", "Edit user failed: name too long")
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("web.home"))

    if raw_email.strip() and email is None:
        log("warning", "Edit user failed: invalid email")
        flash("Email is invalid", "error")
        return redirect(url_for("web.home"))

    try:
        updated_user = update_user_in_db(user_id, name, email)

        if not updated_user:
            log("warning", "User not found for update")
            flash("User not found", "error")
        else:
            log("info", "User updated successfully", user=updated_user)
            flash("User updated successfully", "success")

    except Exception:
        log("exception", "Database error while updating user")
        flash("Database error while updating user", "error")

    return redirect(url_for("web.home"))


@web_bp.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    log("info", "Received delete user request", target_user_id=user_id)

    try:
        deleted_user = delete_user_from_db(user_id)

        if not deleted_user:
            log("warning", "User not found for deletion")
            flash("User not found", "error")
        else:
            deleted_user_id = (
                deleted_user["id"]
                if isinstance(deleted_user, dict)
                else deleted_user[0]
            )

            log(
                "info",
                "User deleted successfully",
                deleted_user_id=deleted_user_id,
            )
            flash("User deleted successfully", "success")

    except Exception:
        log("exception", "Database error while deleting user")
        flash("Database error while deleting user", "error")

    return redirect(url_for("web.home"))