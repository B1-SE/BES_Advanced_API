"""
Inventory routes for the mechanic shop application.
"""
from flask import request, jsonify
from app.extensions import db, limiter, cache
from app.models.inventory import InventoryItem
from .schemas import inventory_item_schema, inventory_items_schema
from decimal import Decimal, InvalidOperation
from . import inventory_bp
# from app.auth import token_required  # Uncomment if you implement authentication

@inventory_bp.route("/", methods=["GET"])
@cache.cached(timeout=300)
@limiter.limit("100 per minute")
def get_all_inventory():
    """
    Get all inventory items.
    ---
    tags:
      - Inventory
    summary: Retrieve all inventory items
    responses:
      200:
        description: List of inventory items
        schema:
          type: object
          properties:
            inventory:
              type: array
              items:
                $ref: '#/definitions/InventoryItem'
            count:
              type: integer
      500:
        description: Server error
    """
    try:
        items = db.session.scalars(db.select(InventoryItem)).all()
        result = inventory_items_schema.dump(items)
        return jsonify({"inventory": result, "count": len(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/<int:item_id>", methods=["GET"])
@cache.cached(timeout=300)
@limiter.limit("100 per minute")
def get_inventory_item(item_id):
    """
    Get a specific inventory item by ID.
    ---
    tags:
      - Inventory
    summary: Retrieve an inventory item by ID
    parameters:
      - name: item_id
        in: path
        required: true
        type: integer
        description: The ID of the inventory item
    responses:
      200:
        description: Inventory item found
        schema:
          $ref: '#/definitions/InventoryItem'
      404:
        description: Inventory item not found
      500:
        description: Server error
    """
    try:
        item = db.session.get(InventoryItem, item_id)
        if not item:
            return jsonify({"error": "Inventory item not found"}), 404
        return jsonify(inventory_item_schema.dump(item)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/", methods=["POST"])
# @token_required  # Uncomment if you implement authentication
@limiter.limit("50 per minute")
def create_inventory_item():
    """
    Create a new inventory item.
    ---
    tags:
      - Inventory
    summary: Create inventory item
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [name, quantity, price]
            properties:
              name:
                type: string
                description: Item name
              description:
                type: string
                description: Item description
              quantity:
                type: integer
                description: Quantity in stock
              price:
                type: number
                format: float
                description: Item price
              supplier:
                type: string
                description: Supplier name
              category:
                type: string
                description: Item category
              reorder_level:
                type: integer
                description: Reorder level threshold
    responses:
      201:
        description: Inventory item created
        schema:
          $ref: '#/definitions/InventoryItem'
      400:
        description: Invalid input
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["name", "quantity", "price"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate numeric fields
        try:
            quantity = int(data["quantity"])
            if quantity < 0:
                return jsonify({"error": "Quantity must be non-negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid quantity format"}), 400

        try:
            price = Decimal(str(data["price"]))
            if price < 0:
                return jsonify({"error": "Price must be non-negative"}), 400
        except (InvalidOperation, ValueError, TypeError):
            return jsonify({"error": "Invalid price format"}), 400

        # Create new inventory item
        item = InventoryItem(
            name=data["name"],
            description=data.get("description"),
            quantity=quantity,
            price=price,
            supplier=data.get("supplier"),
            category=data.get("category"),
            reorder_level=data.get("reorder_level", 0),
        )

        # Save to database
        db.session.add(item)
        db.session.commit()

        return jsonify(inventory_item_schema.dump(item)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/<int:item_id>", methods=["PUT"])
# @token_required  # Uncomment if you implement authentication
@limiter.limit("50 per minute")
def update_inventory_item(item_id):
    """
    Update an inventory item by ID.
    ---
    tags:
      - Inventory
    summary: Update inventory item
    parameters:
      - name: item_id
        in: path
        required: true
        type: integer
        description: The ID of the inventory item
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
              description:
                type: string
              quantity:
                type: integer
              price:
                type: number
                format: float
              supplier:
                type: string
              category:
                type: string
              reorder_level:
                type: integer
    responses:
      200:
        description: Inventory item updated
        schema:
          $ref: '#/definitions/InventoryItem'
      400:
        description: Invalid input
      404:
        description: Inventory item not found
      500:
        description: Server error
    """
    try:
        item = db.session.get(InventoryItem, item_id)
        if not item:
            return jsonify({"error": "Inventory item not found"}), 404

        data = request.get_json()

        # Update fields with validation
        if "name" in data:
            item.name = data["name"]
        if "description" in data:
            item.description = data["description"]
        if "quantity" in data:
            try:
                quantity = int(data["quantity"])
                if quantity < 0:
                    return jsonify({"error": "Quantity must be non-negative"}), 400
                item.quantity = quantity
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid quantity format"}), 400
        if "price" in data:
            try:
                price = Decimal(str(data["price"]))
                if price < 0:
                    return jsonify({"error": "Price must be non-negative"}), 400
                item.price = price
            except (InvalidOperation, ValueError, TypeError):
                return jsonify({"error": "Invalid price format"}), 400
        if "supplier" in data:
            item.supplier = data["supplier"]
        if "category" in data:
            item.category = data["category"]
        if "reorder_level" in data:
            item.reorder_level = data["reorder_level"]

        db.session.commit()
        return jsonify(inventory_item_schema.dump(item)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
# @token_required  # Uncomment if you implement authentication
@limiter.limit("50 per minute")
def delete_inventory_item(item_id):
    """
    Delete an inventory item by ID.
    ---
    tags:
      - Inventory
    summary: Delete inventory item
    parameters:
      - name: item_id
        in: path
        required: true
        type: integer
        description: The ID of the inventory item
    responses:
      200:
        description: Inventory item deleted
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Inventory item not found
      500:
        description: Server error
    """
    try:
        item = db.session.get(InventoryItem, item_id)
        if not item:
            return jsonify({"error": "Inventory item not found"}), 404

        db.session.delete(item)
        db.session.commit()

        return jsonify({"message": "Inventory item deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500