from flask import request, jsonify
from app.blueprints.vehicles import vehicles_bp
from app.blueprints.vehicles.schemas import (
    vehicle_schema, vehicles_schema,
    vehicle_create_schema, vehicle_update_schema
)
from app.models import db, Vehicle, Customer
from app.extensions import limiter, cache
from app.utils.util import validate_request, paginated_response


# ============================================
# CRUD ROUTES FOR VEHICLES
# ============================================

# CREATE - Add a new vehicle
@vehicles_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")
@validate_request(vehicle_create_schema)
def create_vehicle(validated_data):
    """
    Create a new vehicle.
    Requires: customer_id, make, model, year, vin
    Optional: license_plate
    """
    try:
        # Verify customer exists
        customer = db.session.get(Customer, validated_data['customer_id'])
        if not customer:
            return jsonify({
                'status': 'error',
                'message': f'Customer with ID {validated_data["customer_id"]} not found'
            }), 404
        
        # Check if VIN already exists
        existing_vehicle = Vehicle.query.filter_by(vin=validated_data['vin']).first()
        if existing_vehicle:
            return jsonify({
                'status': 'error',
                'message': f'Vehicle with VIN {validated_data["vin"]} already exists'
            }), 400
        
        # Check if license_plate already exists (if provided)
        if 'license_plate' in validated_data and validated_data['license_plate']:
            existing_plate = Vehicle.query.filter_by(license_plate=validated_data['license_plate']).first()
            if existing_plate:
                return jsonify({
                    'status': 'error',
                    'message': f'Vehicle with license plate {validated_data["license_plate"]} already exists'
                }), 400
        
        # Create new vehicle
        new_vehicle = Vehicle(
            customer_id=validated_data['customer_id'],
            make=validated_data['make'],
            model=validated_data['model'],
            year=validated_data['year'],
            vin=validated_data['vin'],
            license_plate=validated_data.get('license_plate')
        )
        
        db.session.add(new_vehicle)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Vehicle created successfully',
            'vehicle': vehicle_schema.dump(new_vehicle)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# READ - Get all vehicles
@vehicles_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_vehicles():
    """
    Get all vehicles with pagination.
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
        pagination = Vehicle.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(paginated_response(
            vehicle_schema,
            pagination,
            'Vehicles retrieved successfully',
            data_key='vehicles'
        )), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# READ - Get a specific vehicle by ID
@vehicles_bp.route('/<int:vehicle_id>', methods=['GET'])
@cache.cached(timeout=60)
def get_vehicle(vehicle_id):
    """Get a specific vehicle by ID"""
    try:
        vehicle = db.session.get(Vehicle, vehicle_id)
        
        if not vehicle:
            return jsonify({'error': f'Vehicle with ID {vehicle_id} not found'}), 404
        
        return jsonify({
            'message': 'Vehicle retrieved successfully',
            'vehicle': vehicle_schema.dump(vehicle)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# READ - Get all vehicles for a specific customer
@vehicles_bp.route('/customer/<int:customer_id>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_customer_vehicles(customer_id):
    """
    Get all vehicles for a specific customer with pagination.
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10, max: 100)
    """
    try:
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        per_page = min(per_page, 100)
        
        pagination = Vehicle.query.filter_by(customer_id=customer_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(paginated_response(
            vehicle_schema,
            pagination,
            f'Vehicles for customer {customer_id} retrieved successfully',
            data_key='vehicles'
        )), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# UPDATE - Update an existing vehicle
@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
@limiter.limit("20 per minute")
@validate_request(vehicle_update_schema)
def update_vehicle(validated_data, vehicle_id):
    """
    Update an existing vehicle.
    Optional fields: customer_id, make, model, year, vin, license_plate
    """
    try:
        vehicle = db.session.get(Vehicle, vehicle_id)
        
        if not vehicle:
            return jsonify({
                'status': 'error',
                'message': f'Vehicle with ID {vehicle_id} not found'
            }), 404
        
        # Update fields if provided
        if 'customer_id' in validated_data:
            # Verify customer exists
            customer = db.session.get(Customer, validated_data['customer_id'])
            if not customer:
                return jsonify({
                    'status': 'error',
                    'message': f'Customer with ID {validated_data["customer_id"]} not found'
                }), 404
            vehicle.customer_id = validated_data['customer_id']
        
        if 'make' in validated_data:
            vehicle.make = validated_data['make']
        if 'model' in validated_data:
            vehicle.model = validated_data['model']
        if 'year' in validated_data:
            vehicle.year = validated_data['year']
        if 'vin' in validated_data:
            # Check if new VIN already exists (and it's not this vehicle)
            existing = Vehicle.query.filter_by(vin=validated_data['vin']).first()
            if existing and existing.vehicle_id != vehicle_id:
                return jsonify({
                    'status': 'error',
                    'message': f'Vehicle with VIN {validated_data["vin"]} already exists'
                }), 400
            vehicle.vin = validated_data['vin']
        if 'license_plate' in validated_data:
            # Check if new license_plate already exists (and it's not this vehicle)
            if validated_data['license_plate']:
                existing = Vehicle.query.filter_by(license_plate=validated_data['license_plate']).first()
                if existing and existing.vehicle_id != vehicle_id:
                    return jsonify({
                        'status': 'error',
                        'message': f'Vehicle with license plate {validated_data["license_plate"]} already exists'
                    }), 400
            vehicle.license_plate = validated_data['license_plate']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle_schema.dump(vehicle)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# DELETE - Delete a vehicle
@vehicles_bp.route('/<int:vehicle_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_vehicle(vehicle_id):
    """Delete a vehicle"""
    try:
        vehicle = db.session.get(Vehicle, vehicle_id)
        
        if not vehicle:
            return jsonify({'error': f'Vehicle with ID {vehicle_id} not found'}), 404
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': f'Vehicle {vehicle_id} deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
