"""
Application factory for the mechanic shop Flask application.
"""

from flask import Flask, send_from_directory, jsonify
from flask import Blueprint, render_template
from sqlalchemy import inspect
from flask_migrate import Migrate
from datetime import datetime
import os
from config import config
from app.extensions import db, ma, limiter, cache, jwt, cors

# Global variable to track if swagger is already set up
_swagger_registered = False


def create_app(config_class=None):
    """
    Create and configure the Flask application.

    Args:
        config_class: Configuration class object
                     If None, defaults to 'development' config

    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask. It will automatically find the 'templates' folder inside the 'app' package.
    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        config_class = config["development"]

    app.config.from_object(config_class)

    # For production, ensure critical environment variables are set.
    # This check is now done at app creation time, not import time.
    if not app.config.get("DEBUG", False) and not app.config.get("TESTING", False):
        # This is "production" mode as per Flask's new conventions
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            raise ValueError("DATABASE_URL is not set for the production environment.")
        # You could add a similar check for SECRET_KEY here as well.

    # Configure caching (using simple in-memory cache for development)
    app.config["CACHE_TYPE"] = "simple"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # 5 minutes default cache timeout

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)  # Initialize rate limiter
    cache.init_app(app)  # Initialize cache
    jwt.init_app(app)
    cors.init_app(app)
    Migrate(app, db)  # Initialize Flask-Migrate

    # Register blueprints
    register_blueprints(app)

    # Import models here so they are registered with Flask-Migrate and other extensions
    with app.app_context():
        from . import models  # noqa: F441, F401

    # The database creation logic is now handled by Flask-Migrate CLI commands
    # This prevents the app from trying to create tables on every startup.

    # Only register Swagger in non-testing environments
    if not app.config.get("TESTING", False):
        setup_swagger(app)

    # Register additional routes
    register_additional_routes(app)

    return app


def setup_swagger(app):
    """Setup Swagger documentation"""
    global _swagger_registered

    if _swagger_registered:
        return

    try:
        # Use flasgger instead of flask_swagger
        from flasgger import Swagger

        host = "localhost:5000"
        schemes = ["http"]
        if not app.config.get("DEBUG", False):
            host = (
                os.environ.get("RENDER_EXTERNAL_HOSTNAME")
                or "mechanic-shop.onrender.com"
            )
            schemes = ["https"]

        swagger_template = {
            "swagger": "2.0",
            "info": {
                "title": "Mechanic Shop Management API",
                "description": (
                    "A comprehensive API for managing a mechanic shop's "
                    "operations including customers, mechanics, service "
                    "tickets, inventory, and memberships."
                ),
                "version": "1.0.0",
                "contact": {
                    "name": "API Support",
                    "email": "support@mechanicshop.com",
                },
            },
            "host": host,
            "basePath": "/",
            "schemes": schemes,
            "securityDefinitions": {
                "Bearer": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": (
                        "JWT Authorization header using the Bearer scheme. "
                        "Example: 'Authorization: Bearer {token}'"
                    ),
                }
            },
            "tags": [
                {"name": "customers", "description": "Customer management operations"},
                {"name": "mechanics", "description": "Mechanic management operations"},
                {
                    "name": "service-tickets",
                    "description": "Service ticket management operations",
                },
                {"name": "inventory", "description": "Inventory management operations"},
                {"name": "members", "description": "Membership management operations"},
                {
                    "name": "calculations",
                    "description": "Mathematical calculation operations",
                },
            ],
        }

        Swagger(app, template=swagger_template)
        _swagger_registered = True

    except ImportError:
        # Swagger packages not installed, skip swagger setup
        pass
    except Exception as e:
        print(f"Warning: Could not set up Swagger: {e}")


def register_blueprints(app):
    """Register application blueprints"""

    blueprints_to_register = [
        ("app.blueprints.mechanics.routes", "mechanics_bp", "/mechanics"),
        ("app.blueprints.service_tickets.routes", "service_tickets_bp", "/service-tickets"),
        ("app.blueprints.customers", "customers_bp", None), # url_prefix is in the blueprint
        ("app.routes.calculations", "calculations_bp", None),
        ("app.blueprints.inventory", "inventory_bp", None),
        ("app.blueprints.members", "members_bp", None),
    ]

    for module_path, bp_name, url_prefix in blueprints_to_register:
        try:
            # Dynamically import the module and get the blueprint object
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            # Register the blueprint, with or without a URL prefix
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        except (ImportError, AttributeError, ModuleNotFoundError) as e:
            print(f"Warning: Could not import or register blueprint '{bp_name}' from '{module_path}': {e}")


def register_additional_routes(app):
    """Register additional application routes"""

    # API root endpoint
    @app.route("/")
    def index():
        """Serves the homepage."""
        return render_template("index.html")

    # Health check endpoint
    @app.route("/health")
    def health_check():
        """Simple health check endpoint."""
        return {
            "status": "healthy",
            "message": "Mechanic Shop API is running",
            "timestamp": datetime.now().isoformat(),
        }, 200

    # Rate limiting demonstration endpoint
    @app.route("/test-rate-limit")
    @limiter.limit("5 per minute")
    def test_rate_limit():
        """
        Test endpoint to demonstrate rate limiting.
        Limited to 5 requests per minute per IP.
        """
        return (
            jsonify(
                {
                    "message": "Rate limiting is working!",
                    "limit": "5 requests per minute",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    # Favicon endpoint
    @app.route("/favicon.ico")
    def favicon():
        """Serve the favicon.ico file from the static directory."""
        static_dir = os.path.join(app.root_path, "static")
        try:
            return send_from_directory(
                static_dir, "favicon.ico", mimetype="image/vnd.microsoft.icon"
            )
        except FileNotFoundError:
            # Fallback to empty response if favicon not found
            return "", 204

    # Optional: General static file serving route
    @app.route("/static/<path:filename>")
    def static_files(filename):
        """Serve static files from the static directory."""
        static_dir = os.path.join(app.root_path, "static")
        return send_from_directory(static_dir, filename)

    # Product data endpoint (example implementation)
    @app.route("/api/products", methods=["GET"])
    def get_products():
        """Get list of products"""
        # Sample response structure
        return {
            "Version": "1.0.0",
            "StatusCode": 200,
            "ApiRequestId": "unique-request-id",
            "Result": [
                {
                    "id": 1,
                    "name": "Product 1",
                    "description": "Description for product 1",
                    "price": 9.99,
                    "currency": "USD",
                },
                {
                    "id": 2,
                    "name": "Product 2",
                    "description": "Description for product 2",
                    "price": 19.99,
                    "currency": "USD",
                },
            ],
        }, 200

    return app
