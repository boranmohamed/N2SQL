"""
Pytest configuration and fixtures for the Vanna AI Web Application.
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient

from app.interface.api import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_query_request() -> dict:
    """Sample query request for testing."""
    return {
        "question": "How many users are there?",
        "user_id": "test_user_123"
    }


@pytest.fixture
def sample_query_response() -> dict:
    """Sample query response for testing."""
    return {
        "sql_query": "SELECT COUNT(*) FROM users",
        "results": [{"count": 42}],
        "execution_time_ms": 150.5,
        "row_count": 1,
        "error_message": None
    }
