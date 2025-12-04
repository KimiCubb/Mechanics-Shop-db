from app.models import Mechanic
from app.extensions import ma
from marshmallow import fields, validate

# ============================================
# RESPONSE SCHEMA (GET responses)
# ============================================
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    """Schema for GET responses"""
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True
    
    mechanic_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    salary = fields.Float(required=True, validate=validate.Range(min=0))


# ============================================
# CREATION SCHEMA (POST requests)
# ============================================
class MechanicCreateSchema(ma.Schema):
    """Schema for POST /mechanics"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    salary = fields.Float(required=True, validate=validate.Range(min=0))


# ============================================
# UPDATE SCHEMA (PUT requests)
# ============================================
class MechanicUpdateSchema(ma.Schema):
    """Schema for PUT /mechanics/:id - all fields optional"""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    email = fields.Email()
    address = fields.Str(validate=validate.Length(min=1, max=255))
    phone = fields.Str(validate=validate.Length(min=10, max=20))
    salary = fields.Float(validate=validate.Range(min=0))


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_create_schema = MechanicCreateSchema()
mechanic_update_schema = MechanicUpdateSchema()

