"""
Main entry point for the Mechanic Shop Flask application for production.
This file is used by Gunicorn to serve the application.
"""

from app import create_app
from config import config

app = create_app(config["production"])