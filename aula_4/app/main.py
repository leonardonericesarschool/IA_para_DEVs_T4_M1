"""Flask application factory and initialization."""
from flask import Flask, jsonify
from flasgger import Flasgger

from app.config.settings import get_config
from app.infrastructure.database.connection import (
    init_db,
    setup_database,
)
from app.infrastructure.database.models import db
from app.presentation.api.routes.expenses import expenses_bp


def create_app(config=None):
    """
    Create and configure the Flask application.

    Args:
        config: Configuration class (if None, uses environment-based config)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)

    # Setup database
    setup_database(app)

    # Initialize Swagger/OpenAPI documentation with CDN resources
    Flasgger(app, config={
        "headers": [],
        "swagger_ui": True,
        "uiversion": 3,
        "specs": [
            {
                "endpoint": "/apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui_bundle_js": "//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js",
        "swagger_ui_standalone_preset_js": "//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js",
        "jquery_url": "//unpkg.com/jquery@3/dist/jquery.min.js",
        "swagger_ui_css": "//unpkg.com/swagger-ui-dist@3/swagger-ui.css"
    })

    # Register blueprints
    app.register_blueprint(expenses_bp)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({"error": "Internal server error"}), 500

    # Initialize database tables
    with app.app_context():
        init_db(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
