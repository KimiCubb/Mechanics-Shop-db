from app.models import Vehicle, Customer
from app.extensions import ma
from marshmallow import fields, validate

# ============================================
# RESPONSE SCHEMA (GET responses)
# ============================================
class VehicleSchema(ma.SQLAlchemyAutoSchema):
    """Schema for GET responses"""
    class Meta:
        model = Vehicle
        load_instance = True
        include_fk = True
    
    vehicle_id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True)
    make = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    model = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    year = fields.Int(required=True)
    vin = fields.Str(required=True, validate=validate.Length(min=17, max=17))
    license_plate = fields.Str(required=False, validate=validate.Length(max=20))


# ============================================
# CREATION SCHEMA (POST requests)
# ============================================
class VehicleCreateSchema(ma.Schema):
    """Schema for POST /vehicles"""
    customer_id = fields.Int(required=True)
    make = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    model = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    year = fields.Int(required=True)
    vin = fields.Str(required=True, validate=validate.Length(min=17, max=17))
    license_plate = fields.Str(required=False, validate=validate.Length(max=20))


# ============================================
# UPDATE SCHEMA (PUT requests)
# ============================================
class VehicleUpdateSchema(ma.Schema):
    """Schema for PUT /vehicles/:id - all fields optional"""
    customer_id = fields.Int()
    make = fields.Str(validate=validate.Length(min=1, max=50))
    model = fields.Str(validate=validate.Length(min=1, max=50))
    year = fields.Int()
    vin = fields.Str(validate=validate.Length(min=17, max=17))
    license_plate = fields.Str(validate=validate.Length(max=20))


vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)
vehicle_create_schema = VehicleCreateSchema()
vehicle_update_schema = VehicleUpdateSchema()

