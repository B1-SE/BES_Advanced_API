"""
Marshmallow schemas for the Customer model.
"""

from app.extensions import ma
from app.models.customer import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing and deserializing a Customer."""

    class Meta:
        model = Customer
        load_instance = True
        exclude = ("password_hash",)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)