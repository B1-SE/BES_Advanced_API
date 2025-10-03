"""
Marshmallow schemas for the Inventory model.
"""

from app.extensions import ma
from app.models.inventory import InventoryItem


class InventoryItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InventoryItem
        load_instance = True

inventory_item_schema = InventoryItemSchema()
inventory_items_schema = InventoryItemSchema(many=True)