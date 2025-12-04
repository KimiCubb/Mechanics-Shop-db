from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError
import os

# Use environment variable for SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')


def encode_token(customer_id):
    """
    Create a JWT token specific to a customer.
    Takes in a customer_id to create a token specific to that user.
    """
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),  # Expires in 1 hour
        'iat': datetime.now(timezone.utc),  # Issued at
        'sub': str(customer_id)  # Customer ID as string (required for proper encoding)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f):
    """
    Decorator that validates the JWT token and returns the customer_id
    to the function it's decorating.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Look for the token in the Authorization header (Bearer Token)
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Get token after "Bearer "
            except IndexError:
                return jsonify({'message': 'Invalid token format. Use: Bearer <token>'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing! Please provide a Bearer Token.'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            customer_id = int(data['sub'])  # Convert back to int for database queries
            
        except ExpiredSignatureError:
            return jsonify({'message': 'Token has expired! Please login again.'}), 401
        except JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        # Pass customer_id to the decorated function
        return f(customer_id, *args, **kwargs)

    return decorated


def validate_request(schema):
    """
    Decorator to validate incoming request data against a Marshmallow schema.
    Returns 400 with validation errors if validation fails.
    
    Usage:
        @app.route('/customers', methods=['POST'])
        @validate_request(customer_create_schema)
        def create_customer(validated_data):
            # validated_data is already validated and deserialized
            ...
    
    Args:
        schema: Marshmallow schema instance for validation
    
    Returns:
        Decorator function that validates request JSON
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                
                if data is None:
                    return jsonify({
                        'status': 'error',
                        'message': 'Request body must be valid JSON',
                        'errors': {}
                    }), 400
                
                # Validate and deserialize data against schema
                validated_data = schema.load(data)
                
                # Pass validated data to the route function
                return f(validated_data, *args, **kwargs)
                
            except ValidationError as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': e.messages
                }), 400
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid JSON in request body',
                    'errors': {'body': [str(e)]}
                }), 400
        
        return decorated_function
    return decorator


def paginated_response(items_schema, pagination_obj, message="Resources retrieved successfully", data_key='data'):
    """
    Create a standardized pagination response.
    
    Usage:
        pagination = Model.query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify(paginated_response(
            model_schema,
            pagination,
            'Models retrieved successfully',
            data_key='models'
        )), 200
    
    Args:
        items_schema: Marshmallow schema for the items (can be many=True or single)
        pagination_obj: Flask-SQLAlchemy pagination object
        message: Success message
        data_key: Key name for the data array in response (e.g., 'models', 'customers', 'parts')
    
    Returns:
        dict: Standardized pagination response
    """
    return {
        'status': 'success',
        'message': message,
        'pagination': {
            'page': pagination_obj.page,
            'per_page': pagination_obj.per_page,
            'total_items': pagination_obj.total,
            'total_pages': pagination_obj.pages,
            'has_next': pagination_obj.has_next,
            'has_prev': pagination_obj.has_prev,
            'next_page': pagination_obj.next_num if pagination_obj.has_next else None,
            'prev_page': pagination_obj.prev_num if pagination_obj.has_prev else None
        },
        data_key: items_schema.dump(pagination_obj.items)
    }