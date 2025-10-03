from app.extensions import ma
from app.models.mechanic import Mechanic
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    """Mechanic schema for serialization/deserialization"""

    class Meta:
        model = Mechanic
        load_instance = True

    salary = fields.Decimal(as_string=True, places=2, required=True)
    email = fields.Email(required=True, description="Unique email address for the mechanic")
    phone = fields.String(description="Mechanic's phone number")

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)