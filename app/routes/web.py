from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.db import check_db_health
from app.logging import log
from app.repository import (
    add_audit_log,
    add_user_to_db,
    delete_user_from_db,
    get_dashboard_stats,
    get_recent_audit_logs,
    get_user_by_id,
    get_users_paginated,
    search_users_paginated,
    update_user_in_db,
)
from app.services.auth_service import (
    change_password_service,
    login_user_service,
    register_user_service,
)
from app.services.user_service import update_current_user_service
from app.utils import decode_access_token, normalize_email


web_bp = Blueprint("web", __name__)


def get_session_user():
    token = session.get("access_token")
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        session.pop("access_token", None)
        session.pop("user_name", None)
        return None

    user_id = payload.get("sub")
    if user_id is None:
        session.pop("access_token", None)
        session.pop("user_name", None)
        return None

    db_user = get_user_by_id(user_id)
    if db_user:
        session["user_name"] = db_user.get("name") or "User"
        return db_user

    session.pop("access_token", None)
    session.pop("user_name", None)
    return None


def login_required_web():
    user = get_session_user()
    if not user:
        flash("Zaloguj się, aby przejść dalej", "error")
        return None
    return user


def admin_required_web():
    user = login_required_web()
    if not user:
        return None

    if user.get("role") != "admin":
        flash("Brak uprawnień do tej sekcji", "error")
        return None

    return user


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
    user = get_session_user()
    is_admin = bool(user and user.get("role") == "admin")

    if not is_admin:
        return render_template(
            "index.html",
            current_user=user,
            is_admin=False,
            users=[],
            query="",
            page=1,
            total_pages=1,
            stats=None,
            recent_logs=[],
        )

    query = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    limit = 10

    try:
        if query:
            users, total = search_users_paginated(query, page, limit)
        else:
            users, total = get_users_paginated(page, limit)

        users = [
            user_item if isinstance(user_item, dict) else {
                "id": user_item[0],
                "name": user_item[1],
                "email": user_item[2],
            }
            for user_item in users
        ]

        total_pages = max(1, (total + limit - 1) // limit)
        stats = get_dashboard_stats()
        recent_logs = get_recent_audit_logs(limit=10)

        return render_template(
            "index.html",
            current_user=user,
            is_admin=True,
            users=users,
            query=query,
            page=page,
            total_pages=total_pages,
            stats=stats,
            recent_logs=recent_logs,
        )

    except Exception:
        log("exception", "Database error on home page")
        flash("Database error", "error")

        return render_template(
            "index.html",
            current_user=user,
            is_admin=True,
            users=[],
            query=query,
            page=1,
            total_pages=1,
            stats=None,
            recent_logs=[],
        )


@web_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        if get_session_user():
            return redirect(url_for("web.profile"))
        return render_template("login.html", current_user=None)

    email = request.form.get("email", "")
    password = request.form.get("password", "")

    try:
        result = login_user_service(
            raw_email=email,
            password=password,
        )

        user = result["user"]

        session["access_token"] = result["access_token"]
        session["user_name"] = user["name"]

        add_audit_log(
            action="login",
            actor_id=user["id"],
            actor_email=user["email"],
            target_user_id=user["id"],
            target_email=user["email"],
            details="User logged in via web",
        )

        flash("Zalogowano pomyślnie", "success")
        log("info", "User logged in via web", user_id=user["id"], email=user["email"])

        return redirect(url_for("web.profile"))

    except Exception as error:
        log("warning", "Web login failed", error=str(error))
        flash(getattr(error, "message", "Logowanie nie powiodło się"), "error")
        return render_template("login.html", current_user=None), 400


@web_bp.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        if get_session_user():
            return redirect(url_for("web.profile"))
        return render_template("register.html", current_user=None)

    name = request.form.get("name", "")
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    try:
        result = register_user_service(
            name=name,
            raw_email=email,
            password=password,
        )

        user = result["user"]

        session["access_token"] = result["access_token"]
        session["user_name"] = user["name"]

        add_audit_log(
            action="register",
            actor_id=user["id"],
            actor_email=user["email"],
            target_user_id=user["id"],
            target_email=user["email"],
            details="User registered via web",
        )

        flash("Konto zostało utworzone", "success")
        log("info", "User registered via web", user_id=user["id"], email=user["email"])

        return redirect(url_for("web.profile"))

    except Exception as error:
        log("warning", "Web register failed", error=str(error))
        flash(getattr(error, "message", "Rejestracja nie powiodła się"), "error")
        return render_template("register.html", current_user=None), 400


@web_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("access_token", None)
    session.pop("user_name", None)
    flash("Wylogowano", "success")
    return redirect(url_for("web.home"))


@web_bp.route("/profile", methods=["GET"])
def profile():
    user = login_required_web()
    if not user:
        return redirect(url_for("web.login_page"))

    fresh_user = get_user_by_id(user["id"]) or user

    return render_template("profile.html", current_user=fresh_user)


@web_bp.route("/profile", methods=["POST"])
def update_profile():
    user = login_required_web()
    if not user:
        return redirect(url_for("web.login_page"))

    name = request.form.get("name")
    email = request.form.get("email")

    try:
        updated_user = update_current_user_service(
            user_id=user["id"],
            name=name,
            raw_email=email,
        )

        session["user_name"] = updated_user["name"]

        add_audit_log(
            action="update_profile",
            actor_id=updated_user["id"],
            actor_email=updated_user["email"],
            target_user_id=updated_user["id"],
            target_email=updated_user["email"],
            details="User updated own profile",
        )

        flash("Profil został zaktualizowany", "success")
        log(
            "info",
            "Profile updated via web",
            user_id=updated_user["id"],
            email=updated_user["email"],
        )

    except Exception as error:
        log(
            "warning",
            "Web profile update failed",
            error=str(error),
            user_id=user["id"],
        )
        flash(getattr(error, "message", "Nie udało się zaktualizować profilu"), "error")

    return redirect(url_for("web.profile"))


@web_bp.route("/change-password", methods=["POST"])
def change_password_web():
    user = login_required_web()
    if not user:
        return redirect(url_for("web.login_page"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")

    try:
        result = change_password_service(
            user_id=user["id"],
            current_password=current_password,
            new_password=new_password,
        )

        add_audit_log(
            action="change_password",
            actor_id=user["id"],
            actor_email=user.get("email"),
            target_user_id=user["id"],
            target_email=user.get("email"),
            details="User changed own password",
        )

        flash(result["message"], "success")
        log("info", "Password changed via web", user_id=user["id"])

    except Exception as error:
        log("warning", "Web password change failed", error=str(error), user_id=user["id"])
        flash(getattr(error, "message", "Nie udało się zmienić hasła"), "error")

    return redirect(url_for("web.profile"))


@web_bp.route("/add-user", methods=["POST"])
def add_user():
    current_user = admin_required_web()
    if not current_user:
        return redirect(url_for("web.home"))

    name = request.form.get("name", "").strip()
    raw_email = request.form.get("email", "")
    email = normalize_email(raw_email)

    log(
        "info",
        "Received add user request",
        submitted_name=name,
        submitted_email=raw_email,
        actor_id=current_user["id"],
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

        add_audit_log(
            action="create_user",
            actor_id=current_user["id"],
            actor_email=current_user.get("email"),
            target_user_id=user["id"],
            target_email=user.get("email"),
            details=f"Admin created user: {user['name']}",
        )

        log("info", "User added successfully", user=user)
        flash("User added successfully", "success")

    except Exception:
        log("exception", "Database error while adding user")
        flash("Database error while adding user", "error")

    return redirect(url_for("web.home"))


@web_bp.route("/edit-user/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    current_user = admin_required_web()
    if not current_user:
        return redirect(url_for("web.home"))

    name = request.form.get("name", "").strip()
    raw_email = request.form.get("email", "")
    email = normalize_email(raw_email)

    log(
        "info",
        "Received edit user request",
        target_user_id=user_id,
        new_name=name,
        new_email=raw_email,
        actor_id=current_user["id"],
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
            add_audit_log(
                action="update_user",
                actor_id=current_user["id"],
                actor_email=current_user.get("email"),
                target_user_id=updated_user["id"],
                target_email=updated_user.get("email"),
                details=f"Admin updated user: {updated_user['name']}",
            )

            log("info", "User updated successfully", user=updated_user)
            flash("User updated successfully", "success")

    except Exception:
        log("exception", "Database error while updating user")
        flash("Database error while updating user", "error")

    return redirect(url_for("web.home"))


@web_bp.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    current_user = admin_required_web()
    if not current_user:
        return redirect(url_for("web.home"))

    log(
        "info",
        "Received delete user request",
        target_user_id=user_id,
        actor_id=current_user["id"],
    )

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

            add_audit_log(
                action="delete_user",
                actor_id=current_user["id"],
                actor_email=current_user.get("email"),
                target_user_id=deleted_user_id,
                target_email=None,
                details=f"Admin deleted user with id={deleted_user_id}",
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