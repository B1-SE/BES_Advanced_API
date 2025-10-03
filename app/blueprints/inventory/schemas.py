"""
Marshmallow schemas for the Inventory model.
"""
from app.extensions import ma
from app.models.inventory import InventoryItem
from marshmallow import fields, validate


class InventoryItemSchema(ma.SQLAlchemyAutoSchema):
    """Inventory item schema for serialization/deserialization"""

    class Meta:
        model = InventoryItem
        load_instance = True

    price = fields.Decimal(
        required=True, as_string=True, places=2, validate=validate.Range(min=0)
    )


inventory_item_schema = InventoryItemSchema()
inventory_items_schema = InventoryItemSchema(many=True)