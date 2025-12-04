from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import (
    customer_schema, customers_schema, login_schema,
    customer_create_schema, customer_update_schema
)
from app.models import db, Customer, Vehicle, ServiceTicket
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required, validate_request, paginated_response
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================
# AUTHENTICATION ROUTES
# ============================================

# LOGIN - Authenticate customer and return token
@customers_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Strict limit on login attempts
@validate_request(login_schema)
def login(validated_data):
    """
    Customer login route.
    Validates email and password using schema, returns a JWT token on success.
    """
    try:
        email = validated_data['email']
        password = validated_data['password']
        
        # Query customer by email
        customer = Customer.query.filter_by(email=email).first()
        
        # Use check_password_hash for secure password comparison
        if customer and check_password_hash(customer.password, password):
            # Generate token using customer_id
            auth_token = encode_token(customer.customer_id)
            
            return jsonify({
                'status': 'success',
                'message': 'Successfully logged in',
                'auth_token': auth_token,
                'customer_id': customer.customer_id
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# GET MY TICKETS - Get service tickets for authenticated customer
@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    """
    Get all service tickets related to the authenticated customer.
    Requires Bearer Token authorization.
    The customer_id is received from the @token_required wrapper.
    """
    try:
        # Verify customer exists
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get all vehicles for this customer
        vehicles = Vehicle.query.filter_by(customer_id=customer_id).all()
        vehicle_ids = [v.vehicle_id for v in vehicles]
        
        # Get all service tickets for those vehicles
        tickets = ServiceTicket.query.filter(ServiceTicket.vehicle_id.in_(vehicle_ids)).all()
        
        # Format response with ticket details
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'service_ticket_id': ticket.service_ticket_id,
                'vehicle_id': ticket.vehicle_id,
                'vehicle': f"{ticket.vehicle.year} {ticket.vehicle.make} {ticket.vehicle.model}",
                'date_in': ticket.date_in.isoformat() if ticket.date_in else None,
                'date_out': ticket.date_out.isoformat() if ticket.date_out else None,
                'description': ticket.description,
                'status': ticket.status,
                'total_cost': ticket.total_cost,
                'mechanics': [m.name for m in ticket.mechanics]
            })
        
        return jsonify({
            'message': 'Your service tickets retrieved successfully',
            'customer_id': customer_id,
            'customer_name': customer.name,
            'count': len(tickets_data),
            'service_tickets': tickets_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============================================
# CRUD ROUTES FOR CUSTOMERS
# ============================================

# CREATE - Add a new customer (Registration)
@customers_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")  # Prevent spam creation
@validate_request(customer_create_schema)
def create_customer(validated_data):
    """
    Create a new customer (registration).
    Requires: name, phone, email, address, password
    """
    try:
        # Check if email already exists
        existing = Customer.query.filter_by(email=validated_data['email']).first()
        if existing:
            return jsonify({
                'status': 'error',
                'message': 'Email already registered'
            }), 400
        
        # Create new customer with hashed password
        new_customer = Customer(
            name=validated_data['name'],
            phone=validated_data['phone'],
            email=validated_data['email'],
            address=validated_data['address'],
            password=generate_password_hash(validated_data['password'])  # Hash the password
        )
        
        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Customer created successfully',
            'customer': customer_schema.dump(new_customer)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# READ - Get all customers with pagination
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_customers():
    """
    Get all customers with pagination.
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10, max: 100)
    """
    try:
        # Get pagination parameters from query string
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limit per_page to prevent excessive queries
        per_page = min(per_page, 100)
        
        # Query with pagination
        pagination = Customer.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(paginated_response(
            customers_schema,
            pagination,
            'Customers retrieved successfully',
            data_key='customers'
        )), 200
    
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


# UPDATE - Update an existing customer (Requires Token)
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
@limiter.limit("20 per minute")  # Rate limit updates
@validate_request(customer_update_schema)
def update_customer(validated_data, token_customer_id, customer_id):
    """
    Update an existing customer.
    Requires authentication - customer can only update their own profile.
    Optional fields: name, phone, email, address, password
    """
    try:
        # Ensure customer can only update their own profile
        if token_customer_id != customer_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized. You can only update your own profile.'
            }), 403
        
        customer = db.session.get(Customer, customer_id)
        
        if not customer:
            return jsonify({
                'status': 'error',
                'message': f'Customer with ID {customer_id} not found'
            }), 404
        
        # Update fields if provided
        if 'name' in validated_data:
            customer.name = validated_data['name']
        if 'phone' in validated_data:
            customer.phone = validated_data['phone']
        if 'email' in validated_data:
            # Check if new email already exists
            existing = Customer.query.filter_by(email=validated_data['email']).first()
            if existing and existing.customer_id != customer_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Email already in use'
                }), 400
            customer.email = validated_data['email']
        if 'address' in validated_data:
            customer.address = validated_data['address']
        if 'password' in validated_data:
            customer.password = generate_password_hash(validated_data['password'])
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Customer updated successfully',
            'customer': customer_schema.dump(customer)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# DELETE - Delete a customer (Requires Token)
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
@limiter.limit("5 per minute")  # Strict limit on deletions
def delete_customer(token_customer_id, customer_id):
    """
    Delete a customer.
    Requires authentication - customer can only delete their own account.
    """
    try:
        # Ensure customer can only delete their own account
        if token_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized. You can only delete your own account.'}), 403
        
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