from flask import request, jsonify
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import (
    inventory_schema, inventories_schema,
    inventory_create_schema, inventory_update_schema
)
from app.models import db, Inventory
from app.extensions import limiter, cache
from app.utils.util import validate_request, paginated_response


# ============================================
# CRUD ROUTES FOR INVENTORY (PARTS)
# ============================================

# CREATE - Add a new part to inventory
@inventory_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")
@validate_request(inventory_create_schema)
def create_part(validated_data):
    """
    Create a new part in inventory.
    Requires: name, price (must be >= 0)
    """
    try:
        # Create new part
        new_part = Inventory(
            name=validated_data['name'],
            price=validated_data['price']
        )
        
        db.session.add(new_part)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Part created successfully',
            'part': inventory_schema.dump(new_part)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# READ - Get all parts in inventory
@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_parts():
    """
    Get all parts in inventory with pagination.
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
        pagination = Inventory.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(paginated_response(
            inventories_schema,
            pagination,
            'Inventory retrieved successfully',
            data_key='parts'
        )), 200
    
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
@validate_request(inventory_update_schema)
def update_part(validated_data, part_id):
    """
    Update an existing part in inventory.
    Optional fields: name, price (must be >= 0)
    """
    try:
        part = db.session.get(Inventory, part_id)
        
        if not part:
            return jsonify({
                'status': 'error',
                'message': f'Part with ID {part_id} not found'
            }), 404
        
        # Update fields if provided
        if 'name' in validated_data:
            part.name = validated_data['name']
        if 'price' in validated_data:
            part.price = validated_data['price']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Part updated successfully',
            'part': inventory_schema.dump(part)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


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
    """
    Search parts by name with pagination.
    Query params:
        - q: Search query (required)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10, max: 100)
    """
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'error': 'Search query parameter "q" is required'}), 400
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        per_page = min(per_page, 100)
        
        # Query with pagination
        pagination = Inventory.query.filter(
            Inventory.name.ilike(f'%{query}%')
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(paginated_response(
            inventories_schema,
            pagination,
            f'Search results for "{query}"',
            data_key='parts'
        )), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
