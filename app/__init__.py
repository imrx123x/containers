import os

from flask import Flask, jsonify
from app.routes.web import web_bp
from app.routes.api import api_bp


def create_app():
    app = Flask(__name__)

    secret_key = os.getenv("SECRET_KEY")
    app_env = os.getenv("APP_ENV", "development").lower()

    if app_env == "production" and not secret_key:
        raise RuntimeError("SECRET_KEY must be set in production")

    app.config["ENV_NAME"] = app_env
    app.config["SECRET_KEY"] = secret_key or "dev-secret-key"
    app.config["JSON_SORT_KEYS"] = False

    register_blueprints(app)
    register_error_handlers(app)

    return app


def register_blueprints(app: Flask):
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)


def register_error_handlers(app: Flask):
    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "Internal server error"}), 500