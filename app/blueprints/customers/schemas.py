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
        exclude = ('password',)  # Exclude password from output
    
    customer_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))  # Load only, never dump


# Login Schema - only email and password
class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()