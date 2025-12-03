from flask import Blueprint

vehicles_bp = Blueprint('vehicles_bp', __name__)

# Attach routes to vehicles blueprint
from . import routes
