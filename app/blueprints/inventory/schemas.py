from app.models import Inventory, ServiceTicketPart
from app.extensions import ma
from marshmallow import fields, validate


# ============================================
# MARSHMALLOW SCHEMAS FOR INVENTORY
# ============================================

class InventorySchema(ma.SQLAlchemyAutoSchema):
    """Schema for Inventory (Parts) model"""
    class Meta:
        model = Inventory
        load_instance = True
        include_fk = True
    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Float(required=True, validate=validate.Range(min=0))


class ServiceTicketPartSchema(ma.SQLAlchemyAutoSchema):
    """Schema for ServiceTicketPart junction table (includes quantity)"""
    class Meta:
        model = ServiceTicketPart
        load_instance = True
        include_fk = True
    
    service_ticket_id = fields.Int(required=True)
    part_id = fields.Int(required=True)
    quantity = fields.Int(required=False, validate=validate.Range(min=1), load_default=1)
    
    # Nested part details for output
    part = fields.Nested(InventorySchema, dump_only=True)


# Schema instances
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
service_ticket_part_schema = ServiceTicketPartSchema()
service_ticket_parts_schema = ServiceTicketPartSchema(many=True)
