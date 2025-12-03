from flask import Blueprint

inventory_bp = Blueprint('inventory', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.blueprints.inventory import routes
