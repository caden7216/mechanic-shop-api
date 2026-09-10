# App configuration. The MySQL password comes from the MYSQL_PASSWORD
# environment variable so it never ends up in the code or on GitHub.

import os
from urllib.parse import quote_plus

# quote_plus escapes characters like @ so they do not break the URL
password = quote_plus(os.environ.get("MYSQL_PASSWORD", ""))


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"mysql+mysqlconnector://root:{password}@localhost/mechanic_shop_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True


class TestingConfig:
    # sqlite is a lightweight database that is perfect for testing, and it
    # keeps the tests away from the real MySQL data.
    SQLALCHEMY_DATABASE_URI = "sqlite:///testing.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    # the rate limits would start returning 429 partway through the tests,
    # so they get turned off while testing
    RATELIMIT_ENABLED = False
