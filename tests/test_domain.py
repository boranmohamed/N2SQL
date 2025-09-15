"""
Tests for the domain layer entities.
"""
import pytest
from datetime import datetime

from app.domain.entities import QueryRequest, QueryResponse, HealthStatus


class TestQueryRequest:
    """Test cases for QueryRequest entity."""
    
    def test_valid_query_request(self) -> None:
        """Test creating a valid query request."""
        question = "How many users are there?"
        user_id = "user123"
        
        query = QueryRequest(question=question, user_id=user_id)
        
        assert query.question == question
        assert query.user_id == user_id
        assert query.timestamp is not None
        assert isinstance(query.timestamp, datetime)
    
    def test_query_request_without_user_id(self) -> None:
        """Test creating a query request without user_id."""
        question = "How many users are there?"
        
        query = QueryRequest(question=question)
        
        assert query.question == question
        assert query.user_id is None
        assert query.timestamp is not None
    
    def test_query_request_empty_question(self) -> None:
        """Test that empty question raises ValueError."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            QueryRequest(question="")
    
    def test_query_request_whitespace_question(self) -> None:
        """Test that whitespace-only question raises ValueError."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            QueryRequest(question="   ")


class TestQueryResponse:
    """Test cases for QueryResponse entity."""
    
    def test_valid_query_response(self) -> None:
        """Test creating a valid query response."""
        sql_query = "SELECT COUNT(*) FROM users"
        results = [{"count": 42}]
        execution_time_ms = 150.5
        row_count = 1
        
        response = QueryResponse(
            sql_query=sql_query,
            results=results,
            execution_time_ms=execution_time_ms,
            row_count=row_count
        )
        
        assert response.sql_query == sql_query
        assert response.results == results
        assert response.execution_time_ms == execution_time_ms
        assert response.row_count == row_count
        assert response.error_message is None
    
    def test_query_response_with_error(self) -> None:
        """Test creating a query response with error message."""
        sql_query = ""
        results = []
        execution_time_ms = 0
        row_count = 0
        error_message = "Database connection failed"
        
        response = QueryResponse(
            sql_query=sql_query,
            results=results,
            execution_time_ms=execution_time_ms,
            row_count=row_count,
            error_message=error_message
        )
        
        assert response.error_message == error_message
    
    def test_query_response_empty_sql(self) -> None:
        """Test that empty SQL query raises ValueError."""
        with pytest.raises(ValueError, match="SQL query cannot be empty"):
            QueryResponse(
                sql_query="",
                results=[],
                execution_time_ms=0,
                row_count=0
            )
    
    def test_query_response_negative_execution_time(self) -> None:
        """Test that negative execution time raises ValueError."""
        with pytest.raises(ValueError, match="Execution time cannot be negative"):
            QueryResponse(
                sql_query="SELECT 1",
                results=[],
                execution_time_ms=-1,
                row_count=0
            )
    
    def test_query_response_negative_row_count(self) -> None:
        """Test that negative row count raises ValueError."""
        with pytest.raises(ValueError, match="Row count cannot be negative"):
            QueryResponse(
                sql_query="SELECT 1",
                results=[],
                execution_time_ms=0,
                row_count=-1
            )


class TestHealthStatus:
    """Test cases for HealthStatus entity."""
    
    def test_valid_health_status(self) -> None:
        """Test creating a valid health status."""
        status = "healthy"
        version = "1.0.0"
        database_connected = True
        vanna_connected = True
        
        health = HealthStatus(
            status=status,
            timestamp=None,  # Will be set in __post_init__
            version=version,
            database_connected=database_connected,
            vanna_connected=vanna_connected
        )
        
        assert health.status == status
        assert health.version == version
        assert health.database_connected == database_connected
        assert health.vanna_connected == vanna_connected
        assert health.timestamp is not None
        assert isinstance(health.timestamp, datetime)
    
    def test_invalid_status(self) -> None:
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Status must be one of: healthy, unhealthy, degraded"):
            HealthStatus(
                status="invalid",
                timestamp=None,
                version="1.0.0",
                database_connected=True,
                vanna_connected=True
            )
    
    def test_all_valid_statuses(self) -> None:
        """Test all valid status values."""
        valid_statuses = ["healthy", "unhealthy", "degraded"]
        
        for status in valid_statuses:
            health = HealthStatus(
                status=status,
                timestamp=None,
                version="1.0.0",
                database_connected=True,
                vanna_connected=True
            )
            assert health.status == status
