from app.models import Vehicle, Customer
from app.extensions import ma
from marshmallow import fields, validate

# ============================================
# VEHICLE SCHEMA
# ============================================
class VehicleSchema(ma.SQLAlchemyAutoSchema):
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

vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)
