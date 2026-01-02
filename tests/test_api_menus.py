"""Tests for menu API endpoints."""

import pytest


class TestGetMenus:
    """Tests for getting menus."""

    def test_get_menus_empty(self, client, auth_headers):
        """Test getting menus when user has none."""
        response = client.get("/api/menus", headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_menus_with_data(self, client, auth_headers, test_menu):
        """Test getting menus with existing data."""
        response = client.get("/api/menus", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Menu"

    def test_get_menus_unauthorized(self, client):
        """Test getting menus without authentication."""
        response = client.get("/api/menus")

        assert response.status_code == 401


class TestGetMenu:
    """Tests for getting a single menu."""

    def test_get_menu_success(self, client, auth_headers, test_menu):
        """Test getting a specific menu."""
        response = client.get(f"/api/menus/{test_menu}", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Test Menu"
        assert data["description"] == "A test menu"

    def test_get_menu_not_found(self, client, auth_headers):
        """Test getting non-existent menu."""
        response = client.get("/api/menus/9999", headers=auth_headers)

        assert response.status_code == 404

    def test_get_menu_unauthorized_user(self, client, test_menu, app):
        """Test getting menu belonging to another user."""
        from flask_jwt_extended import create_access_token
        from app.models import User

        with app.app_context():
            other_user = User.create(username="other", password="password123")
            token = create_access_token(identity=str(other_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.get(f"/api/menus/{test_menu}", headers=headers)
            assert response.status_code == 403


class TestCreateMenu:
    """Tests for creating menus."""

    def test_create_menu_success(self, client, auth_headers):
        """Test creating a new menu."""
        response = client.post(
            "/api/menus",
            headers=auth_headers,
            json={"title": "New Menu", "description": "A new menu"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "id" in data
        assert data["message"] == "Menu created"

    def test_create_menu_minimal(self, client, auth_headers):
        """Test creating a menu with minimal data."""
        response = client.post(
            "/api/menus", headers=auth_headers, json={"title": "Minimal"}
        )

        assert response.status_code == 201

    def test_create_menu_no_data(self, client, auth_headers):
        """Test creating a menu with no data."""
        response = client.post("/api/menus", headers=auth_headers, json=None)

        # Flask returns 415 Unsupported Media Type when no JSON is provided
        assert response.status_code == 415

    def test_create_menu_unauthorized(self, client):
        """Test creating a menu without authentication."""
        response = client.post("/api/menus", json={"title": "Test"})

        assert response.status_code == 401


class TestUpdateMenu:
    """Tests for updating menus."""

    def test_update_menu_success(self, client, auth_headers, test_menu):
        """Test updating a menu."""
        response = client.put(
            f"/api/menus/{test_menu}",
            headers=auth_headers,
            json={"title": "Updated Menu", "description": "Updated description"},
        )

        assert response.status_code == 200
        assert response.get_json()["message"] == "Menu updated"

    def test_update_menu_partial(self, client, auth_headers, test_menu):
        """Test partially updating a menu."""
        response = client.put(
            f"/api/menus/{test_menu}",
            headers=auth_headers,
            json={"title": "Only Title Updated"},
        )

        assert response.status_code == 200

    def test_update_menu_not_found(self, client, auth_headers):
        """Test updating non-existent menu."""
        response = client.put(
            "/api/menus/9999",
            headers=auth_headers,
            json={"title": "Test"},
        )

        assert response.status_code == 404

    def test_update_menu_unauthorized_user(self, client, test_menu, app):
        """Test updating menu belonging to another user."""
        from flask_jwt_extended import create_access_token
        from app.models import User

        with app.app_context():
            other_user = User.create(username="other", password="password123")
            token = create_access_token(identity=str(other_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.put(
                f"/api/menus/{test_menu}",
                headers=headers,
                json={"title": "Hacked"},
            )
            assert response.status_code == 403


class TestDeleteMenu:
    """Tests for deleting menus."""

    def test_delete_menu_success(self, client, auth_headers, test_menu):
        """Test deleting a menu."""
        response = client.delete(
            f"/api/menus/{test_menu}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.get_json()["message"] == "Menu deleted"

        # Verify deletion
        response = client.get(f"/api/menus/{test_menu}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_menu_not_found(self, client, auth_headers):
        """Test deleting non-existent menu."""
        response = client.delete("/api/menus/9999", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_menu_unauthorized_user(self, client, test_menu, app):
        """Test deleting menu belonging to another user."""
        from flask_jwt_extended import create_access_token
        from app.models import User

        with app.app_context():
            other_user = User.create(username="other", password="password123")
            token = create_access_token(identity=str(other_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.delete(f"/api/menus/{test_menu}", headers=headers)
            assert response.status_code == 403
