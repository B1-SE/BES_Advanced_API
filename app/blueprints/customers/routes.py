"""
Customer routes for the mechanic shop API.
"""
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.customer import Customer

customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/", methods=["GET"])
def get_customers():
    """Get all customers."""
    customers = db.session.scalars(db.select(Customer)).all()
    return jsonify([customer.to_dict() for customer in customers]), 200

@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """Get a customer by ID."""
    customer = db.session.get(Customer, customer_id)
    if customer:
        return jsonify(customer.to_dict()), 200
    return jsonify({"error": "Customer not found"}), 404

@customers_bp.route("/", methods=["POST"])
def create_customer():
    """Create a new customer."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    required_fields = ["first_name", "last_name", "email", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    if db.session.execute(db.select(Customer).filter_by(email=data["email"])).scalar():
        return jsonify({"error": "Email already registered"}), 409

    customer = Customer(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        phone_number=data.get("phone_number"),
        address=data.get("address"),
    )
    customer.set_password(data["password"])
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201

@customers_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    """Update a customer by ID."""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    for field in ["first_name", "last_name", "email", "phone_number", "address"]:
        if field in data:
            setattr(customer, field, data[field])
    if "password" in data:
        customer.set_password(data["password"])
    db.session.commit()
    return jsonify(customer.to_dict()), 200

@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    """Delete a customer by ID."""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"}), 200