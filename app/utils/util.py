from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify
import os

# Use environment variable for SECRET_KEY (more secure)
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')


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
            
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired! Please login again.'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        # Pass customer_id to the decorated function
        return f(customer_id, *args, **kwargs)

    return decorated