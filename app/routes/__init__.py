"""
Routes package for the mechanic shop application.
"""
from .calculations import calculations_bp
from .members import members_bp

# Export all blueprints
__all__ = ["calculations_bp", "members_bp"]
