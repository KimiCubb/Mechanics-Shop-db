from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema
from marshmallow import ValidationError
from app.models import db, ServiceTicket, Mechanic
from app.extensions import limiter, cache


# ============================================
# CRUD ROUTES FOR SERVICE TICKETS
# ============================================

# CREATE - Add a new service ticket
@service_tickets_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")
def create_service_ticket():
    """Create a new service ticket"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['vehicle_id', 'description']):
            return jsonify({'error': 'Missing required fields: vehicle_id, description'}), 400
        
        # Create new service ticket
        new_ticket = ServiceTicket(
            vehicle_id=data['vehicle_id'],
            description=data['description'],
            status=data.get('status', 'Open'),
            total_cost=data.get('total_cost', 0.0)
        )
        
        db.session.add(new_ticket)
        db.session.commit()
        
        return jsonify({
            'message': 'Service ticket created successfully',
            'service_ticket': service_ticket_schema.dump(new_ticket)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# READ - Get all service tickets
@service_tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_service_tickets():
    """Get all service tickets"""
    try:
        tickets = ServiceTicket.query.all()
        return jsonify({
            'message': 'Service tickets retrieved successfully',
            'count': len(tickets),
            'service_tickets': service_tickets_schema.dump(tickets)
        }), 200
    
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
def update_service_ticket(ticket_id):
    """Update an existing service ticket"""
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        
        if not ticket:
            return jsonify({'error': f'Service ticket with ID {ticket_id} not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'description' in data:
            ticket.description = data['description']
        if 'status' in data:
            ticket.status = data['status']
        if 'total_cost' in data:
            ticket.total_cost = data['total_cost']
        if 'date_out' in data:
            from datetime import datetime
            ticket.date_out = datetime.fromisoformat(data['date_out'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Service ticket updated successfully',
            'service_ticket': service_ticket_schema.dump(ticket)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


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
