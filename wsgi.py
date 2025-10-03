"""
WSGI entry point for the Mechanic Shop Flask application.
This file is used by production WSGI servers like Gunicorn.
"""
import os

from app import create_app
from config import config

config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config[config_name])

