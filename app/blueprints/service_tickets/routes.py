from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import (
    service_ticket_schema, service_tickets_schema,
    service_ticket_create_schema, service_ticket_update_schema
)
from app.models import db, ServiceTicket, Mechanic, Inventory, ServiceTicketPart
from app.extensions import limiter, cache
from app.utils.util import validate_request, paginated_response


# ============================================
# CRUD ROUTES FOR SERVICE TICKETS
# ============================================

# CREATE - Add a new service ticket
@service_tickets_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")
@validate_request(service_ticket_create_schema)
def create_service_ticket(validated_data):
    """
    Create a new service ticket.
    Requires: vehicle_id, description
    Optional: status (default: 'Open'), total_cost (default: 0.0)
    """
    try:
        # Create new service ticket
        new_ticket = ServiceTicket(
            vehicle_id=validated_data['vehicle_id'],
            description=validated_data['description'],
            status=validated_data.get('status', 'Open'),
            total_cost=validated_data.get('total_cost', 0.0)
        )
        
        db.session.add(new_ticket)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Service ticket created successfully',
            'service_ticket': service_ticket_schema.dump(new_ticket)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# READ - Get all service tickets
@service_tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_service_tickets():
    """
    Get all service tickets with pagination.
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10, max: 100)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limit per_page to prevent excessive queries
        per_page = min(per_page, 100)
        
        # Query with pagination
        pagination = ServiceTicket.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(paginated_response(
            service_ticket_schema,
            pagination,
            'Service tickets retrieved successfully',
            data_key='service_tickets'
        )), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# READ - Get a specific service ticket by ID
@service_tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@cache.cached(timeout=60)
def get_service_ticket(ticket_id):
    """Get a specific service ticket by ID"""
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        return jsonify({
            'message': 'Service ticket retrieved successfully',
            'service_ticket': service_ticket_schema.dump(ticket)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ASSIGN MECHANIC - Add a mechanic to a service ticket
@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("30 per minute")
def assign_mechanic(ticket_id, mechanic_id):
    """Assign a mechanic to a service ticket"""
    try:
        # Get the service ticket
        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        # Get the mechanic
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({'error': f'Mechanic with ID {mechanic_id} not found'}), 404
        
        # Check if mechanic is already assigned
        if mechanic in ticket.mechanics:
            return jsonify({'error': f'Mechanic {mechanic_id} is already assigned to this ticket'}), 400
        
        # Add mechanic to the service ticket
        ticket.mechanics.append(mechanic)
        db.session.commit()
        
        return jsonify({
            'message': f'Mechanic {mechanic.name} assigned to service ticket {ticket_id} successfully',
            'service_ticket': service_ticket_schema.dump(ticket)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# REMOVE MECHANIC - Remove a mechanic from a service ticket
@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("30 per minute")
def remove_mechanic(ticket_id, mechanic_id):
    """Remove a mechanic from a service ticket"""
    try:
        # Get the service ticket
        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        # Get the mechanic
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({'error': f'Mechanic with ID {mechanic_id} not found'}), 404
        
        # Check if mechanic is assigned to this ticket
        if mechanic not in ticket.mechanics:
            return jsonify({'error': f'Mechanic {mechanic_id} is not assigned to this ticket'}), 400
        
        # Remove mechanic from the service ticket
        ticket.mechanics.remove(mechanic)
        db.session.commit()
        
        return jsonify({
            'message': f'Mechanic {mechanic.name} removed from service ticket {ticket_id} successfully',
            'service_ticket': service_ticket_schema.dump(ticket)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# UPDATE - Update an existing service ticket
@service_tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@limiter.limit("20 per minute")
@validate_request(service_ticket_update_schema)
def update_service_ticket(validated_data, ticket_id):
    """
    Update an existing service ticket.
    Optional fields: vehicle_id, description, status, date_out, total_cost
    """
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        
        if not ticket:
            return jsonify({
                'status': 'error',
                'message': f'Service ticket with ID {ticket_id} not found'
            }), 404
        
        # Update fields if provided
        if 'vehicle_id' in validated_data:
            ticket.vehicle_id = validated_data['vehicle_id']
        if 'description' in validated_data:
            ticket.description = validated_data['description']
        if 'status' in validated_data:
            ticket.status = validated_data['status']
        if 'total_cost' in validated_data:
            ticket.total_cost = validated_data['total_cost']
        if 'date_out' in validated_data:
            ticket.date_out = validated_data['date_out']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Service ticket updated successfully',
            'service_ticket': service_ticket_schema.dump(ticket)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# DELETE - Delete a service ticket
@service_tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_service_ticket(ticket_id):
    """Delete a service ticket"""
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        db.session.delete(ticket)
        db.session.commit()
        
        return jsonify({
            'message': f'Service ticket {ticket_id} deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# EDIT MECHANICS - Add and remove mechanics from a ticket in one request
@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@limiter.limit("20 per minute")
def edit_ticket_mechanics(ticket_id):
    """
    Add and remove mechanics from a service ticket.
    Takes in remove_ids and add_ids arrays to batch update mechanics.
    """
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        data = request.get_json()
        
        remove_ids = data.get('remove_ids', [])
        add_ids = data.get('add_ids', [])
        
        removed_mechanics = []
        added_mechanics = []
        errors = []
        
        # Remove mechanics
        for mechanic_id in remove_ids:
            mechanic = db.session.get(Mechanic, mechanic_id)
            if not mechanic:
                errors.append(f'Mechanic with ID {mechanic_id} not found')
                continue
            if mechanic not in ticket.mechanics:
                errors.append(f'Mechanic {mechanic_id} is not assigned to this ticket')
                continue
            ticket.mechanics.remove(mechanic)
            removed_mechanics.append({'id': mechanic_id, 'name': mechanic.name})
        
        # Add mechanics
        for mechanic_id in add_ids:
            mechanic = db.session.get(Mechanic, mechanic_id)
            if not mechanic:
                errors.append(f'Mechanic with ID {mechanic_id} not found')
                continue
            if mechanic in ticket.mechanics:
                errors.append(f'Mechanic {mechanic_id} is already assigned to this ticket')
                continue
            ticket.mechanics.append(mechanic)
            added_mechanics.append({'id': mechanic_id, 'name': mechanic.name})
        
        db.session.commit()
        
        response = {
            'message': 'Service ticket mechanics updated successfully',
            'service_ticket': service_ticket_schema.dump(ticket),
            'removed_mechanics': removed_mechanics,
            'added_mechanics': added_mechanics
        }
        
        if errors:
            response['warnings'] = errors
        
        return jsonify(response), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ADD PART - Add a single part to a service ticket
@service_tickets_bp.route('/<int:ticket_id>/add-part', methods=['POST'])
@limiter.limit("30 per minute")
def add_part_to_ticket(ticket_id):
    """
    Add a single part to an existing service ticket.
    Request body:
        - part_id: ID of the part from inventory
        - quantity: Number of parts to add (optional, default: 1)
    """
    try:
        # Get the service ticket
        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        data = request.get_json()
        
        # Validate required field
        if 'part_id' not in data:
            return jsonify({'error': 'Missing required field: part_id'}), 400
        
        part_id = data['part_id']
        quantity = data.get('quantity', 1)
        
        # Validate quantity
        if quantity < 1:
            return jsonify({'error': 'Quantity must be at least 1'}), 400
        
        # Get the part from inventory
        part = db.session.get(Inventory, part_id)
        if not part:
            return jsonify({'error': f'Part with ID {part_id} not found in inventory'}), 404
        
        # Check if part is already on this ticket
        existing = ServiceTicketPart.query.filter_by(
            service_ticket_id=ticket_id,
            part_id=part_id
        ).first()
        
        if existing:
            # Update quantity if part already exists on ticket
            existing.quantity += quantity
            message = f'Updated quantity of {part.name} on ticket {ticket_id}'
        else:
            # Add new part to ticket
            ticket_part = ServiceTicketPart(
                service_ticket_id=ticket_id,
                part_id=part_id,
                quantity=quantity
            )
            db.session.add(ticket_part)
            message = f'Added {quantity}x {part.name} to ticket {ticket_id}'
        
        db.session.commit()
        
        # Get all parts on this ticket for response
        ticket_parts = ServiceTicketPart.query.filter_by(service_ticket_id=ticket_id).all()
        parts_data = []
        total_parts_cost = 0
        
        for tp in ticket_parts:
            part_info = {
                'part_id': tp.part_id,
                'name': tp.part.name,
                'price': tp.part.price,
                'quantity': tp.quantity,
                'subtotal': tp.part.price * tp.quantity
            }
            parts_data.append(part_info)
            total_parts_cost += part_info['subtotal']
        
        return jsonify({
            'message': message,
            'service_ticket_id': ticket_id,
            'parts': parts_data,
            'total_parts_cost': total_parts_cost
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# REMOVE PART - Remove a part from a service ticket
@service_tickets_bp.route('/<int:ticket_id>/remove-part/<int:part_id>', methods=['DELETE'])
@limiter.limit("30 per minute")
def remove_part_from_ticket(ticket_id, part_id):
    """Remove a part from a service ticket"""
    try:
        # Get the service ticket
        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        # Find the part on this ticket
        ticket_part = ServiceTicketPart.query.filter_by(
            service_ticket_id=ticket_id,
            part_id=part_id
        ).first()
        
        if not ticket_part:
            return jsonify({'error': f'Part {part_id} is not on ticket {ticket_id}'}), 404
        
        part_name = ticket_part.part.name
        db.session.delete(ticket_part)
        db.session.commit()
        
        return jsonify({
            'message': f'Removed {part_name} from ticket {ticket_id}'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# GET PARTS - Get all parts on a service ticket
@service_tickets_bp.route('/<int:ticket_id>/parts', methods=['GET'])
@cache.cached(timeout=30)
def get_ticket_parts(ticket_id):
    """Get all parts on a service ticket"""
    try:
        # Get the service ticket
        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        # Get all parts on this ticket
        ticket_parts = ServiceTicketPart.query.filter_by(service_ticket_id=ticket_id).all()
        
        parts_data = []
        total_parts_cost = 0
        
        for tp in ticket_parts:
            part_info = {
                'part_id': tp.part_id,
                'name': tp.part.name,
                'price': tp.part.price,
                'quantity': tp.quantity,
                'subtotal': tp.part.price * tp.quantity
            }
            parts_data.append(part_info)
            total_parts_cost += part_info['subtotal']
        
        return jsonify({
            'message': f'Parts for ticket {ticket_id} retrieved successfully',
            'service_ticket_id': ticket_id,
            'count': len(parts_data),
            'parts': parts_data,
            'total_parts_cost': total_parts_cost
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
