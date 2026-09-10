# Token helpers. encode_token() makes a JWT for a customer, and the
# token_required decorator protects routes by checking that token.

import os
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import request, jsonify
from jose import jwt
import jose

# The real key is an environment variable so it is not published on GitHub.
# The fallback is there for the GitHub Actions pipeline, which has no
# SECRET_KEY environment variable set, and for running the tests.
SECRET_KEY = os.environ.get("SECRET_KEY") or "a super secret, secret key"


def encode_token(customer_id):
    """Builds a token that is specific to one customer."""
    payload = {
        # the token stops working an hour from now
        "exp": datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        "iat": datetime.now(timezone.utc),  # issued at
        # sub has to be a string or the token comes out malformed
        "sub": str(customer_id),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def token_required(f):
    """Put this on a route to make it require a Bearer token."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # the token comes in as "Bearer <token>"
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split(" ")

            if len(parts) == 2:
                token = parts[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            customer_id = int(data["sub"])
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jose.exceptions.JWTError:
            return jsonify({"message": "Invalid token!"}), 401

        # hand the customer id to the route we are wrapping
        return f(customer_id, *args, **kwargs)

    return decorated
