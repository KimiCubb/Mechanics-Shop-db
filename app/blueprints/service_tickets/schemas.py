from app.models import ServiceTicket, Mechanic
from app.extensions import ma
from marshmallow import fields, validate
from app.blueprints.mechanics.schemas import MechanicSchema

# ============================================
# SERVICE TICKET SCHEMA
# ============================================
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
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

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
