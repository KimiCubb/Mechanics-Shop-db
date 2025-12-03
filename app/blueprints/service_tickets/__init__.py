from flask import Blueprint

service_tickets_bp = Blueprint('service_tickets_bp', __name__)

# Attach routes to service_tickets blueprint
from . import routes
