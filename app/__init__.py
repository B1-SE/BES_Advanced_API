"""
Customer blueprint package.
"""

# The blueprint is now defined in routes.py to avoid circular imports.
from .routes import customers_bp  # noqa: F401