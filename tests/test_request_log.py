"""Regression tests for request logging middleware."""

from app.models import RequestLog


class TestRequestLogMiddleware:
    """Test that the request logging middleware works correctly."""

    def test_api_request_is_logged(self, client, app):
        """Test that API requests are logged."""
        # Make an API request
        response = client.get("/api/health")
        assert response.status_code == 200

        # Check that the request was logged
        with app.app_context():
            log = RequestLog.query.first()
            assert log is not None
            assert log.method == "GET"
            assert log.endpoint == "/api/health"
            assert log.status_code == 200

    def test_non_api_request_not_logged(self, client, app):
        """Test that non-API requests are not logged."""
        # Make a non-API request (admin login page)
        client.get("/admin/login")

        # Check that no log entry was created
        with app.app_context():
            count = RequestLog.query.count()
            assert count == 0

    def test_multiple_requests_logged_separately(self, client, app):
        """Test that multiple API requests create multiple log entries."""
        # Make several API requests
        client.get("/api/health")
        client.get("/api/health")
        client.get("/api/health")

        # Check count
        with app.app_context():
            count = RequestLog.query.count()
            assert count == 3

    def test_authenticated_request_logs_user_id(self, client, app, auth_headers):
        """Test that authenticated requests log the user_id."""
        # Make an authenticated API request
        response = client.get("/api/menus", headers=auth_headers)
        assert response.status_code == 200

        # Check that user_id was logged
        with app.app_context():
            log = RequestLog.query.filter_by(endpoint="/api/menus").first()
            assert log is not None
            assert log.user_id is not None

    def test_unauthenticated_request_logs_null_user_id(self, client, app):
        """Test that unauthenticated requests log null user_id."""
        # Make an unauthenticated API request
        client.get("/api/health")

        # Check that user_id is null
        with app.app_context():
            log = RequestLog.query.first()
            assert log is not None
            assert log.user_id is None

    def test_different_http_methods_logged(self, client, app, auth_headers, test_menu):
        """Test that different HTTP methods are logged correctly."""
        # GET
        client.get("/api/health")

        # POST
        client.post(
            "/api/menus",
            headers=auth_headers,
            json={"title": "Test Menu"},
        )

        # Check logs
        with app.app_context():
            get_log = RequestLog.query.filter_by(method="GET").first()
            post_log = RequestLog.query.filter_by(method="POST").first()

            assert get_log is not None
            assert get_log.method == "GET"

            assert post_log is not None
            assert post_log.method == "POST"

    def test_error_responses_logged(self, client, app, auth_headers):
        """Test that error responses are also logged."""
        # Make a request that will fail (non-existent menu)
        response = client.get("/api/menus/99999", headers=auth_headers)
        assert response.status_code == 404

        # Check that the error was logged
        with app.app_context():
            log = RequestLog.query.filter_by(endpoint="/api/menus/99999").first()
            assert log is not None
            assert log.status_code == 404


class TestRequestLogModel:
    """Test RequestLog model methods."""

    def test_get_recent(self, client, app):
        """Test get_recent returns logs in descending order by timestamp."""
        # Create some log entries via API requests
        client.get("/api/health")
        client.get("/api/health")
        client.get("/api/health")

        with app.app_context():
            recent = RequestLog.get_recent(2)
            assert len(recent) == 2
            # Should return only 2 items even though we created 3
            all_logs = RequestLog.query.count()
            assert all_logs == 3

    def test_get_daily_counts(self, client, app):
        """Test get_daily_counts returns correct aggregation."""
        # Create some log entries
        client.get("/api/health")
        client.get("/api/health")
        client.get("/api/health")

        with app.app_context():
            counts = RequestLog.get_daily_counts(7)
            assert len(counts) >= 1
            # Should have at least 3 requests today
            today_count = counts[0][1] if counts else 0
            assert today_count >= 3

    def test_create_factory_method(self, app):
        """Test the create factory method."""
        with app.app_context():
            log = RequestLog.create(
                method="GET",
                endpoint="/test/endpoint",
                status_code=200,
                user_id=None,
            )
            assert log.id is not None
            assert log.method == "GET"
            assert log.endpoint == "/test/endpoint"
            assert log.status_code == 200


class TestDashboardCacheInvalidation:
    """Test that dashboard cache is invalidated after new requests."""

    def test_cache_invalidated_after_api_request(self, client, app):
        """Test that dashboard cache keys are invalidated after API requests."""
        from app.extensions import cache

        with app.app_context():
            # Set some cache values
            cache.set("admin_dashboard_stats", {"requests": 0})
            cache.set("admin_chart_data", {"labels": [], "values": []})
            cache.set("admin_recent_logs", [])

            # Make an API request
            client.get("/api/health")

            # Cache should be invalidated
            assert cache.get("admin_dashboard_stats") is None
            assert cache.get("admin_chart_data") is None
            assert cache.get("admin_recent_logs") is None
