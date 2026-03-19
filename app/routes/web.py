from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.repository import (
    get_all_users,
    add_user_to_db,
    update_user_in_db,
    delete_user_from_db,
)

web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET"])
def home():
    users = get_all_users()
    return render_template("index.html", users=users)


@web_bp.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name", "").strip()

    if not name:
        flash("Name is required", "error")
        return redirect(url_for("web.home"))

    if len(name) > 100:
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("web.home"))

    try:
        add_user_to_db(name)
        flash("User added successfully", "success")
    except Exception:
        flash("Database error while adding user", "error")

    return redirect(url_for("web.home"))


@web_bp.route("/edit-user/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    name = request.form.get("name", "").strip()

    if not name:
        flash("Name is required", "error")
        return redirect(url_for("web.home"))

    if len(name) > 100:
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("web.home"))

    try:
        updated_user = update_user_in_db(user_id, name)

        if not updated_user:
            flash("User not found", "error")
        else:
            flash("User updated successfully", "success")
    except Exception:
        flash("Database error while updating user", "error")

    return redirect(url_for("web.home"))


@web_bp.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    try:
        deleted_user = delete_user_from_db(user_id)

        if not deleted_user:
            flash("User not found", "error")
        else:
            flash("User deleted successfully", "success")
    except Exception:
        flash("Database error while deleting user", "error")

    return redirect(url_for("web.home"))