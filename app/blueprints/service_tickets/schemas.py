from app.models import ServiceTicket, Mechanic
from app.extensions import ma
from marshmallow import fields, validate
from app.blueprints.mechanics.schemas import MechanicSchema

# ============================================
# RESPONSE SCHEMA (GET responses)
# ============================================
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    """Schema for GET responses"""
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True
    
    service_ticket_id = fields.Int(dump_only=True)
    vehicle_id = fields.Int(required=True)
    date_in = fields.DateTime(dump_only=True)
    date_out = fields.DateTime(allow_none=True)
    description = fields.Str(required=True, validate=validate.Length(min=1))
    status = fields.Str(validate=validate.OneOf(['Open', 'In Progress', 'Closed']))
    total_cost = fields.Float()
    
    # Nested mechanics for display
    mechanics = fields.Nested(MechanicSchema, many=True, dump_only=True)


# ============================================
# CREATION SCHEMA (POST requests)
# ============================================
class ServiceTicketCreateSchema(ma.Schema):
    """Schema for POST /service-tickets"""
    vehicle_id = fields.Int(required=True)
    description = fields.Str(required=True, validate=validate.Length(min=1))
    status = fields.Str(validate=validate.OneOf(['Open', 'In Progress', 'Closed']), load_default='Open')
    total_cost = fields.Float(validate=validate.Range(min=0), load_default=0.0)


# ============================================
# UPDATE SCHEMA (PUT requests)
# ============================================
class ServiceTicketUpdateSchema(ma.Schema):
    """Schema for PUT /service-tickets/:id - all fields optional"""
    vehicle_id = fields.Int()
    description = fields.Str(validate=validate.Length(min=1))
    status = fields.Str(validate=validate.OneOf(['Open', 'In Progress', 'Closed']))
    date_out = fields.DateTime(allow_none=True)
    total_cost = fields.Float(validate=validate.Range(min=0))


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
service_ticket_create_schema = ServiceTicketCreateSchema()
service_ticket_update_schema = ServiceTicketUpdateSchema()
