"""
Customer routes for the mechanic shop application.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.customer import Customer
from .schemas import customer_schema, customers_schema
from app.blueprints.service_tickets.schemas import service_tickets_schema
from app.utils.util import validate_email

# Create customers blueprint
customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/", methods=["GET"])
@limiter.limit("100 per minute")
def get_all_customers():
    """Get all customers"""
    try:
        customers = db.session.scalars(db.select(Customer)).all()
        result = customers_schema.dump(customers)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/<int:customer_id>", methods=["GET"])
@limiter.limit("100 per minute")
def get_customer(customer_id):
    """Get a specific customer"""
    try:
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/", methods=["POST"])
@limiter.limit("50 per minute")
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["first_name", "last_name", "email"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate email format
        if not validate_email(data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        # Check if email already exists
        existing_customer = db.session.scalar(
            db.select(Customer).where(Customer.email == data["email"])
        )
        if existing_customer:
            return jsonify({"error": "Email already exists"}), 400

        # Create new customer
        customer = Customer(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone_number=data.get("phone_number"),
            address=data.get("address"),
        )

        # Set password if provided
        if "password" in data:
            customer.set_password(data["password"])

        # Save to database
        db.session.add(customer)
        db.session.commit()

        return jsonify(customer_schema.dump(customer)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@limiter.limit("50 per minute")
@jwt_required()
def update_customer(customer_id):
    """Update a customer (requires authentication)"""
    try:
        # Check ownership inline
        current_customer_id = get_jwt_identity()
        current_customer = db.session.get(Customer, current_customer_id)
        if current_customer.id != customer_id:
            return jsonify({"error": "Unauthorized access"}), 403

        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        data = request.get_json()

        # Validate email format if provided
        if "email" in data and not validate_email(data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        # Update fields
        if "first_name" in data:
            customer.first_name = data["first_name"]
        if "last_name" in data:
            customer.last_name = data["last_name"]
        if "email" in data:
            # Check if new email already exists (for different customer)
            existing = db.session.scalar(
                db.select(Customer).where(Customer.email == data["email"])
            )
            if existing and existing.id != customer_id:
                return jsonify({"error": "Email already exists"}), 400
            customer.email = data["email"]
        if "phone_number" in data:
            customer.phone_number = data["phone_number"]
        if "address" in data:
            customer.address = data["address"]
        if "password" in data:
            customer.set_password(data["password"])

        db.session.commit()
        return jsonify(customer_schema.dump(customer)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@limiter.limit("50 per minute")
@jwt_required()
def delete_customer(customer_id):
    """Delete a customer (requires authentication)"""
    try:
        # Check ownership inline
        current_customer_id = get_jwt_identity()
        current_customer = db.session.get(Customer, current_customer_id)
        if current_customer.id != customer_id:
            return jsonify({"error": "Unauthorized access"}), 403

        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        db.session.delete(customer)
        db.session.commit()

        return jsonify({"message": "Customer deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/login", methods=["POST"])
@limiter.limit("50 per minute")
def login():
    """Customer login"""
    try:
        data = request.get_json()

        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Email and password required"}), 400

        customer = db.session.scalar(
            db.select(Customer).where(Customer.email == data["email"])
        )

        if not customer:
            return jsonify({"error": "Invalid credentials"}), 401

        if not customer.password_hash:
            return jsonify({"error": "Account not properly configured"}), 401

        if not customer.check_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=customer.id)

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "customer": customer_schema.dump(customer),
                    "token": token,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug logging
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@customers_bp.route("/my-tickets", methods=["GET"])
@jwt_required()
def get_my_tickets():
    """Get all service tickets for the authenticated customer."""
    try:
        current_customer_id = get_jwt_identity()
        current_customer = db.session.get(Customer, current_customer_id)
        # The service_tickets relationship on the Customer model can be used directly.
        tickets = current_customer.service_tickets

        return (
            jsonify(service_tickets_schema.dump(tickets)),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500