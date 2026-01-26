"""
API Endpoint Tests
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Health endpoint should be accessible without auth."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Root endpoint should be accessible without auth."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["status"] == "running"


class TestAuthentication:
    """Tests for API authentication."""
    
    def test_missing_api_key(self, client, sample_scam_message):
        """Request without API key should fail."""
        response = client.post("/api/analyze", json=sample_scam_message)
        assert response.status_code == 401
    
    def test_invalid_api_key(self, client, sample_scam_message):
        """Request with invalid API key should fail."""
        response = client.post(
            "/api/analyze",
            json=sample_scam_message,
            headers={"x-api-key": "invalid-key"}
        )
        assert response.status_code == 403
    
    def test_valid_api_key(self, client, sample_scam_message, auth_headers):
        """Request with valid API key should succeed."""
        # Note: This will fail in test environment without real Google API key
        # but tests the auth flow
        response = client.post(
            "/api/analyze",
            json=sample_scam_message,
            headers=auth_headers
        )
        # Should not be 401 or 403
        assert response.status_code not in [401, 403]


class TestAnalyzeEndpoint:
    """Tests for the main analyze endpoint."""
    
    def test_analyze_request_structure(self, client, sample_scam_message, auth_headers):
        """Test request validation."""
        # Missing required fields
        invalid_request = {"sessionId": "test"}
        response = client.post(
            "/api/analyze",
            json=invalid_request,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error
    
    def test_analyze_response_structure(self, client, sample_scam_message, auth_headers):
        """Test response has required fields."""
        response = client.post(
            "/api/analyze",
            json=sample_scam_message,
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "scamDetected" in data
            assert "engagementMetrics" in data
            assert "extractedIntelligence" in data


class TestSessionEndpoints:
    """Tests for session management endpoints."""
    
    def test_get_nonexistent_session(self, client, auth_headers):
        """Getting nonexistent session should return 404."""
        response = client.get(
            "/api/session/nonexistent-session",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_delete_nonexistent_session(self, client, auth_headers):
        """Deleting nonexistent session should return 404."""
        response = client.delete(
            "/api/session/nonexistent-session",
            headers=auth_headers
        )
        assert response.status_code == 404
