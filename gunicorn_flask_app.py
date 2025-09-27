"""
Main entry point for the Mechanic Shop Flask application.
"""

from app import create_app
from config import config

# Create the application using your factory and config
app = create_app(config["production"])

# Optionally, you can add routes here if needed, but usually they live in your app.