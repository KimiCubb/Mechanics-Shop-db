from app.models import Customer
from app.extensions import ma
from marshmallow import fields, validate

# ============================================
# RESPONSE SCHEMA (Never includes password)
# ============================================
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """Schema for GET responses - never includes password"""
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True
        exclude = ('password',)
    
    customer_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=1, max=255))


# ============================================
# CREATION SCHEMA (Requires password)
# ============================================
class CustomerCreateSchema(ma.Schema):
    """Schema for POST /customers - requires password"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))


# ============================================
# UPDATE SCHEMA (Password optional)
# ============================================
class CustomerUpdateSchema(ma.Schema):
    """Schema for PUT /customers/:id - all fields optional including password"""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    phone = fields.Str(validate=validate.Length(min=10, max=20))
    email = fields.Email()
    address = fields.Str(validate=validate.Length(min=1, max=255))
    password = fields.Str(validate=validate.Length(min=6, max=100))


# ============================================
# LOGIN SCHEMA (Only email and password)
# ============================================
class LoginSchema(ma.Schema):
    """Schema for POST /customers/login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


# Instantiate schemas
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_create_schema = CustomerCreateSchema()
customer_update_schema = CustomerUpdateSchema()
login_schema = LoginSchema()