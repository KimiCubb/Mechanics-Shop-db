from flask import Blueprint

customers_bp = Blueprint('customers_bp', __name__)

# attach routes to my customers blueprint

from . import routes