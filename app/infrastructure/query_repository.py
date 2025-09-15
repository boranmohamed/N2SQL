"""
Query repository implementation for storing and retrieving queries.
"""
import uuid
from typing import Optional

from loguru import logger

from ..domain.entities import QueryRequest, QueryResponse
from ..domain.repositories import QueryRepository


class InMemoryQueryRepository(QueryRepository):
    """In-memory implementation of the query repository for development."""
    
    def __init__(self) -> None:
        """Initialize the in-memory repository."""
        self._queries: dict[str, QueryRequest] = {}
        self._responses: dict[str, QueryResponse] = {}
    
    async def save_query(self, query: QueryRequest) -> str:
        """
        Save a query request and return its ID.
        
        Args:
            query: Query request to save
            
        Returns:
            Generated query ID
        """
        query_id = str(uuid.uuid4())
        self._queries[query_id] = query
        logger.info(f"Saved query with ID: {query_id}")
        return query_id
    
    async def get_query_by_id(self, query_id: str) -> Optional[QueryRequest]:
        """
        Retrieve a query request by ID.
        
        Args:
            query_id: ID of the query to retrieve
            
        Returns:
            Query request if found, None otherwise
        """
        return self._queries.get(query_id)
    
    async def save_response(self, query_id: str, response: QueryResponse) -> None:
        """
        Save a query response.
        
        Args:
            query_id: ID of the query this response belongs to
            response: Query response to save
        """
        self._responses[query_id] = response
        logger.info(f"Saved response for query ID: {query_id}")
    
    async def get_response_by_id(self, query_id: str) -> Optional[QueryResponse]:
        """
        Retrieve a query response by query ID.
        
        Args:
            query_id: ID of the query to get response for
            
        Returns:
            Query response if found, None otherwise
        """
        return self._responses.get(query_id)
    
    async def get_all_queries(self) -> list[tuple[str, QueryRequest]]:
        """
        Get all stored queries with their IDs.
        
        Returns:
            List of (query_id, query_request) tuples
        """
        return list(self._queries.items())
    
    async def get_all_responses(self) -> list[tuple[str, QueryResponse]]:
        """
        Get all stored responses with their query IDs.
        
        Returns:
            List of (query_id, query_response) tuples
        """
        return list(self._responses.items())
