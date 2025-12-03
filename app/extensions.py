from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Initialize Limiter - configured via config.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
)

# Initialize Marshmallow
ma = Marshmallow()

# Initialize Cache - configured via config.py
cache = Cache()