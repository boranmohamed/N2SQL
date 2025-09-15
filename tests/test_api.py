"""
Tests for the API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from app.interface.api import app


class TestHealthEndpoint:
    """Test cases for the health check endpoint."""
    
    def test_health_check_success(self, client: TestClient) -> None:
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "database_connected" in data
        assert "vanna_connected" in data
        assert "uptime_seconds" in data
        
        assert data["version"] == "0.1.0"
        assert isinstance(data["uptime_seconds"], (int, float))


class TestQueryEndpoint:
    """Test cases for the query endpoint."""
    
    def test_query_success(self, client: TestClient, sample_query_request: dict) -> None:
        """Test successful query processing."""
        response = client.post("/query", json=sample_query_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sql_query" in data
        assert "results" in data
        assert "execution_time_ms" in data
        assert "row_count" in data
        assert "error_message" in data
        
        # Check that SQL was generated
        assert data["sql_query"] != ""
        assert isinstance(data["results"], list)
        assert data["row_count"] >= 0
        assert data["execution_time_ms"] >= 0
    
    def test_query_without_user_id(self, client: TestClient) -> None:
        """Test query processing without user_id."""
        request_data = {"question": "How many users are there?"}
        
        response = client.post("/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["sql_query"] != ""
    
    def test_query_empty_question(self, client: TestClient) -> None:
        """Test query with empty question."""
        request_data = {"question": ""}
        
        response = client.post("/query", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid request" in data["detail"]
    
    def test_query_missing_question(self, client: TestClient) -> None:
        """Test query with missing question field."""
        request_data = {"user_id": "user123"}
        
        response = client.post("/query", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_query_whitespace_question(self, client: TestClient) -> None:
        """Test query with whitespace-only question."""
        request_data = {"question": "   "}
        
        response = client.post("/query", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid request" in data["detail"]


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_endpoint(self, client: TestClient) -> None:
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Welcome to Vanna AI Web Application"
        assert "version" in data["data"]
        assert "endpoints" in data["data"]
        assert data["data"]["version"] == "0.1.0"
        
        # Check that all expected endpoints are listed
        expected_endpoints = ["health", "query", "docs", "redoc"]
        for endpoint in expected_endpoints:
            assert endpoint in data["data"]["endpoints"]


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_invalid_json(self, client: TestClient) -> None:
        """Test handling of invalid JSON."""
        response = client.post("/query", data="invalid json")
        
        assert response.status_code == 422
    
    def test_method_not_allowed(self, client: TestClient) -> None:
        """Test method not allowed error."""
        response = client.get("/query")
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_not_found(self, client: TestClient) -> None:
        """Test not found error."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404  # Not Found
