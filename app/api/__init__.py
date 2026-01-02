"""API blueprint - handles menu, dish, and attribute CRUD operations."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db, limiter
from ..models import Dish, Emotion, Menu, Shape, Texture

api_bp = Blueprint("api", __name__, url_prefix="/api")


# =============================================================================
# Health Check
# =============================================================================


@api_bp.route("/health", methods=["GET"])
@limiter.limit("120 per minute")
def health_check():
    """Health check endpoint to verify API and database availability."""
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception:
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 503


# =============================================================================
# Menu Routes
# =============================================================================


@api_bp.route("/menus", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def get_menus():
    """Get all menus for current user."""
    user_id = int(get_jwt_identity())
    menus = Menu.query.filter_by(owner_id=user_id).all()
    return (
        jsonify(
            [
                {
                    "id": m.id,
                    "title": m.title,
                    "description": m.description,
                    "dish_count": len(m.dishes),
                }
                for m in menus
            ]
        ),
        200,
    )


@api_bp.route("/menus/<int:menu_id>", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def get_menu(menu_id: int):
    """Get a specific menu with dishes."""
    user_id = int(get_jwt_identity())
    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({"error": "Menu not found"}), 404

    if menu.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    return (
        jsonify(
            {
                "id": menu.id,
                "title": menu.title,
                "description": menu.description,
                "dishes": [_serialize_dish(d) for d in menu.dishes],
            }
        ),
        200,
    )


@api_bp.route("/menus", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")
def create_menu():
    """Create a new menu."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    menu = Menu(
        title=data.get("title", ""),
        description=data.get("description", ""),
        owner_id=user_id,
    )
    db.session.add(menu)
    db.session.commit()

    return jsonify({"message": "Menu created", "id": menu.id}), 201


@api_bp.route("/menus/<int:menu_id>", methods=["PUT"])
@jwt_required()
@limiter.limit("30 per minute")
def update_menu(menu_id: int):
    """Update a menu."""
    user_id = int(get_jwt_identity())
    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({"error": "Menu not found"}), 404

    if menu.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if data.get("title"):
        menu.title = data["title"]
    if data.get("description"):
        menu.description = data["description"]

    db.session.commit()
    return jsonify({"message": "Menu updated"}), 200


@api_bp.route("/menus/<int:menu_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("10 per minute")
def delete_menu(menu_id: int):
    """Delete a menu and all its dishes."""
    user_id = int(get_jwt_identity())
    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({"error": "Menu not found"}), 404

    if menu.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(menu)
    db.session.commit()
    return jsonify({"message": "Menu deleted"}), 200


# =============================================================================
# Dish Routes
# =============================================================================


@api_bp.route("/menus/<int:menu_id>/dishes", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def get_dishes(menu_id: int):
    """Get all dishes in a menu."""
    user_id = int(get_jwt_identity())
    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({"error": "Menu not found"}), 404

    if menu.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify([_serialize_dish(d) for d in menu.dishes]), 200


@api_bp.route("/menus/<int:menu_id>/dishes", methods=["POST"])
@jwt_required()
@limiter.limit("30 per minute")
def create_dish(menu_id: int):
    """Create a new dish in a menu."""
    user_id = int(get_jwt_identity())
    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({"error": "Menu not found"}), 404

    if menu.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    dish = Dish(
        menu_id=menu_id,
        name=data.get("name", ""),
        description=data.get("description", ""),
        section=data.get("section", ""),
        bitter=data.get("bitter"),
        salty=data.get("salty"),
        sour=data.get("sour"),
        sweet=data.get("sweet"),
        umami=data.get("umami"),
        fat=data.get("fat"),
        piquant=data.get("piquant"),
        temperature=data.get("temperature"),
        color1=data.get("color1"),
        color2=data.get("color2"),
        color3=data.get("color3"),
    )

    # Handle relationships
    _set_dish_relationships(dish, data)

    db.session.add(dish)
    db.session.commit()

    return jsonify({"message": "Dish created", "id": dish.id}), 201


@api_bp.route("/dishes/<int:dish_id>", methods=["PUT"])
@jwt_required()
@limiter.limit("30 per minute")
def update_dish(dish_id: int):
    """Update a dish."""
    user_id = int(get_jwt_identity())
    dish = db.session.get(Dish, dish_id)

    if not dish:
        return jsonify({"error": "Dish not found"}), 404

    menu = db.session.get(Menu, dish.menu_id)
    if menu.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    # Update scalar fields
    for field in [
        "name",
        "description",
        "section",
        "bitter",
        "salty",
        "sour",
        "sweet",
        "umami",
        "fat",
        "piquant",
        "temperature",
        "color1",
        "color2",
        "color3",
    ]:
        if field in data:
            setattr(dish, field, data[field])

    # Handle relationships
    _set_dish_relationships(dish, data)

    db.session.commit()
    return jsonify({"message": "Dish updated"}), 200


@api_bp.route("/dishes/<int:dish_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("20 per minute")
def delete_dish(dish_id: int):
    """Delete a dish."""
    user_id = int(get_jwt_identity())
    dish = db.session.get(Dish, dish_id)

    if not dish:
        return jsonify({"error": "Dish not found"}), 404

    menu = db.session.get(Menu, dish.menu_id)
    if menu.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(dish)
    db.session.commit()
    return jsonify({"message": "Dish deleted"}), 200


# =============================================================================
# Attribute Routes
# =============================================================================


@api_bp.route("/emotions", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def get_emotions():
    """Get all available emotions."""
    emotions = Emotion.query.all()
    return jsonify([{"id": e.id, "description": e.description} for e in emotions]), 200


@api_bp.route("/textures", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def get_textures():
    """Get all available textures."""
    textures = Texture.query.all()
    return jsonify([{"id": t.id, "description": t.description} for t in textures]), 200


@api_bp.route("/shapes", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def get_shapes():
    """Get all available shapes."""
    shapes = Shape.query.all()
    return jsonify([{"id": s.id, "description": s.description} for s in shapes]), 200


# =============================================================================
# Helper Functions
# =============================================================================


def _serialize_dish(dish: Dish) -> dict:
    """Serialize a dish to JSON-compatible dict."""
    return {
        "id": dish.id,
        "name": dish.name,
        "description": dish.description,
        "section": dish.section,
        "emotions": [{"id": e.id, "description": e.description} for e in dish.emotions],
        "textures": [{"id": t.id, "description": t.description} for t in dish.textures],
        "shapes": [{"id": s.id, "description": s.description} for s in dish.shapes],
        "bitter": dish.bitter,
        "salty": dish.salty,
        "sour": dish.sour,
        "sweet": dish.sweet,
        "umami": dish.umami,
        "fat": dish.fat,
        "piquant": dish.piquant,
        "temperature": dish.temperature,
        "colors": [c for c in [dish.color1, dish.color2, dish.color3] if c],
    }


def _set_dish_relationships(dish: Dish, data: dict) -> None:
    """Set emotion, texture, and shape relationships on a dish."""
    if "emotion_ids" in data:
        dish.emotions = Emotion.query.filter(Emotion.id.in_(data["emotion_ids"])).all()

    if "texture_ids" in data:
        dish.textures = Texture.query.filter(Texture.id.in_(data["texture_ids"])).all()

    if "shape_ids" in data:
        dish.shapes = Shape.query.filter(Shape.id.in_(data["shape_ids"])).all()
