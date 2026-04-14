from flasgger import Swagger


swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Flask Users API",
        "description": "API for user management, authentication, and role-based access control.",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["https"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Wklej token w formacie: Bearer <access_token>",
        }
    },
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}


def init_swagger(app):
    Swagger(app, template=swagger_template, config=swagger_config)