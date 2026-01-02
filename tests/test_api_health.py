"""Tests for health check endpoint."""


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check_returns_healthy(self, client):
        """Test that health check returns healthy status with database connected."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    def test_health_check_no_auth_required(self, client):
        """Test that health check does not require authentication."""
        # No auth headers provided
        response = client.get("/api/health")

        assert response.status_code == 200
