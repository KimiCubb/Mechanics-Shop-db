from app.models import Inventory, ServiceTicketPart
from app.extensions import ma
from marshmallow import fields, validate


# ============================================
# RESPONSE SCHEMA (GET responses)
# ============================================
class InventorySchema(ma.SQLAlchemyAutoSchema):
    """Schema for Inventory (Parts) model - GET responses"""
    class Meta:
        model = Inventory
        load_instance = True
        include_fk = True
    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Float(required=True, validate=validate.Range(min=0))


# ============================================
# CREATION SCHEMA (POST requests)
# ============================================
class InventoryCreateSchema(ma.Schema):
    """Schema for POST /inventory"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Float(required=True, validate=validate.Range(min=0))


# ============================================
# UPDATE SCHEMA (PUT requests)
# ============================================
class InventoryUpdateSchema(ma.Schema):
    """Schema for PUT /inventory/:id - all fields optional"""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    price = fields.Float(validate=validate.Range(min=0))


# ============================================
# SERVICE TICKET PART SCHEMA
# ============================================
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
inventory_create_schema = InventoryCreateSchema()
inventory_update_schema = InventoryUpdateSchema()
service_ticket_part_schema = ServiceTicketPartSchema()
service_ticket_parts_schemas = ServiceTicketPartSchema(many=True)
