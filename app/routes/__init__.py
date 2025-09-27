"""
Routes package for the mechanic shop application.
"""

from .customers import customers_bp
from .calculations import calculations_bp
from .members import members_bp

# Export all blueprints
__all__ = ["customers_bp", "calculations_bp", "members_bp"]
