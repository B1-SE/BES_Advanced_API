from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.inventory import InventoryItem

class InventoryItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = InventoryItem
        load_instance = True

inventory_item_schema = InventoryItemSchema()
inventory_items_schema = InventoryItemSchema(many=True)