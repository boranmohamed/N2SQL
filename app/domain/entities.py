"""
Core domain entities for the Vanna AI application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class QueryRequest:
    """Domain entity representing a natural language query request."""
    
    question: str
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Validate the question field."""
        if not self.question or not self.question.strip():
            raise ValueError("Question cannot be empty")
        
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class QueryResponse:
    """Domain entity representing a query response with SQL and results."""
    
    sql_query: str
    results: List[Dict[str, Any]]
    execution_time_ms: float
    row_count: int
    error_message: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate the response fields."""
        if not self.sql_query or not self.sql_query.strip():
            raise ValueError("SQL query cannot be empty")
        
        if self.execution_time_ms < 0:
            raise ValueError("Execution time cannot be negative")
        
        if self.row_count < 0:
            raise ValueError("Row count cannot be negative")


@dataclass
class HealthStatus:
    """Domain entity representing application health status."""
    
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    vanna_connected: bool
    
    def __post_init__(self) -> None:
        """Validate the health status fields."""
        if self.status not in ["healthy", "unhealthy", "degraded"]:
            raise ValueError("Status must be one of: healthy, unhealthy, degraded")
        
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
