"""
WSGI entry point for the Mechanic Shop Flask application.
This file is used by production WSGI servers like Gunicorn.
"""

from app import create_app
from config import config

app = create_app(config["production"])