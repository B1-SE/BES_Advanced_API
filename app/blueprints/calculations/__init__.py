"""
Calculations blueprint package.
"""

from flask import Blueprint

calculations_bp = Blueprint("calculations", __name__, url_prefix="/calculations")

from . import routes  # noqa: F401, E402