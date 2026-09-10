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
