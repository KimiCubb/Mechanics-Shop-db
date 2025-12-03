from app.models import Customer
from app.extensions import ma
from marshmallow import fields, validate

# ============================================
# MARSHMALLOW SCHEMAS
# ============================================
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True  # Include foreign keys in serialization
        exclude = ()  # Exclude any fields if needed
    
    customer_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=1, max=255))

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)