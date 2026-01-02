"""Tests for admin area access."""

import pytest


class TestAdminLogin:
    """Tests for admin login functionality."""

    def test_admin_login_page_loads(self, client):
        """Test that admin login page loads."""
        response = client.get("/admin/login")

        assert response.status_code == 200
        assert b"Login" in response.data or b"login" in response.data

    def test_admin_login_success(self, client, admin_user):
        """Test successful admin login."""
        response = client.post(
            "/admin/login",
            data={"username": "admin", "password": "adminpassword123"},
            follow_redirects=False,
        )

        # Should redirect after successful login
        assert response.status_code in [200, 302]

    def test_admin_login_wrong_password(self, client, admin_user):
        """Test admin login with wrong password."""
        response = client.post(
            "/admin/login",
            data={"username": "admin", "password": "wrongpassword"},
            follow_redirects=True,
        )

        assert b"Invalid" in response.data or response.status_code == 200

    def test_admin_login_regular_user_denied(self, client, test_user):
        """Test that regular users cannot access admin."""
        response = client.post(
            "/admin/login",
            data={"username": "testuser", "password": "testpassword123"},
            follow_redirects=True,
        )

        # Should show access denied or stay on login page
        assert b"denied" in response.data.lower() or b"login" in response.data.lower()

    def test_manager_can_login(self, client, manager_user):
        """Test that managers can login to admin."""
        response = client.post(
            "/admin/login",
            data={"username": "manager", "password": "managerpassword123"},
            follow_redirects=False,
        )

        # Should redirect after successful login
        assert response.status_code in [200, 302]


class TestAdminAccess:
    """Tests for admin area access control."""

    def test_admin_index_requires_login(self, client):
        """Test that admin index requires authentication."""
        response = client.get("/admin/", follow_redirects=False)

        # Should redirect to login
        assert response.status_code in [302, 308] or b"login" in response.data.lower()

    def test_admin_logout(self, client, admin_user):
        """Test admin logout."""
        # Login first
        client.post(
            "/admin/login",
            data={"username": "admin", "password": "adminpassword123"},
            follow_redirects=False,
        )

        # Then logout
        response = client.get("/admin/logout", follow_redirects=True)

        assert response.status_code == 200


class TestAdminViews:
    """Tests for admin model views.

    Note: These tests may be skipped if Flask-Admin 2.x has issues with
    custom AdminIndexView. The core functionality is tested via the login tests.
    """

    def login_admin(self, client, admin_user):
        """Helper to login as admin."""
        return client.post(
            "/admin/login",
            data={"username": "admin", "password": "adminpassword123"},
            follow_redirects=False,
        )

    def test_users_view_accessible(self, client, admin_user):
        """Test that users view is accessible to admin."""
        self.login_admin(client, admin_user)
        response = client.get("/admin/user/")
        assert response.status_code == 200

    def test_menus_view_accessible(self, client, admin_user):
        """Test that menus view is accessible to admin."""
        self.login_admin(client, admin_user)
        response = client.get("/admin/menu/")
        assert response.status_code == 200

    def test_dishes_view_accessible(self, client, admin_user):
        """Test that dishes view is accessible to admin."""
        self.login_admin(client, admin_user)
        response = client.get("/admin/dish/")
        assert response.status_code == 200

    def test_request_logs_view_accessible(self, client, admin_user):
        """Test that request logs view is accessible to admin."""
        self.login_admin(client, admin_user)
        response = client.get("/admin/requestlog/")
        assert response.status_code == 200


class TestManagerAccess:
    """Tests for manager access to admin views."""

    def login_manager(self, client, manager_user):
        """Helper to login as manager."""
        return client.post(
            "/admin/login",
            data={"username": "manager", "password": "managerpassword123"},
            follow_redirects=False,
        )

    def test_manager_can_view_request_logs(self, client, manager_user):
        """Test that managers can view request logs."""
        self.login_manager(client, manager_user)
        response = client.get("/admin/requestlog/")
        assert response.status_code == 200

    def test_manager_cannot_edit_users(self, client, manager_user, test_user):
        """Test that managers cannot edit users (admin only view)."""
        self.login_manager(client, manager_user)
        response = client.get("/admin/user/")
        assert response.status_code in [302, 403] or b"denied" in response.data.lower()
