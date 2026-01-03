"""Application factory module."""

from flask import Flask

from .config import Config
from .extensions import babel, cache, cors, db, jwt, limiter, login_manager, migrate


def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(config_class)

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register CLI commands
    _register_cli(app)

    # Register middleware
    _register_middleware(app)

    # Setup admin
    _setup_admin(app)

    # Setup login manager
    _setup_login_manager()

    # Auto-initialize database if enabled
    if app.config.get("AUTO_INIT_DB", True):
        _auto_init_database(app)

    return app


def _init_extensions(app: Flask):
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    babel.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)


def _register_blueprints(app: Flask):
    """Register application blueprints."""
    from .admin import admin_auth_bp
    from .api import api_bp
    from .auth import auth_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_auth_bp)


def _register_cli(app: Flask):
    """Register CLI commands."""
    from .cli import init_cli

    init_cli(app)


def _register_middleware(app: Flask):
    """Register middleware."""
    from .middleware import init_middleware

    init_middleware(app)


def _setup_admin(app: Flask):
    """Setup Flask-Admin."""
    from .admin import init_admin

    init_admin(app)


def _setup_login_manager():
    """Configure login manager."""
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


def _auto_init_database(app: Flask):
    """Auto-initialize database if needed."""
    import logging

    from .db_init import init_database

    logger = logging.getLogger(__name__)
    try:
        init_database(app)
    except Exception as e:
        logger.warning(f"Database auto-initialization skipped or failed: {e}")
        # Don't fail startup - might be running migrations or CLI commands
