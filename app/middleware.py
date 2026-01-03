"""Middleware for request processing."""

import logging
import sys

from flask import Flask, g, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from jwt.exceptions import ExpiredSignatureError

from .extensions import cache, db
from .models import RequestLog

logger = logging.getLogger(__name__)


def init_middleware(app: Flask):
    """Initialize request middleware."""

    @app.before_request
    def before_request():
        """Pre-request processing - capture request info before processing."""
        # Store request info for logging after response
        if request.path.startswith("/api"):
            g.log_request = True
            g.request_method = request.method
            g.request_path = request.path
        else:
            g.log_request = False

    @app.after_request
    def log_request(response):
        """Log API requests for analytics."""
        # Only log API requests
        if not getattr(g, "log_request", False):
            return response

        # Try to get user ID from JWT
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                user_id = int(identity)
        except (ExpiredSignatureError, Exception):
            pass

        # Create log entry
        try:
            log = RequestLog(
                method=g.request_method,
                endpoint=g.request_path,
                status_code=response.status_code,
                user_id=user_id,
            )
            db.session.add(log)
            db.session.commit()

            # Invalidate dashboard cache so stats update
            cache.delete("admin_dashboard_stats")
            cache.delete("admin_chart_data")
            cache.delete("admin_recent_logs")
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
            print(f"[MIDDLEWARE ERROR] Failed to log request: {e}", file=sys.stderr)
            db.session.rollback()

        return response
