"""
Mechanics blueprint package.
"""

from flask import Blueprint

mechanics_bp = Blueprint("mechanics", __name__, url_prefix="/mechanics")

from . import routes  # noqa: F401, E402
