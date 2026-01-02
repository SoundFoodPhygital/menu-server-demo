"""Admin package - exports admin setup functions."""

from .views import init_admin
from .routes import admin_auth_bp

__all__ = ["init_admin", "admin_auth_bp"]
