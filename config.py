# App configuration. The MySQL password comes from the MYSQL_PASSWORD
# environment variable so it never ends up in the code or on GitHub.

import os
from urllib.parse import quote_plus

# Reads the .env file so the database url and secret key are available as
# environment variables while working locally. python-dotenv is not in
# requirements.txt because Render sets the real environment variables itself,
# so the import is wrapped in a try/except.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

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


class ProductionConfig:
    # the live database on Render. The url is kept in the .env file locally and
    # set as an environment variable on Render, so it never ends up on GitHub.
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"
    # debug mode off, because it shows the code to anyone who hits an error
    DEBUG = False
