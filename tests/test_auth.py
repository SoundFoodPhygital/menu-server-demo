"""Tests for authentication endpoints."""

import pytest


class TestRegistration:
    """Tests for user registration."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={"username": "newuser", "password": "newpassword123"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "User created successfully"
        assert "user_id" in data

    def test_register_missing_username(self, client):
        """Test registration with missing username."""
        response = client.post(
            "/auth/register",
            json={"password": "newpassword123"},
        )

        assert response.status_code == 400
        assert "Username and password required" in response.get_json()["error"]

    def test_register_missing_password(self, client):
        """Test registration with missing password."""
        response = client.post(
            "/auth/register",
            json={"username": "newuser"},
        )

        assert response.status_code == 400
        assert "Username and password required" in response.get_json()["error"]

    def test_register_no_data(self, client):
        """Test registration with no data."""
        response = client.post("/auth/register", json=None)

        # Flask returns 415 Unsupported Media Type when no JSON is provided
        assert response.status_code == 415

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username."""
        response = client.post(
            "/auth/register",
            json={"username": "testuser", "password": "anotherpassword"},
        )

        assert response.status_code == 409
        assert "already exists" in response.get_json()["error"]


class TestLogin:
    """Tests for user login."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert "user_id" in data

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.get_json()["error"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "anypassword"},
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.get_json()["error"]

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials."""
        response = client.post("/auth/login", json={"username": "testuser"})

        assert response.status_code == 400

    def test_login_no_data(self, client):
        """Test login with no data."""
        response = client.post("/auth/login", json=None)

        # Flask returns 415 Unsupported Media Type when no JSON is provided
        assert response.status_code == 415


class TestLogout:
    """Tests for user logout."""

    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post("/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert "Successfully logged out" in response.get_json()["message"]

    def test_logout_without_token(self, client):
        """Test logout without authentication."""
        response = client.post("/auth/logout")

        assert response.status_code == 401

    def test_token_revoked_after_logout(self, client, app, test_user):
        """Test that token is revoked after logout."""
        # Login to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Logout
        client.post("/auth/logout", headers=headers)

        # Try to use token again
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401


class TestCurrentUser:
    """Tests for getting current user info."""

    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user info."""
        response = client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "testuser"
        assert data["role"] == "user"

    def test_get_current_user_admin(self, client, admin_auth_headers, admin_user):
        """Test getting current admin user info."""
        response = client.get("/auth/me", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    def test_get_current_user_without_token(self, client):
        """Test getting current user without authentication."""
        response = client.get("/auth/me")

        assert response.status_code == 401
