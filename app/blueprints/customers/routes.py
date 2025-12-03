from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from app.models import db, Customer
from app.extensions import limiter, cache


# ============================================
# CRUD ROUTES FOR CUSTOMERS
# ============================================

# CREATE - Add a new customer
@customers_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")  # Prevent spam creation
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['name', 'phone', 'email', 'address']):
            return jsonify({'error': 'Missing required fields: name, phone, email, address'}), 400
        
        # Create new customer
        new_customer = Customer(
            name=data['name'],
            phone=data['phone'],
            email=data['email'],
            address=data['address']
        )
        
        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify({
            'message': 'Customer created successfully',
            'customer': customer_schema.dump(new_customer)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# READ - Get all customers
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)  # Cache for 60 seconds
def get_customers():
    """Get all customers"""
    try:
        customers = Customer.query.all()
        return jsonify({
            'message': 'Customers retrieved successfully',
            'count': len(customers),
            'customers': customers_schema.dump(customers)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# READ - Get a specific customer by ID
@customers_bp.route('/<int:customer_id>', methods=['GET'])
@cache.cached(timeout=60)  # Cache for 60 seconds
def get_customer(customer_id):
    """Get a specific customer by ID"""
    try:
        customer = db.session.get(Customer, customer_id)
        
        if not customer:
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404
        
        return jsonify({
            'message': 'Customer retrieved successfully',
            'customer': customer_schema.dump(customer)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# UPDATE - Update an existing customer
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@limiter.limit("20 per minute")  # Rate limit updates
def update_customer(customer_id):
    """Update an existing customer"""
    try:
        customer = db.session.get(Customer, customer_id)
        
        if not customer:
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            customer.name = data['name']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'email' in data:
            customer.email = data['email']
        if 'address' in data:
            customer.address = data['address']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer_schema.dump(customer)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# DELETE - Delete a customer
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@limiter.limit("5 per minute")  # Strict limit on deletions
def delete_customer(customer_id):
    """Delete a customer"""
    try:
        customer = db.session.get(Customer, customer_id)
        
        if not customer:
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({
            'message': f'Customer {customer_id} deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400