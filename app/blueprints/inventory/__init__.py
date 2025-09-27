"""
Inventory blueprint initialization.
"""

from flask import Blueprint

inventory_bp = Blueprint("inventory", __name__)

# Import routes after blueprint initialization to avoid circular imports
from . import routes  # noqa: F401, E402