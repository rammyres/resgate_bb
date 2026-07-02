import os

from flask import Flask


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-troque-em-producao"),
        MAX_CONTENT_LENGTH=1 * 1024 * 1024,  # 1 MB é mais que suficiente para o payload JSON
    )

    if test_config:
        app.config.update(test_config)

    from . import routes
    app.register_blueprint(routes.bp)

    return app
