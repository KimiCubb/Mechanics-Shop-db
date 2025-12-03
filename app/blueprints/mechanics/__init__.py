from flask import Blueprint

mechanics_bp = Blueprint('mechanics_bp', __name__)

# Attach routes to mechanics blueprint
from . import routes
