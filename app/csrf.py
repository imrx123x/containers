from flask_wtf.csrf import CSRFError, CSRFProtect

csrf = CSRFProtect()


def init_csrf(app):
    csrf.init_app(app)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        from flask import flash, jsonify, redirect, request, url_for

        if request.path.startswith("/api/"):
            return jsonify(
                {
                    "error": "CSRF token missing or invalid",
                    "code": "csrf_error",
                }
            ), 400

        flash("Sesja formularza wygasła albo token CSRF jest niepoprawny. Spróbuj ponownie.", "error")
        return redirect(request.referrer or url_for("web.home"))