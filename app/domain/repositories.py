"""
Repository interfaces for the domain layer.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import QueryRequest, QueryResponse, HealthStatus


class QueryRepository(ABC):
    """Abstract repository for query operations."""
    
    @abstractmethod
    async def save_query(self, query: QueryRequest) -> str:
        """Save a query request and return its ID."""
        pass
    
    @abstractmethod
    async def get_query_by_id(self, query_id: str) -> Optional[QueryRequest]:
        """Retrieve a query request by ID."""
        pass
    
    @abstractmethod
    async def save_response(self, query_id: str, response: QueryResponse) -> None:
        """Save a query response."""
        pass


class VannaRepository(ABC):
    """Abstract repository for Vanna AI operations."""
    
    @abstractmethod
    async def generate_sql(self, question: str) -> str:
        """Generate SQL from natural language question."""
        pass
    
    @abstractmethod
    async def check_connection(self) -> bool:
        """Check if Vanna AI is accessible."""
        pass


class DatabaseRepository(ABC):
    """Abstract repository for database operations."""
    
    @abstractmethod
    async def execute_query(self, sql: str) -> tuple[List[dict], float]:
        """Execute SQL query and return results with execution time."""
        pass
    
    @abstractmethod
    async def check_connection(self) -> bool:
        """Check if database is accessible."""
        pass
