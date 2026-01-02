"""Flask extensions initialization."""

import os

from flask_babel import Babel
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Database
db = SQLAlchemy()

# Migrations
migrate = Migrate()

# Login manager
login_manager = LoginManager()

# JWT
jwt = JWTManager()

# Babel
babel = Babel()

# CORS
cors = CORS()

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
)

# Cache
cache = Cache()
