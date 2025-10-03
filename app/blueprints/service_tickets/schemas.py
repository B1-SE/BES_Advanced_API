"""
Service ticket schemas for the mechanic shop application.
"""

from app.extensions import ma
from app.models.service_ticket import ServiceTicket
from marshmallow import fields, validate


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    """Service ticket schema for serialization/deserialization"""

    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True

    status = fields.Str(
        validate=validate.OneOf(["pending", "in_progress", "completed", "cancelled"])
    )
    priority = fields.Str(validate=validate.OneOf(["low", "medium", "high", "urgent"]))


# Schema instances
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)