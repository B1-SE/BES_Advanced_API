"""
Service ticket schemas for the mechanic shop application.
"""

from app.extensions import ma
from app.models.service_ticket import ServiceTicket
from marshmallow import fields, validate
from app.models.mechanic import Mechanic

# Minimal Mechanic schema for nesting to avoid circular imports
class MechanicSummarySchema(ma.SQLAlchemyAutoSchema):
    """Summary schema for nested mechanic output in service tickets."""
    class Meta:
        model = Mechanic
        load_instance = True
        fields = ("id", "name", "email")  # Include other minimal fields as needed

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    """Service ticket schema for serialization/deserialization"""

    status = fields.Str(
        required=True,
        validate=validate.OneOf(["pending", "in_progress", "completed", "cancelled"]),
        description="The status of the service ticket."
    )
    priority = fields.Str(
        required=True,
        validate=validate.OneOf(["low", "medium", "high", "urgent"]),
        description="The priority level of the service ticket."
    )

    # Nested mechanics (assigned to this ticket)
    mechanics = fields.Nested(
        MechanicSummarySchema,
        many=True,
        dump_only=True,
        description="List of mechanics assigned to this service ticket."
    )

    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True

# Schema instances
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)