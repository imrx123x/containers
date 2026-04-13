import os
import uuid

from flask import Flask, jsonify, g, request

from app.routes.web import web_bp
from app.routes.api import api_bp
from app.logging import log


def create_app():
    app = Flask(__name__)

    # ========================
    # Config
    # ========================

    secret_key = os.getenv("SECRET_KEY")
    app_env = os.getenv("APP_ENV", "development").lower()

    if app_env == "production" and not secret_key:
        raise RuntimeError("SECRET_KEY must be set in production")

    app.config["ENV_NAME"] = app_env
    app.config["SECRET_KEY"] = secret_key or "dev-secret-key"
    app.config["JSON_SORT_KEYS"] = False

    # ========================
    # Request ID (global)
    # ========================

    @app.before_request
    def assign_request_id():
        g.request_id = str(uuid.uuid4())

    # ========================
    # Logging response (API + WEB)
    # ========================

    @app.after_request
    def log_response(response):
        try:
            log(
                "info",
                "Request completed",
                status=response.status_code,
                method=request.method,
                path=request.path,
            )
        except Exception:
            # logging nigdy nie może rozwalić requestu
            pass

        return response

    # ========================
    # Blueprints
    # ========================

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    # ========================
    # Error handlers
    # ========================

    register_error_handlers(app)

    return app


def register_error_handlers(app: Flask):
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