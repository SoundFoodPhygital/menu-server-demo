"""Tests for dish API endpoints."""

import pytest


class TestGetDishes:
    """Tests for getting dishes."""

    def test_get_dishes_empty(self, client, auth_headers, test_menu):
        """Test getting dishes when menu has none."""
        response = client.get(f"/api/menus/{test_menu}/dishes", headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_dishes_with_data(self, client, auth_headers, test_menu, test_dish):
        """Test getting dishes with existing data."""
        response = client.get(f"/api/menus/{test_menu}/dishes", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Dish"

    def test_get_dishes_menu_not_found(self, client, auth_headers):
        """Test getting dishes from non-existent menu."""
        response = client.get("/api/menus/9999/dishes", headers=auth_headers)

        assert response.status_code == 404

    def test_get_dishes_unauthorized_menu(self, client, test_menu, app):
        """Test getting dishes from another user's menu."""
        from flask_jwt_extended import create_access_token
        from app.models import User

        with app.app_context():
            other_user = User.create(username="other", password="password123")
            token = create_access_token(identity=str(other_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.get(f"/api/menus/{test_menu}/dishes", headers=headers)
            assert response.status_code == 403


class TestCreateDish:
    """Tests for creating dishes."""

    def test_create_dish_success(self, client, auth_headers, test_menu):
        """Test creating a new dish."""
        response = client.post(
            f"/api/menus/{test_menu}/dishes",
            headers=auth_headers,
            json={
                "name": "Pasta Carbonara",
                "description": "Classic Roman pasta",
                "section": "Primi",
                "salty": 3,
                "umami": 4,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "id" in data
        assert data["message"] == "Dish created"

    def test_create_dish_with_attributes(
        self, client, auth_headers, test_menu, sample_attributes
    ):
        """Test creating a dish with emotions, textures, and shapes."""
        response = client.post(
            f"/api/menus/{test_menu}/dishes",
            headers=auth_headers,
            json={
                "name": "Happy Dish",
                "emotion_ids": sample_attributes["emotions"],
                "texture_ids": sample_attributes["textures"],
                "shape_ids": sample_attributes["shapes"],
            },
        )

        assert response.status_code == 201

    def test_create_dish_menu_not_found(self, client, auth_headers):
        """Test creating dish in non-existent menu."""
        response = client.post(
            "/api/menus/9999/dishes",
            headers=auth_headers,
            json={"name": "Test"},
        )

        assert response.status_code == 404

    def test_create_dish_unauthorized_menu(self, client, test_menu, app):
        """Test creating dish in another user's menu."""
        from flask_jwt_extended import create_access_token
        from app.models import User

        with app.app_context():
            other_user = User.create(username="other", password="password123")
            token = create_access_token(identity=str(other_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.post(
                f"/api/menus/{test_menu}/dishes",
                headers=headers,
                json={"name": "Hacked Dish"},
            )
            assert response.status_code == 403

    def test_create_dish_no_data(self, client, auth_headers, test_menu):
        """Test creating dish with no data."""
        response = client.post(
            f"/api/menus/{test_menu}/dishes",
            headers=auth_headers,
            json=None,
        )

        # Flask returns 415 Unsupported Media Type when no JSON is provided
        assert response.status_code == 415


class TestUpdateDish:
    """Tests for updating dishes."""

    def test_update_dish_success(self, client, auth_headers, test_dish):
        """Test updating a dish."""
        response = client.put(
            f"/api/dishes/{test_dish}",
            headers=auth_headers,
            json={
                "name": "Updated Dish",
                "description": "Updated description",
                "sweet": 5,
            },
        )

        assert response.status_code == 200
        assert response.get_json()["message"] == "Dish updated"

    def test_update_dish_attributes(
        self, client, auth_headers, test_dish, sample_attributes
    ):
        """Test updating dish attributes."""
        response = client.put(
            f"/api/dishes/{test_dish}",
            headers=auth_headers,
            json={
                "emotion_ids": sample_attributes["emotions"][:1],
                "texture_ids": sample_attributes["textures"][:1],
            },
        )

        assert response.status_code == 200

    def test_update_dish_not_found(self, client, auth_headers):
        """Test updating non-existent dish."""
        response = client.put(
            "/api/dishes/9999",
            headers=auth_headers,
            json={"name": "Test"},
        )

        assert response.status_code == 404

    def test_update_dish_unauthorized(self, client, test_dish, app):
        """Test updating another user's dish."""
        from flask_jwt_extended import create_access_token
        from app.models import User

        with app.app_context():
            other_user = User.create(username="other", password="password123")
            token = create_access_token(identity=str(other_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.put(
                f"/api/dishes/{test_dish}",
                headers=headers,
                json={"name": "Hacked"},
            )
            assert response.status_code == 403


class TestDeleteDish:
    """Tests for deleting dishes."""

    def test_delete_dish_success(self, client, auth_headers, test_dish, test_menu):
        """Test deleting a dish."""
        dish_id = test_dish
        menu_id = test_menu

        response = client.delete(f"/api/dishes/{dish_id}", headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json()["message"] == "Dish deleted"

        # Verify deletion
        response = client.get(f"/api/menus/{menu_id}/dishes", headers=auth_headers)
        assert len(response.get_json()) == 0

    def test_delete_dish_not_found(self, client, auth_headers):
        """Test deleting non-existent dish."""
        response = client.delete("/api/dishes/9999", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_dish_unauthorized(self, client, test_dish, app):
        """Test deleting another user's dish."""
        from flask_jwt_extended import create_access_token
        from app.models import User

        with app.app_context():
            other_user = User.create(username="other", password="password123")
            token = create_access_token(identity=str(other_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.delete(f"/api/dishes/{test_dish}", headers=headers)
            assert response.status_code == 403
