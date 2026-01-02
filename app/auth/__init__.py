"""Authentication blueprint - handles user registration, login, and logout."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from ..extensions import db, jwt, limiter
from ..models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Store for revoked tokens (in production, use Redis or database)
revoked_tokens = set()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if JWT token has been revoked."""
    jti = jwt_payload["jti"]
    return jti in revoked_tokens


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    """Register a new user."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if User.get_by_username(username):
        return jsonify({"error": "Username already exists"}), 409

    user = User.create(username=username, password=password)

    return jsonify({"message": "User created successfully", "user_id": user.id}), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """Login and get JWT token."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = User.get_by_username(username)

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({"access_token": access_token, "user_id": user.id}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout and revoke JWT token."""
    jti = get_jwt()["jti"]
    revoked_tokens.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current authenticated user info."""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user.id, "username": user.username, "role": user.role}), 200
