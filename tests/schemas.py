"""
Schemas for the service ticket blueprint.
"""

from app.extensions import ma
from app.models.service_ticket import ServiceTicket
from app.blueprints.mechanics.schemas import MechanicSchema
from app.schemas.inventory import InventorySchema


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    """Schema for a single service ticket."""

    mechanics = ma.Nested(MechanicSchema, many=True, dump_only=True)
    inventory_parts = ma.Nested(InventorySchema, many=True, dump_only=True)

    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)