from flask import request, jsonify
from app.blueprints.vehicles import vehicles_bp
from app.blueprints.vehicles.schemas import vehicle_schema, vehicles_schema
from marshmallow import ValidationError
from app.models import db, Vehicle, Customer
from app.extensions import limiter, cache


# ============================================
# CRUD ROUTES FOR VEHICLES
# ============================================

# CREATE - Add a new vehicle
@vehicles_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")
def create_vehicle():
    """Create a new vehicle"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['customer_id', 'make', 'model', 'year', 'vin']):
            return jsonify({'error': 'Missing required fields: customer_id, make, model, year, vin'}), 400
        
        # Verify customer exists
        customer = db.session.get(Customer, data['customer_id'])
        if not customer:
            return jsonify({'error': f'Customer with ID {data["customer_id"]} not found'}), 404
        
        # Check if VIN already exists
        existing_vehicle = Vehicle.query.filter_by(vin=data['vin']).first()
        if existing_vehicle:
            return jsonify({'error': f'Vehicle with VIN {data["vin"]} already exists'}), 400
        
        # Create new vehicle
        new_vehicle = Vehicle(
            customer_id=data['customer_id'],
            make=data['make'],
            model=data['model'],
            year=data['year'],
            vin=data['vin']
        )
        
        db.session.add(new_vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle created successfully',
            'vehicle': vehicle_schema.dump(new_vehicle)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# READ - Get all vehicles
@vehicles_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_vehicles():
    """Get all vehicles"""
    try:
        vehicles = Vehicle.query.all()
        return jsonify({
            'message': 'Vehicles retrieved successfully',
            'count': len(vehicles),
            'vehicles': vehicles_schema.dump(vehicles)
        }), 200
    
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
@cache.cached(timeout=60)
def get_customer_vehicles(customer_id):
    """Get all vehicles for a specific customer"""
    try:
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404
        
        vehicles = Vehicle.query.filter_by(customer_id=customer_id).all()
        return jsonify({
            'message': f'Vehicles for customer {customer_id} retrieved successfully',
            'count': len(vehicles),
            'vehicles': vehicles_schema.dump(vehicles)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# UPDATE - Update an existing vehicle
@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
@limiter.limit("20 per minute")
def update_vehicle(vehicle_id):
    """Update an existing vehicle"""
    try:
        vehicle = db.session.get(Vehicle, vehicle_id)
        
        if not vehicle:
            return jsonify({'error': f'Vehicle with ID {vehicle_id} not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'make' in data:
            vehicle.make = data['make']
        if 'model' in data:
            vehicle.model = data['model']
        if 'year' in data:
            vehicle.year = data['year']
        if 'vin' in data:
            # Check if new VIN already exists (and it's not this vehicle)
            existing = Vehicle.query.filter_by(vin=data['vin']).first()
            if existing and existing.vehicle_id != vehicle_id:
                return jsonify({'error': f'Vehicle with VIN {data["vin"]} already exists'}), 400
            vehicle.vin = data['vin']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle_schema.dump(vehicle)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


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
