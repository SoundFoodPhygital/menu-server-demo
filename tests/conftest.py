"""Pytest configuration and fixtures."""

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import User, Menu, Dish, Emotion, Texture, Shape


@pytest.fixture(scope="function")
def app():
    """Create and configure a test application instance."""
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user and return user_id."""
    with app.app_context():
        user = User.create(username="testuser", password="testpassword123")
        user_id = user.id
        return user_id


@pytest.fixture
def admin_user(app):
    """Create an admin user and return user_id."""
    with app.app_context():
        user = User.create(username="admin", password="adminpassword123", is_admin=True)
        user_id = user.id
        return user_id


@pytest.fixture
def manager_user(app):
    """Create a manager user and return user_id."""
    with app.app_context():
        user = User.create(
            username="manager", password="managerpassword123", is_manager=True
        )
        user_id = user.id
        return user_id


@pytest.fixture
def auth_headers(app, test_user):
    """Get JWT authorization headers for test user."""
    with app.app_context():
        access_token = create_access_token(identity=str(test_user))
        return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_auth_headers(app, admin_user):
    """Get JWT authorization headers for admin user."""
    with app.app_context():
        access_token = create_access_token(identity=str(admin_user))
        return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_menu(app, test_user):
    """Create a test menu and return menu_id."""
    with app.app_context():
        menu = Menu(
            title="Test Menu",
            description="A test menu",
            owner_id=test_user,
        )
        db.session.add(menu)
        db.session.commit()
        menu_id = menu.id
        return menu_id


@pytest.fixture
def test_dish(app, test_menu):
    """Create a test dish and return dish_id."""
    with app.app_context():
        dish = Dish(
            menu_id=test_menu,
            name="Test Dish",
            description="A delicious test dish",
            section="Main",
            bitter=1,
            salty=2,
            sour=3,
            sweet=4,
            umami=5,
        )
        db.session.add(dish)
        db.session.commit()
        dish_id = dish.id
        return dish_id


@pytest.fixture
def sample_attributes(app):
    """Create sample emotions, textures, and shapes."""
    with app.app_context():
        emotions = [Emotion(description="Happy"), Emotion(description="Nostalgic")]
        textures = [Texture(description="Crunchy"), Texture(description="Smooth")]
        shapes = [Shape(description="Round"), Shape(description="Square")]

        db.session.add_all(emotions + textures + shapes)
        db.session.commit()

        return {
            "emotions": [e.id for e in emotions],
            "textures": [t.id for t in textures],
            "shapes": [s.id for s in shapes],
        }
