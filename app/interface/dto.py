"""
Data Transfer Objects (DTOs) for the API interface.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequestDTO(BaseModel):
    """DTO for query request."""
    
    question: str = Field(..., description="Natural language question to convert to SQL")
    user_id: Optional[str] = Field(None, description="Optional user identifier")


class QueryResponseDTO(BaseModel):
    """DTO for query response."""
    
    sql_query: str = Field(..., description="Generated SQL query")
    results: List[Dict[str, Any]] = Field(..., description="Query execution results")
    execution_time_ms: float = Field(..., description="Total execution time in milliseconds")
    row_count: int = Field(..., description="Number of rows returned")
    error_message: Optional[str] = Field(None, description="Error message if query failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponseDTO(BaseModel):
    """DTO for health check response."""
    
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    database_connected: bool = Field(..., description="Database connection status")
    vanna_connected: bool = Field(..., description="Vanna AI connection status")
    uptime_seconds: Optional[float] = Field(None, description="Application uptime in seconds")


class ErrorResponseDTO(BaseModel):
    """DTO for error responses."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")


class SuccessResponseDTO(BaseModel):
    """DTO for success responses."""
    
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
