"""Tests for attribute API endpoints (emotions, textures, shapes)."""

import pytest


class TestEmotions:
    """Tests for emotions endpoint."""

    def test_get_emotions_empty(self, client, auth_headers):
        """Test getting emotions when none exist."""
        response = client.get("/api/emotions", headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_emotions_with_data(self, client, auth_headers, sample_attributes):
        """Test getting emotions with existing data."""
        response = client.get("/api/emotions", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        names = [e["description"] for e in data]
        assert "Happy" in names
        assert "Nostalgic" in names

    def test_get_emotions_unauthorized(self, client):
        """Test getting emotions without authentication."""
        response = client.get("/api/emotions")

        assert response.status_code == 401


class TestTextures:
    """Tests for textures endpoint."""

    def test_get_textures_empty(self, client, auth_headers):
        """Test getting textures when none exist."""
        response = client.get("/api/textures", headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_textures_with_data(self, client, auth_headers, sample_attributes):
        """Test getting textures with existing data."""
        response = client.get("/api/textures", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        names = [t["description"] for t in data]
        assert "Crunchy" in names
        assert "Smooth" in names

    def test_get_textures_unauthorized(self, client):
        """Test getting textures without authentication."""
        response = client.get("/api/textures")

        assert response.status_code == 401


class TestShapes:
    """Tests for shapes endpoint."""

    def test_get_shapes_empty(self, client, auth_headers):
        """Test getting shapes when none exist."""
        response = client.get("/api/shapes", headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_shapes_with_data(self, client, auth_headers, sample_attributes):
        """Test getting shapes with existing data."""
        response = client.get("/api/shapes", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        names = [s["description"] for s in data]
        assert "Round" in names
        assert "Square" in names

    def test_get_shapes_unauthorized(self, client):
        """Test getting shapes without authentication."""
        response = client.get("/api/shapes")

        assert response.status_code == 401
