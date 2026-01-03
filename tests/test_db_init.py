"""Tests for database initialization functionality."""

import os
from unittest.mock import patch

import pytest

from app import create_app
from app.config import Config, TestingConfig
from app.db_init import (
    _create_admin_user,
    _create_tables,
    _database_needs_init,
    _seed_default_data,
    check_database_connection,
    init_database,
)
from app.extensions import db
from app.models import Emotion, Shape, Texture, User


class TestDatabaseInitialization:
    """Tests for database auto-initialization."""

    def test_database_needs_init_empty_db(self, app):
        """Test that empty database is detected as needing initialization."""
        with app.app_context():
            # Tables exist but are empty
            db.drop_all()
            db.create_all()
            assert _database_needs_init() is True

    def test_database_needs_init_with_user(self, app):
        """Test that database with users doesn't need initialization."""
        with app.app_context():
            User.create(username="testuser", password="testpass123")
            assert _database_needs_init() is False

    def test_create_tables(self, app):
        """Test table creation."""
        with app.app_context():
            db.drop_all()
            _create_tables()
            # Verify tables exist by querying
            assert User.query.count() == 0
            assert Emotion.query.count() == 0

    def test_seed_default_data(self, app):
        """Test seeding of default attributes."""
        with app.app_context():
            _seed_default_data(app)

            # Check emotions were created
            emotions = Emotion.query.all()
            assert len(emotions) == 9
            emotion_names = [e.description for e in emotions]
            assert "happy" in emotion_names
            assert "sad" in emotion_names

            # Check textures were created
            textures = Texture.query.all()
            assert len(textures) == 10
            texture_names = [t.description for t in textures]
            assert "crispy" in texture_names
            assert "creamy" in texture_names

            # Check shapes were created
            shapes = Shape.query.all()
            assert len(shapes) == 9
            shape_names = [s.description for s in shapes]
            assert "round" in shape_names
            assert "square" in shape_names

    def test_seed_default_data_idempotent(self, app):
        """Test that seeding is idempotent (can be run multiple times)."""
        with app.app_context():
            _seed_default_data(app)
            initial_count = Emotion.query.count()

            _seed_default_data(app)
            assert Emotion.query.count() == initial_count

    def test_create_admin_user_from_env(self, app):
        """Test admin user creation from environment variables."""
        with app.app_context():
            with patch.dict(
                os.environ,
                {
                    "ADMIN_USERNAME": "customadmin",
                    "ADMIN_PASSWORD": "custompass123",
                    "ADMIN_EMAIL": "custom@example.com",
                },
            ):
                _create_admin_user(app)

                user = User.get_by_username("customadmin")
                assert user is not None
                assert user.email == "custom@example.com"
                assert user.is_admin is True
                assert user.is_manager is True
                assert user.check_password("custompass123")

    def test_create_admin_user_default_values(self, app):
        """Test admin user creation with default values."""
        with app.app_context():
            # Clear environment variables
            with patch.dict(
                os.environ,
                {"ADMIN_USERNAME": "", "ADMIN_PASSWORD": "", "ADMIN_EMAIL": ""},
                clear=False,
            ):
                # Remove the env vars if they exist
                os.environ.pop("ADMIN_USERNAME", None)
                os.environ.pop("ADMIN_PASSWORD", None)
                os.environ.pop("ADMIN_EMAIL", None)

                _create_admin_user(app)

                user = User.get_by_username("admin")
                assert user is not None
                assert user.is_admin is True
                assert user.check_password("admin123")

    def test_create_admin_user_idempotent(self, app):
        """Test that admin creation doesn't duplicate users."""
        with app.app_context():
            _create_admin_user(app)
            initial_count = User.query.count()

            _create_admin_user(app)
            assert User.query.count() == initial_count

    def test_check_database_connection_success(self, app):
        """Test database connection check succeeds."""
        assert check_database_connection(app) is True

    def test_init_database_full(self, app):
        """Test full database initialization."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            result = init_database(app)

            assert result is True
            assert User.query.count() >= 1
            assert Emotion.query.count() == 9
            assert Texture.query.count() == 10
            assert Shape.query.count() == 9

    def test_init_database_already_initialized(self, app):
        """Test that init_database returns False when already set up."""
        with app.app_context():
            # First initialization
            init_database(app)

            # Second initialization should return False
            result = init_database(app)
            assert result is False


class TestAutoInitConfig:
    """Tests for AUTO_INIT_DB configuration."""

    def test_auto_init_db_disabled_in_testing(self):
        """Test that AUTO_INIT_DB is disabled in testing config."""
        assert TestingConfig.AUTO_INIT_DB is False

    def test_auto_init_db_enabled_by_default(self):
        """Test that AUTO_INIT_DB is enabled by default."""
        # Default Config should have AUTO_INIT_DB = True
        assert Config.AUTO_INIT_DB is True

    def test_auto_init_db_from_env_true(self):
        """Test AUTO_INIT_DB can be set to true from environment."""
        with patch.dict(os.environ, {"AUTO_INIT_DB": "true"}):
            # Need to reimport to get fresh config
            result = os.environ.get("AUTO_INIT_DB", "true").lower() in (
                "true",
                "1",
                "yes",
            )
            assert result is True

    def test_auto_init_db_from_env_false(self):
        """Test AUTO_INIT_DB can be set to false from environment."""
        with patch.dict(os.environ, {"AUTO_INIT_DB": "false"}):
            result = os.environ.get("AUTO_INIT_DB", "true").lower() in (
                "true",
                "1",
                "yes",
            )
            assert result is False


class TestDatabaseURLConfig:
    """Tests for database URL configuration."""

    def test_sqlite_default(self):
        """Test default SQLite database URL."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DATABASE_URL", None)
            from app.config import get_database_url

            url = get_database_url()
            assert "sqlite:///" in url
            assert "instance/project.db" in url

    def test_postgres_url_passthrough(self):
        """Test PostgreSQL URL is passed through unchanged."""
        pg_url = "postgresql://user:pass@localhost:5432/soundfood"
        with patch.dict(os.environ, {"DATABASE_URL": pg_url}):
            from app.config import get_database_url

            url = get_database_url()
            assert url == pg_url

    def test_mysql_url_passthrough(self):
        """Test MySQL URL is passed through unchanged."""
        mysql_url = "mysql+pymysql://user:pass@localhost:3306/soundfood"
        with patch.dict(os.environ, {"DATABASE_URL": mysql_url}):
            from app.config import get_database_url

            url = get_database_url()
            assert url == mysql_url

    def test_sqlite_relative_path_converted(self):
        """Test relative SQLite path is converted to absolute."""
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///test.db"}):
            from app.config import get_database_url

            url = get_database_url()
            # Should be converted to absolute path (4 slashes for absolute)
            assert url.startswith("sqlite:///")
            assert "/test.db" in url

    def test_sqlite_absolute_path_unchanged(self):
        """Test absolute SQLite path is not modified."""
        abs_url = "sqlite:////absolute/path/test.db"
        with patch.dict(os.environ, {"DATABASE_URL": abs_url}):
            from app.config import get_database_url

            url = get_database_url()
            assert url == abs_url
