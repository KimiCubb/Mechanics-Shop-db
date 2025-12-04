from flask import Flask, jsonify
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.customers import customers_bp
from app.blueprints.vehicles import vehicles_bp
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.inventory import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint

# Initialize Swagger UI for API documentation
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Path to the Swagger/OpenAPI JSON specification file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic Shop API"
    }
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swaggerui_blueprint, url_prefix='/api/docs')

    # Health check endpoint (exempt from rate limiting)
    @app.route('/health', methods=['GET'])
    @limiter.exempt
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'message': 'Mechanic Shop API is running'
        }), 200

    return app



