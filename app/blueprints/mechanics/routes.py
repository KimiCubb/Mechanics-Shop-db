from flask import request, jsonify
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError
from app.models import db, Mechanic, service_ticket_mechanic
from app.extensions import limiter, cache
from sqlalchemy import func


# ============================================
# CRUD ROUTES FOR MECHANICS
# ============================================

# CREATE - Add a new mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")
def create_mechanic():
    """Create a new mechanic"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['name', 'email', 'address', 'phone', 'salary']):
            return jsonify({'error': 'Missing required fields: name, email, address, phone, salary'}), 400
        
        # Create new mechanic
        new_mechanic = Mechanic(
            name=data['name'],
            email=data['email'],
            address=data['address'],
            phone=data['phone'],
            salary=data['salary']
        )
        
        db.session.add(new_mechanic)
        db.session.commit()
        
        return jsonify({
            'message': 'Mechanic created successfully',
            'mechanic': mechanic_schema.dump(new_mechanic)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# READ - Get all mechanics
@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    """Get all mechanics"""
    try:
        mechanics = Mechanic.query.all()
        return jsonify({
            'message': 'Mechanics retrieved successfully',
            'count': len(mechanics),
            'mechanics': mechanics_schema.dump(mechanics)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# READ - Get a specific mechanic by ID
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanic(mechanic_id):
    """Get a specific mechanic by ID"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        
        if not mechanic:
            return jsonify({'error': f'Mechanic with ID {mechanic_id} not found'}), 404
        
        return jsonify({
            'message': 'Mechanic retrieved successfully',
            'mechanic': mechanic_schema.dump(mechanic)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# UPDATE - Update an existing mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("20 per minute")
def update_mechanic(mechanic_id):
    """Update an existing mechanic"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        
        if not mechanic:
            return jsonify({'error': f'Mechanic with ID {mechanic_id} not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            mechanic.name = data['name']
        if 'email' in data:
            mechanic.email = data['email']
        if 'address' in data:
            mechanic.address = data['address']
        if 'phone' in data:
            mechanic.phone = data['phone']
        if 'salary' in data:
            mechanic.salary = data['salary']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Mechanic updated successfully',
            'mechanic': mechanic_schema.dump(mechanic)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# DELETE - Delete a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_mechanic(mechanic_id):
    """Delete a mechanic"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        
        if not mechanic:
            return jsonify({'error': f'Mechanic with ID {mechanic_id} not found'}), 404
        
        db.session.delete(mechanic)
        db.session.commit()
        
        return jsonify({
            'message': f'Mechanic {mechanic_id} deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# READ - Get mechanics sorted by most tickets worked
@mechanics_bp.route('/top-performers', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics_by_ticket_count():
    """
    Get all mechanics ordered by the number of tickets they have worked on.
    Returns mechanics with the most tickets first.
    """
    try:
        # Query mechanics with ticket count, ordered by count descending
        mechanics_with_counts = db.session.query(
            Mechanic,
            func.count(service_ticket_mechanic.c.service_ticket_id).label('ticket_count')
        ).outerjoin(
            service_ticket_mechanic,
            Mechanic.mechanic_id == service_ticket_mechanic.c.mechanic_id
        ).group_by(
            Mechanic.mechanic_id
        ).order_by(
            func.count(service_ticket_mechanic.c.service_ticket_id).desc()
        ).all()
        
        # Format response with ticket counts
        mechanics_data = []
        for mechanic, ticket_count in mechanics_with_counts:
            mechanic_info = mechanic_schema.dump(mechanic)
            mechanic_info['ticket_count'] = ticket_count
            mechanics_data.append(mechanic_info)
        
        return jsonify({
            'message': 'Mechanics retrieved successfully, ordered by tickets worked',
            'count': len(mechanics_data),
            'mechanics': mechanics_data
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
