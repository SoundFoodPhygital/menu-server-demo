"""Integration tests for complete workflows."""

import pytest


class TestUserWorkflow:
    """Test complete user workflows."""

    def test_register_login_create_menu_workflow(self, client):
        """Test complete workflow: register -> login -> create menu -> add dish."""
        # 1. Register
        response = client.post(
            "/auth/register",
            json={"username": "workflow_user", "password": "workflowpass123"},
        )
        assert response.status_code == 201

        # 2. Login
        response = client.post(
            "/auth/login",
            json={"username": "workflow_user", "password": "workflowpass123"},
        )
        assert response.status_code == 200
        token = response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create menu
        response = client.post(
            "/api/menus",
            headers=headers,
            json={
                "title": "My Restaurant Menu",
                "description": "A wonderful selection of dishes",
            },
        )
        assert response.status_code == 201
        menu_id = response.get_json()["id"]

        # 4. Add dish to menu
        response = client.post(
            f"/api/menus/{menu_id}/dishes",
            headers=headers,
            json={
                "name": "Spaghetti Bolognese",
                "description": "Classic Italian pasta with meat sauce",
                "section": "Primi",
                "salty": 2,
                "umami": 4,
            },
        )
        assert response.status_code == 201
        dish_id = response.get_json()["id"]

        # 5. Verify menu contains dish
        response = client.get(f"/api/menus/{menu_id}", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["dishes"]) == 1
        assert data["dishes"][0]["name"] == "Spaghetti Bolognese"

        # 6. Update dish
        response = client.put(
            f"/api/dishes/{dish_id}",
            headers=headers,
            json={"name": "Spaghetti alla Bolognese", "sweet": 1},
        )
        assert response.status_code == 200

        # 7. Delete dish
        response = client.delete(f"/api/dishes/{dish_id}", headers=headers)
        assert response.status_code == 200

        # 8. Delete menu
        response = client.delete(f"/api/menus/{menu_id}", headers=headers)
        assert response.status_code == 200

        # 9. Logout
        response = client.post("/auth/logout", headers=headers)
        assert response.status_code == 200

    def test_multi_user_isolation(self, client, app):
        """Test that users cannot access each other's data."""
        # Create two users
        client.post(
            "/auth/register",
            json={"username": "user1", "password": "password123"},
        )
        client.post(
            "/auth/register",
            json={"username": "user2", "password": "password123"},
        )

        # User 1 login and create menu
        response = client.post(
            "/auth/login",
            json={"username": "user1", "password": "password123"},
        )
        token1 = response.get_json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        response = client.post(
            "/api/menus",
            headers=headers1,
            json={"title": "User 1 Menu"},
        )
        menu_id = response.get_json()["id"]

        # User 2 login
        response = client.post(
            "/auth/login",
            json={"username": "user2", "password": "password123"},
        )
        token2 = response.get_json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 2 should not see User 1's menu in list
        response = client.get("/api/menus", headers=headers2)
        assert response.status_code == 200
        assert len(response.get_json()) == 0

        # User 2 should not be able to access User 1's menu directly
        response = client.get(f"/api/menus/{menu_id}", headers=headers2)
        assert response.status_code == 403

        # User 2 should not be able to update User 1's menu
        response = client.put(
            f"/api/menus/{menu_id}",
            headers=headers2,
            json={"title": "Hacked Menu"},
        )
        assert response.status_code == 403

        # User 2 should not be able to delete User 1's menu
        response = client.delete(f"/api/menus/{menu_id}", headers=headers2)
        assert response.status_code == 403


class TestDishWithAttributes:
    """Test dishes with emotions, textures, and shapes."""

    def test_create_dish_with_all_attributes(
        self, client, auth_headers, test_menu, sample_attributes
    ):
        """Test creating a dish with all attribute types."""
        response = client.post(
            f"/api/menus/{test_menu}/dishes",
            headers=auth_headers,
            json={
                "name": "Complete Dish",
                "description": "A dish with all attributes",
                "section": "Special",
                "emotion_ids": sample_attributes["emotions"],
                "texture_ids": sample_attributes["textures"],
                "shape_ids": sample_attributes["shapes"],
                "bitter": 1,
                "salty": 2,
                "sour": 3,
                "sweet": 4,
                "umami": 5,
                "fat": 2,
                "piquant": 1,
                "temperature": 3,
                "color1": "#FF0000",
                "color2": "#00FF00",
                "color3": "#0000FF",
            },
        )

        assert response.status_code == 201
        dish_id = response.get_json()["id"]

        # Verify dish was created with all attributes
        response = client.get(f"/api/menus/{test_menu}/dishes", headers=auth_headers)
        dishes = response.get_json()
        dish = next(d for d in dishes if d["id"] == dish_id)

        assert dish["name"] == "Complete Dish"
        assert len(dish["emotions"]) == 2
        assert len(dish["textures"]) == 2
        assert len(dish["shapes"]) == 2
        assert dish["bitter"] == 1
        assert dish["sweet"] == 4
        assert "#FF0000" in dish["colors"]
