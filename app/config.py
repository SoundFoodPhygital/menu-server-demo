"""Application configuration."""

import os
from datetime import timedelta
from pathlib import Path

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    # Look for .env in the project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on environment variables


def get_database_url() -> str:
    """Get database URL from environment or use SQLite default.

    Supports:
    - SQLite: sqlite:///instance/project.db (default)
    - PostgreSQL: postgresql://user:pass@host:5432/dbname
    - MariaDB/MySQL: mysql+pymysql://user:pass@host:3306/dbname
    """
    db_url = os.environ.get("DATABASE_URL", "sqlite:///instance/project.db")

    # Convert relative SQLite path to absolute path
    if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:////"):
        # Relative path - make it absolute relative to project root
        relative_path = db_url.replace("sqlite:///", "")
        # Get the project root (parent of app directory)
        project_root = Path(__file__).parent.parent
        absolute_path = project_root / relative_path
        # Ensure the directory exists
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        db_url = f"sqlite:///{absolute_path}"

    return db_url


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Check connection before using
    }
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    WTF_CSRF_ENABLED = True
    FLASK_ADMIN_SWATCH = "cerulean"

    # Auto-initialize database on startup
    AUTO_INIT_DB = os.environ.get("AUTO_INIT_DB", "true").lower() in (
        "true",
        "1",
        "yes",
    )

    # Cache configuration
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 0  # Disable caching by default in tests
    AUTO_INIT_DB = False  # Don't auto-initialize database in tests


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
