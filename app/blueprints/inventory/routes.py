from flask import request, jsonify
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema
from marshmallow import ValidationError
from app.models import db, Inventory
from app.extensions import limiter, cache


# ============================================
# CRUD ROUTES FOR INVENTORY (PARTS)
# ============================================

# CREATE - Add a new part to inventory
@inventory_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")
def create_part():
    """Create a new part in inventory"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['name', 'price']):
            return jsonify({'error': 'Missing required fields: name, price'}), 400
        
        # Validate price is positive
        if data['price'] < 0:
            return jsonify({'error': 'Price must be a positive value'}), 400
        
        # Create new part
        new_part = Inventory(
            name=data['name'],
            price=data['price']
        )
        
        db.session.add(new_part)
        db.session.commit()
        
        return jsonify({
            'message': 'Part created successfully',
            'part': inventory_schema.dump(new_part)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# READ - Get all parts in inventory
@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_parts():
    """Get all parts in inventory"""
    try:
        parts = Inventory.query.all()
        return jsonify({
            'message': 'Inventory retrieved successfully',
            'count': len(parts),
            'parts': inventories_schema.dump(parts)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# READ - Get a specific part by ID
@inventory_bp.route('/<int:part_id>', methods=['GET'])
@cache.cached(timeout=60)
def get_part(part_id):
    """Get a specific part by ID"""
    try:
        part = db.session.get(Inventory, part_id)
        
        if not part:
            return jsonify({'error': f'Part with ID {part_id} not found'}), 404
        
        return jsonify({
            'message': 'Part retrieved successfully',
            'part': inventory_schema.dump(part)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# UPDATE - Update an existing part
@inventory_bp.route('/<int:part_id>', methods=['PUT'])
@limiter.limit("20 per minute")
def update_part(part_id):
    """Update an existing part in inventory"""
    try:
        part = db.session.get(Inventory, part_id)
        
        if not part:
            return jsonify({'error': f'Part with ID {part_id} not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            part.name = data['name']
        if 'price' in data:
            if data['price'] < 0:
                return jsonify({'error': 'Price must be a positive value'}), 400
            part.price = data['price']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Part updated successfully',
            'part': inventory_schema.dump(part)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# DELETE - Delete a part from inventory
@inventory_bp.route('/<int:part_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_part(part_id):
    """Delete a part from inventory"""
    try:
        part = db.session.get(Inventory, part_id)
        
        if not part:
            return jsonify({'error': f'Part with ID {part_id} not found'}), 404
        
        db.session.delete(part)
        db.session.commit()
        
        return jsonify({
            'message': f'Part {part_id} deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# SEARCH - Search parts by name
@inventory_bp.route('/search', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def search_parts():
    """Search parts by name"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'error': 'Search query parameter "q" is required'}), 400
        
        parts = Inventory.query.filter(Inventory.name.ilike(f'%{query}%')).all()
        
        return jsonify({
            'message': f'Search results for "{query}"',
            'count': len(parts),
            'parts': inventories_schema.dump(parts)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
