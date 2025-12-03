from app.models import Mechanic
from app.extensions import ma
from marshmallow import fields, validate

# ============================================
# MECHANIC SCHEMA
# ============================================
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True
    
    mechanic_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    salary = fields.Float(required=True)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
