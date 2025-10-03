"""
Service Tickets blueprint initialization.
"""
from flask import Blueprint

service_tickets_bp = Blueprint(
    "service_tickets", __name__, url_prefix="/service-tickets"
)

from . import routes  # noqa: F401, E402
