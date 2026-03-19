import os
from flask import Flask
from app.routes.web import web_bp
from app.routes.api import api_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    return app