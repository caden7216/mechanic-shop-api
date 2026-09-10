# Third party extensions live here so the blueprints can import them without
# importing the whole app (which would cause a circular import).

from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

ma = Marshmallow()

# key_func=get_remote_address makes the limit per client IP address
limiter = Limiter(key_func=get_remote_address)

# SimpleCache stores the cached responses in memory
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
