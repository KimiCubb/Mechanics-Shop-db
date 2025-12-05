from flask import request, jsonify
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import (
    mechanic_schema, mechanics_schema,
    mechanic_create_schema, mechanic_update_schema
)
from app.models import db, Mechanic, service_ticket_mechanic
from app.extensions import limiter, cache
from app.utils.util import validate_request, paginated_response
from sqlalchemy import func


# ============================================
# CRUD ROUTES FOR MECHANICS
# ============================================

# CREATE - Add a new mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")
@validate_request(mechanic_create_schema)
def create_mechanic(validated_data):
    """
    Create a new mechanic.
    Requires: name, email, address, phone, salary (must be >= 0)
    """
    try:
        # Create new mechanic
        new_mechanic = Mechanic(
            name=validated_data['name'],
            email=validated_data['email'],
            address=validated_data['address'],
            phone=validated_data['phone'],
            salary=validated_data['salary']
        )
        
        db.session.add(new_mechanic)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Mechanic created successfully',
            'mechanic': mechanic_schema.dump(new_mechanic)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# READ - Get all mechanics
@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_mechanics():
    """
    Get all mechanics with pagination.
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
        pagination = Mechanic.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(paginated_response(
            mechanic_schema,
            pagination,
            'Mechanics retrieved successfully',
            data_key='mechanics'
        )), 200
    
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
@validate_request(mechanic_update_schema)
def update_mechanic(validated_data, mechanic_id):
    """
    Update an existing mechanic.
    Optional fields: name, email, address, phone, salary (must be >= 0)
    """
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        
        if not mechanic:
            return jsonify({
                'status': 'error',
                'message': f'Mechanic with ID {mechanic_id} not found'
            }), 404
        
        # Update fields if provided
        if 'name' in validated_data:
            mechanic.name = validated_data['name']
        if 'email' in validated_data:
            mechanic.email = validated_data['email']
        if 'address' in validated_data:
            mechanic.address = validated_data['address']
        if 'phone' in validated_data:
            mechanic.phone = validated_data['phone']
        if 'salary' in validated_data:
            mechanic.salary = validated_data['salary']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Mechanic updated successfully',
            'mechanic': mechanic_schema.dump(mechanic)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


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
