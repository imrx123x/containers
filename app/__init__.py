import os
import time
import uuid

from flask import Flask, g, jsonify, request

from app.exceptions import AppError
from app.logging import log
from app.routes.api import api_bp
from app.routes.auth import auth_bp
from app.routes.web import web_bp


def create_app():
    app = Flask(__name__)

    secret_key = os.getenv("SECRET_KEY")
    app_env = os.getenv("APP_ENV", "development").lower()

    if app_env == "production" and not secret_key:
        raise RuntimeError("SECRET_KEY must be set in production")

    app.config["ENV_NAME"] = app_env
    app.config["SECRET_KEY"] = secret_key or "dev-secret-key"
    app.config["JSON_SORT_KEYS"] = False

    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.started_at = time.perf_counter()

    @app.after_request
    def after_request(response):
        try:
            duration_ms = None

            if hasattr(g, "started_at"):
                duration_ms = round((time.perf_counter() - g.started_at) * 1000, 2)

            response.headers["X-Request-ID"] = g.request_id

            log(
                "info",
                "Request completed",
                status=response.status_code,
                duration_ms=duration_ms,
                method=request.method,
                path=request.path,
            )
        except Exception:
            pass

        return response

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    register_error_handlers(app)

    return app


def register_error_handlers(app: Flask):
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        log(
            "warning",
            "Application error",
            error_code=error.code,
            error_message=error.message,
            status=error.status_code,
        )
        return jsonify({"error": error.message, "code": error.code}), error.status_code

    @app.errorhandler(404)
    def not_found(_error):
        log("warning", "Route not found")
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        log("warning", "Method not allowed")
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(Exception)
    def internal_error(error):
        log("exception", "Unhandled exception", error=str(error))
        return jsonify({"error": "Internal server error"}), 500