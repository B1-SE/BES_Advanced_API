"""
Members blueprint package.
"""

from flask import Blueprint

members_bp = Blueprint("members", __name__, url_prefix="/members")

from . import routes  # noqa: F401, E402