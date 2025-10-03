"""
Application factory for the mechanic shop API.
"""
from flask import Flask, send_from_directory, jsonify
from flask import Blueprint, render_template
from flask_migrate import Migrate
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from flasgger import Flasgger

from app.extensions import db, ma, cache, limiter, jwt, cors
from config import config


def create_app(config_name="default"):
    """
    Create and configure an instance of the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize Flasgger for API documentation
    Flasgger(app)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)

    # Conditionally initialize Flask-Migrate
    try:
        Migrate(app, db)
    except NameError:
        pass  # flask_migrate is not installed, skip

    # Register blueprints
    register_blueprints(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Define a simple root route
    @app.route("/")
    def index():
        return "<h1>Mechanic Shop API</h1>"

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error"}), 500

    return app


def register_blueprints(app):
    """Register application blueprints"""

    blueprints_to_register = [
        ("app.blueprints.mechanics.routes", "mechanics_bp", "/mechanics"),
        ("app.blueprints.service_tickets.routes", "service_tickets_bp", "/service-tickets"),
        ("app.blueprints.customers.routes", "customers_bp", "/customers"),
        ("app.blueprints.calculations", "calculations_bp", None),
        ("app.blueprints.inventory", "inventory_bp", None),
    ]

    for module_path, bp_name, url_prefix in blueprints_to_register:
        try:
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not import or register blueprint '{bp_name}' from '{module_path}': {e}")