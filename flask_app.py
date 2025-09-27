"""
Main entry point for the Mechanic Shop Flask application.
"""

from app import create_app
from app.extensions import db
from config import config

# Create the application
app = create_app(config["production"])
