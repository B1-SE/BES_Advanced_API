"""
Service Ticket routes for the mechanic shop API.
"""
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db, limiter  # , cache  # Uncomment if using Flask-Caching
# from app.auth import token_required    # Uncomment if you implement this
from app.models.service_ticket import ServiceTicket
from app.models.mechanic import Mechanic
from app.models.customer import Customer
from app.models.inventory import InventoryItem
from app.blueprints.service_tickets.schemas import (
    service_ticket_schema,
    service_tickets_schema,
)

service_tickets_bp = Blueprint("service_tickets", __name__)

# Utility functions to DRY existence checks
def get_service_ticket_or_404(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return None, jsonify({"error": "Service ticket not found"}), 404
    return ticket, None, None

def get_mechanic_or_404(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return None, jsonify({"error": "Mechanic not found"}), 404
    return mechanic, None, None

def get_customer_or_404(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return None, jsonify({"error": "Customer not found"}), 400
    return customer, None, None

def get_inventory_item_or_404(inventory_id):
    item = db.session.get(InventoryItem, inventory_id)
    if not item:
        return None, jsonify({"error": "Inventory item not found"}), 404
    return item, None, None

@service_tickets_bp.route("/", methods=["POST"])
# @token_required  # Uncomment to require authentication
def create_service_ticket():
    """
    Create a new service ticket.
    ---
    tags:
      - Service Tickets
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [customer_id, description, service_date]
            properties:
              customer_id:
                type: integer
                description: Customer ID for this ticket
              description:
                type: string
                description: Ticket description
              service_date:
                type: string
                format: date
                description: Date of service (YYYY-MM-DD)
              mechanic_ids:
                type: array
                items:
                  type: integer
                description: List of mechanic IDs to assign
    responses:
      201:
        description: Created
        content:
          application/json:
            schema:
              $ref: '#/definitions/ServiceTicket'
      400:
        description: Invalid input
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        service_ticket_data = service_ticket_schema.load(json_data)
        customer, err, code = get_customer_or_404(service_ticket_data["customer_id"])
        if not customer:
            return err, code

        new_service_ticket = ServiceTicket(
            customer_id=service_ticket_data["customer_id"],
            description=service_ticket_data["description"],
            service_date=service_ticket_data["service_date"],
        )

        if "mechanic_ids" in service_ticket_data and service_ticket_data["mechanic_ids"]:
            for mechanic_id in service_ticket_data["mechanic_ids"]:
                mechanic, err, code = get_mechanic_or_404(mechanic_id)
                if mechanic:
                    new_service_ticket.mechanics.append(mechanic)

        db.session.add(new_service_ticket)
        db.session.commit()
        return jsonify(service_ticket_schema.dump(new_service_ticket)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@service_tickets_bp.route("/", methods=["GET"])
# @cache.cached(timeout=300)  # Uncomment to cache for 5 minutes
# @token_required
def get_service_tickets():
    """
    Get all service tickets.
    ---
    tags:
      - Service Tickets
    responses:
      200:
        description: List of all service tickets
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/definitions/ServiceTicket'
    """
    service_tickets = db.session.scalars(db.select(ServiceTicket)).all()
    return jsonify(service_tickets_schema.dump(service_tickets)), 200

@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
# @cache.cached(timeout=300)  # Uncomment to cache for 5 minutes
# @token_required
def get_service_ticket(ticket_id):
    """
    Get a single service ticket by ID.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Ticket found
        content:
          application/json:
            schema:
              $ref: '#/definitions/ServiceTicket'
      404:
        description: Ticket not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    return jsonify(service_ticket_schema.dump(ticket)), 200

@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
# @token_required
def update_service_ticket(ticket_id):
    """
    Update a service ticket by ID.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              description:
                type: string
              service_date:
                type: string
                format: date
              customer_id:
                type: integer
    responses:
      200:
        description: Updated ticket
        content:
          application/json:
            schema:
              $ref: '#/definitions/ServiceTicket'
      400:
        description: Invalid input
      404:
        description: Ticket not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        service_ticket_data = service_ticket_schema.load(json_data, partial=True)
        if "description" in service_ticket_data:
            ticket.description = service_ticket_data["description"]
        if "service_date" in service_ticket_data:
            ticket.service_date = service_ticket_data["service_date"]
        if "customer_id" in service_ticket_data:
            customer, err, code = get_customer_or_404(service_ticket_data["customer_id"])
            if not customer:
                return err, code
            ticket.customer_id = service_ticket_data["customer_id"]

        db.session.commit()
        return jsonify(service_ticket_schema.dump(ticket)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@service_tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
# @token_required
def delete_service_ticket(ticket_id):
    """
    Delete a service ticket by ID.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Ticket deleted
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Ticket not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    try:
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({"message": "Service ticket deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@service_tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
# @token_required
def edit_ticket_mechanics(ticket_id):
    """
    Bulk add and remove mechanics from a service ticket.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              add_ids:
                type: array
                items:
                  type: integer
                description: Mechanic IDs to add
              remove_ids:
                type: array
                items:
                  type: integer
                description: Mechanic IDs to remove
    responses:
      200:
        description: Mechanics updated
      207:
        description: Partial success
      400:
        description: No changes made or invalid input
      404:
        description: Ticket not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        add_ids = json_data.get("add_ids", [])
        remove_ids = json_data.get("remove_ids", [])
        if not isinstance(add_ids, list):
            return jsonify({"error": "add_ids must be a list of mechanic IDs"}), 400
        if not isinstance(remove_ids, list):
            return jsonify({"error": "remove_ids must be a list of mechanic IDs"}), 400

        changes_made = []
        errors = []

        for mechanic_id in remove_ids:
            mechanic, err, code = get_mechanic_or_404(mechanic_id)
            if not mechanic:
                errors.append(f"Mechanic with ID {mechanic_id} not found")
                continue
            if mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)
                changes_made.append(f"Removed mechanic {mechanic.name} (ID: {mechanic_id})")
            else:
                errors.append(f"Mechanic {mechanic.name} (ID: {mechanic_id}) was not assigned to this ticket")

        for mechanic_id in add_ids:
            mechanic, err, code = get_mechanic_or_404(mechanic_id)
            if not mechanic:
                errors.append(f"Mechanic with ID {mechanic_id} not found")
                continue
            if mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)
                changes_made.append(f"Added mechanic {mechanic.name} (ID: {mechanic_id})")
            else:
                errors.append(f"Mechanic {mechanic.name} (ID: {mechanic_id}) was already assigned to this ticket")

        if changes_made:
            db.session.commit()

        response_data = {
            "message": f"Processed {len(add_ids + remove_ids)} mechanic changes for ticket {ticket_id}",
            "changes_made": changes_made,
            "service_ticket": service_ticket_schema.dump(ticket),
        }
        if errors:
            response_data["errors"] = errors

        if changes_made and not errors:
            return jsonify(response_data), 200
        elif changes_made and errors:
            return jsonify(response_data), 207
        elif not changes_made and errors:
            return jsonify(response_data), 400
        else:
            return jsonify({"message": "No changes requested", "service_ticket": service_ticket_schema.dump(ticket)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to edit ticket mechanics", "message": str(e)}), 500

@service_tickets_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("20 per minute")
# @token_required
def assign_mechanic_to_ticket(ticket_id, mechanic_id):
    """
    Assign a mechanic to a service ticket.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
      - name: mechanic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Mechanic assigned to ticket
      400:
        description: Mechanic already assigned
      404:
        description: Ticket or mechanic not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    mechanic, err, code = get_mechanic_or_404(mechanic_id)
    if not mechanic:
        return err, code
    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned to this service ticket"}), 400
    try:
        ticket.mechanics.append(mechanic)
        db.session.commit()
        return jsonify({"message": f"Mechanic {mechanic.name} assigned to service ticket {ticket_id}", "service_ticket": service_ticket_schema.dump(ticket)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@service_tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
# @token_required
def remove_mechanic_from_ticket(ticket_id, mechanic_id):
    """
    Remove a mechanic from a service ticket.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
      - name: mechanic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Mechanic removed from ticket
      400:
        description: Mechanic not assigned to ticket
      404:
        description: Ticket or mechanic not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    mechanic, err, code = get_mechanic_or_404(mechanic_id)
    if not mechanic:
        return err, code
    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic is not assigned to this service ticket"}), 400
    try:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({"message": f"Mechanic {mechanic.name} removed from service ticket {ticket_id}", "service_ticket": service_ticket_schema.dump(ticket)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@service_tickets_bp.route("/<int:ticket_id>/inventory", methods=["POST"])
# @token_required
def add_inventory_to_ticket(ticket_id):
    """
    Add inventory parts to a service ticket.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              inventory_ids:
                type: array
                items:
                  type: integer
                description: Inventory item IDs to add
    responses:
      200:
        description: Inventory added to ticket
      207:
        description: Partial success
      400:
        description: No additions made or invalid input
      404:
        description: Ticket not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        inventory_ids = json_data.get("inventory_ids", [])
        if not isinstance(inventory_ids, list):
            return jsonify({"error": "inventory_ids must be a list of inventory IDs"}), 400

        changes_made = []
        errors = []

        for inventory_id in inventory_ids:
            item, err, code = get_inventory_item_or_404(inventory_id)
            if not item:
                errors.append(f"Inventory item with ID {inventory_id} not found")
                continue
            if item not in ticket.inventory_parts:
                ticket.inventory_parts.append(item)
                changes_made.append(f"Added inventory item {item.name} (ID: {inventory_id})")
            else:
                errors.append(f"Inventory item {item.name} (ID: {inventory_id}) was already added to this ticket")

        if changes_made:
            db.session.commit()

        response_data = {
            "message": f"Processed {len(inventory_ids)} inventory additions for ticket {ticket_id}",
            "changes_made": changes_made,
            "service_ticket": service_ticket_schema.dump(ticket),
        }
        if errors:
            response_data["errors"] = errors

        if changes_made and not errors:
            return jsonify(response_data), 200
        elif changes_made and errors:
            return jsonify(response_data), 207
        elif not changes_made and errors:
            return jsonify(response_data), 400
        else:
            return jsonify({"message": "No changes requested", "service_ticket": service_ticket_schema.dump(ticket)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add inventory to ticket", "message": str(e)}), 500

@service_tickets_bp.route("/<int:ticket_id>/inventory", methods=["DELETE"])
# @token_required
def remove_inventory_from_ticket(ticket_id):
    """
    Remove inventory parts from a service ticket.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              inventory_ids:
                type: array
                items:
                  type: integer
                description: Inventory item IDs to remove
    responses:
      200:
        description: Inventory removed from ticket
      207:
        description: Partial success
      400:
        description: No removals made or invalid input
      404:
        description: Ticket not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        inventory_ids = json_data.get("inventory_ids", [])
        if not isinstance(inventory_ids, list):
            return jsonify({"error": "inventory_ids must be a list of inventory IDs"}), 400

        changes_made = []
        errors = []

        for inventory_id in inventory_ids:
            item, err, code = get_inventory_item_or_404(inventory_id)
            if not item:
                errors.append(f"Inventory item with ID {inventory_id} not found")
                continue
            if item in ticket.inventory_parts:
                ticket.inventory_parts.remove(item)
                changes_made.append(f"Removed inventory item {item.name} (ID: {inventory_id})")
            else:
                errors.append(f"Inventory item {item.name} (ID: {inventory_id}) was not assigned to this ticket")

        if changes_made:
            db.session.commit()

        response_data = {
            "message": f"Processed {len(inventory_ids)} inventory removals for ticket {ticket_id}",
            "changes_made": changes_made,
            "service_ticket": service_ticket_schema.dump(ticket),
        }
        if errors:
            response_data["errors"] = errors

        if changes_made and not errors:
            return jsonify(response_data), 200
        elif changes_made and errors:
            return jsonify(response_data), 207
        elif not changes_made and errors:
            return jsonify(response_data), 400
        else:
            return jsonify({"message": "No changes requested", "service_ticket": service_ticket_schema.dump(ticket)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to remove inventory from ticket", "message": str(e)}), 500

@service_tickets_bp.route("/<int:ticket_id>/inventory/<int:inventory_id>", methods=["POST"])
# @token_required
def add_single_inventory_to_ticket(ticket_id, inventory_id):
    """
    Add a single inventory item to a service ticket.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
      - name: inventory_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Inventory item added to ticket
      400:
        description: Inventory item already assigned
      404:
        description: Ticket or inventory item not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    item, err, code = get_inventory_item_or_404(inventory_id)
    if not item:
        return err, code
    if item in ticket.inventory_parts:
        return jsonify({"message": "Inventory item already added to this service ticket"}), 400
    try:
        ticket.inventory_parts.append(item)
        db.session.commit()
        return jsonify({"message": f"Inventory item {item.name} added to service ticket {ticket_id}", "service_ticket": service_ticket_schema.dump(ticket)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@service_tickets_bp.route("/<int:ticket_id>/inventory/<int:inventory_id>", methods=["DELETE"])
# @token_required
def remove_single_inventory_from_ticket(ticket_id, inventory_id):
    """
    Remove a single inventory item from a service ticket.
    ---
    tags:
      - Service Tickets
    parameters:
      - name: ticket_id
        in: path
        required: true
        schema:
          type: integer
      - name: inventory_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Inventory item removed from ticket
      400:
        description: Inventory item not assigned to ticket
      404:
        description: Ticket or inventory item not found
    """
    ticket, err, code = get_service_ticket_or_404(ticket_id)
    if not ticket:
        return err, code
    item, err, code = get_inventory_item_or_404(inventory_id)
    if not item:
        return err, code
    if item not in ticket.inventory_parts:
        return jsonify({"message": "Inventory item is not assigned to this service ticket"}), 400
    try:
        ticket.inventory_parts.remove(item)
        db.session.commit()
        return jsonify({"message": f"Inventory item {item.name} removed from service ticket {ticket_id}", "service_ticket": service_ticket_schema.dump(ticket)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500