"""Middleware for request processing."""

from flask import Flask, request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from jwt.exceptions import ExpiredSignatureError

from .extensions import db
from .models import RequestLog


def init_middleware(app: Flask):
    """Initialize request middleware."""

    @app.after_request
    def log_request(response):
        """Log API requests for analytics."""
        # Only log API requests
        if not request.path.startswith("/api"):
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
        log = RequestLog(
            method=request.method,
            endpoint=request.path,
            status_code=response.status_code,
            user_id=user_id,
        )
        db.session.add(log)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        return response

    @app.before_request
    def before_request():
        """Pre-request processing."""
        # Add any pre-request logic here
        pass
