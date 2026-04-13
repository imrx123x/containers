from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.repository import (
    get_all_users,
    add_user_to_db,
    update_user_in_db,
    delete_user_from_db,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET"])
def home():
    logger.info("GET / - fetching all users")
    users = get_all_users()
    logger.info(f"Users count: {len(users)}")
    return render_template("index.html", users=users)


@web_bp.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name", "").strip()
    logger.info(f"POST /add-user - received name: '{name}'")

    if not name:
        logger.warning("Add user failed: empty name")
        flash("Name is required", "error")
        return redirect(url_for("web.home"))

    if len(name) > 100:
        logger.warning("Add user failed: name too long")
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("web.home"))

    try:
        user = add_user_to_db(name)
        logger.info(f"User added: {user}")
        flash("User added successfully", "success")
    except Exception as e:
        logger.error(f"Database error while adding user: {e}")
        flash("Database error while adding user", "error")

    return redirect(url_for("web.home"))


@web_bp.route("/edit-user/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    name = request.form.get("name", "").strip()
    logger.info(f"POST /edit-user/{user_id} - new name: '{name}'")

    if not name:
        logger.warning("Edit user failed: empty name")
        flash("Name is required", "error")
        return redirect(url_for("web.home"))

    if len(name) > 100:
        logger.warning("Edit user failed: name too long")
        flash("Name must be at most 100 characters", "error")
        return redirect(url_for("web.home"))

    try:
        updated_user = update_user_in_db(user_id, name)

        if not updated_user:
            logger.warning(f"User not found: id={user_id}")
            flash("User not found", "error")
        else:
            logger.info(f"User updated: {updated_user}")
            flash("User updated successfully", "success")
    except Exception as e:
        logger.error(f"Database error while updating user: {e}")
        flash("Database error while updating user", "error")

    return redirect(url_for("web.home"))


@web_bp.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    logger.info(f"POST /delete-user/{user_id}")

    try:
        deleted_user = delete_user_from_db(user_id)

        if not deleted_user:
            logger.warning(f"User not found for deletion: id={user_id}")
            flash("User not found", "error")
        else:
            logger.info(f"User deleted: id={deleted_user[0]}")
            flash("User deleted successfully", "success")
    except Exception as e:
        logger.error(f"Database error while deleting user: {e}")
        flash("Database error while deleting user", "error")

    return redirect(url_for("web.home"))