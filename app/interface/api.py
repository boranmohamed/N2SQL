"""
FastAPI application with all endpoints.
"""
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from ..application.use_cases import HealthCheckUseCase, ProcessQueryUseCase
# Domain entities imported as needed
from ..infrastructure.database import db_manager, SQLiteDatabaseRepository
from ..infrastructure.query_repository import InMemoryQueryRepository
from ..infrastructure.vanna_factory import get_vanna_client_from_env
from .dto import (
    ErrorResponseDTO,
    HealthResponseDTO,
    QueryRequestDTO,
    QueryResponseDTO,
    SuccessResponseDTO,
)

# Application startup time
STARTUP_TIME = time.time()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Vanna AI Web Application",
        description="A production-ready Python web application that integrates with Vanna.AI to convert natural language queries into SQL queries",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Add startup and shutdown events
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)
    
    return app


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    
    error_response = ErrorResponseDTO(
        error="Internal server error",
        detail=str(exc) if app.debug else "An unexpected error occurred",
        request_id=request.headers.get("X-Request-ID", "unknown"),
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict(),
    )


async def startup_event() -> None:
    """Application startup event handler."""
    logger.info("🚀 APPLICATION STARTUP: Starting Vanna AI Web Application...")
    logger.info("   📅 Startup time: " + datetime.now().isoformat())
    
    # Initialize database
    try:
        logger.info("   🗄️  Initializing database...")
        await db_manager.check_connection()
        logger.info("   ✅ Database connection established and initialized")
    except Exception as e:
        logger.error(f"   ❌ Failed to establish database connection: {e}")
        logger.error(f"   📋 Error type: {type(e).__name__}")
    
    logger.info("   🎉 Application startup completed successfully")


async def shutdown_event() -> None:
    """Application shutdown event handler."""
    logger.info("🛑 APPLICATION SHUTDOWN: Shutting down Vanna AI Web Application...")
    logger.info("   📅 Shutdown time: " + datetime.now().isoformat())
    
    # Clean up database connections
    try:
        logger.info("   🗄️  Cleaning up database connections...")
        # No dispose method needed for native SQLite
        logger.info("   ✅ Database connections cleaned up successfully")
    except Exception as e:
        logger.error(f"   ❌ Error during database cleanup: {e}")
    
    logger.info("   🎉 Application shutdown completed successfully")


# Create the FastAPI app instance
app = create_app()

# Mount static files and templates
templates_path = Path(__file__).parent.parent.parent / "templates"
if templates_path.exists():
    app.mount("/static", StaticFiles(directory=str(templates_path)), name="static")

# Add route to serve the main HTML page
@app.get("/")
async def serve_frontend():
    """Serve the main frontend HTML page."""
    templates_path = Path(__file__).parent.parent.parent / "templates"
    index_path = templates_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {"message": "Frontend not found. Please ensure templates/index.html exists."}


@app.get(
    "/health",
    response_model=HealthResponseDTO,
    summary="Health Check",
    description="Check the health status of the application and its dependencies",
    tags=["Health"],
)
async def health_check() -> HealthResponseDTO:
    """Health check endpoint."""
    logger.info(f"🏥 HEALTH CHECK REQUESTED")
    logger.info(f"   📅 Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Create repositories
        vanna_repo = get_vanna_client_from_env()
        db_repo = SQLiteDatabaseRepository(db_manager)
        
        logger.info(f"   🔧 Repositories created successfully")
        
        # Create and execute health check use case
        health_use_case = HealthCheckUseCase(
            vanna_repo=vanna_repo,
            db_repo=db_repo,
            version="0.1.0",
        )
        
        logger.info(f"   ⚙️  Health check use case created, executing...")
        
        health_status = await health_use_case.execute()
        
        logger.info(f"   ✅ Health check executed successfully")
        logger.info(f"   📊 Status: {health_status.status}")
        logger.info(f"   🗄️  Database connected: {health_status.database_connected}")
        logger.info(f"   🤖 Vanna connected: {health_status.vanna_connected}")
        
        # Calculate uptime
        uptime_seconds = time.time() - STARTUP_TIME
        
        response_dto = HealthResponseDTO(
            status=health_status.status,
            timestamp=health_status.timestamp,
            version=health_status.version,
            database_connected=health_status.database_connected,
            vanna_connected=health_status.vanna_connected,
            uptime_seconds=uptime_seconds,
        )
        
        # Log response details
        logger.info(f"   📤 HEALTH RESPONSE SENT")
        logger.info(f"      📊 Status: {response_dto.status}")
        logger.info(f"      🗄️  Database: {response_dto.database_connected}")
        logger.info(f"      🤖 Vanna: {response_dto.vanna_connected}")
        logger.info(f"      ⏱️  Uptime: {response_dto.uptime_seconds:.2f}s")
        
        return response_dto
        
    except Exception as e:
        logger.error(f"   ❌ HEALTH CHECK FAILED: {e}")
        logger.error(f"   📋 Error type: {type(e).__name__}")
        logger.error(f"   🔍 Error details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}",
        )


@app.post(
    "/query",
    response_model=QueryResponseDTO,
    summary="Process Natural Language Query",
    description="Convert a natural language question to SQL and execute it",
    tags=["Query"],
    responses={
        200: {"description": "Query processed successfully"},
        400: {"description": "Invalid request"},
        500: {"description": "Internal server error"},
    },
)
async def process_query(query_request: QueryRequestDTO) -> QueryResponseDTO:
    """Process a natural language query and return SQL with results."""
    # Log incoming request
    logger.info(f"🚀 QUERY REQUEST RECEIVED")
    logger.info(f"   📝 Question: '{query_request.question}'")
    logger.info(f"   👤 User ID: {query_request.user_id}")
    logger.info(f"   📅 Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Create repositories
        query_repo = InMemoryQueryRepository()
        vanna_repo = get_vanna_client_from_env()
        db_repo = SQLiteDatabaseRepository(db_manager)
        
        logger.info(f"   🔧 Repositories created successfully")
        
        # Create and execute query processing use case
        query_use_case = ProcessQueryUseCase(
            query_repo=query_repo,
            vanna_repo=vanna_repo,
            db_repo=db_repo,
        )
        
        logger.info(f"   ⚙️  Use case created, executing...")
        
        response = await query_use_case.execute(
            question=query_request.question,
            user_id=query_request.user_id,
        )
        
        logger.info(f"   ✅ Use case executed successfully")
        logger.info(f"   🎯 Generated SQL: '{response.sql_query}'")
        logger.info(f"   📊 Results count: {response.row_count}")
        logger.info(f"   ⏱️  Execution time: {response.execution_time_ms:.2f}ms")
        
        if response.error_message:
            logger.warning(f"   ⚠️  Error message: {response.error_message}")
        
        # Convert domain entity to DTO
        response_dto = QueryResponseDTO(
            sql_query=response.sql_query,
            results=response.results,
            execution_time_ms=response.execution_time_ms,
            row_count=response.row_count,
            error_message=response.error_message,
        )
        
        # Log response details
        logger.info(f"   📤 RESPONSE SENT")
        logger.info(f"      🎯 SQL Query: '{response_dto.sql_query}'")
        logger.info(f"      📊 Row Count: {response_dto.row_count}")
        logger.info(f"      ⏱️  Execution Time: {response_dto.execution_time_ms:.2f}ms")
        logger.info(f"      ⚠️  Error Message: {response_dto.error_message or 'None'}")
        
        return response_dto
        
    except ValueError as e:
        logger.warning(f"   ❌ VALIDATION ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except RuntimeError as e:
        logger.error(f"   ❌ RUNTIME ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"   ❌ UNEXPECTED ERROR: {e}")
        logger.error(f"   📋 Error type: {type(e).__name__}")
        logger.error(f"   🔍 Error details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during query processing",
        )


@app.get(
    "/",
    response_model=SuccessResponseDTO,
    summary="Root Endpoint",
    description="Welcome message and API information",
    tags=["Root"],
)
async def root() -> SuccessResponseDTO:
    """Root endpoint with API information."""
    return SuccessResponseDTO(
        message="Welcome to Vanna AI Web Application",
        data={
            "version": "0.1.0",
            "description": "Convert natural language to SQL queries using Vanna.AI",
            "endpoints": {
                "health": "/health",
                "query": "/query",
                "docs": "/docs",
                "redoc": "/redoc",
            },
        },
    )


@app.get("/rag/status")
async def get_rag_status():
    """Get RAG system status and capabilities."""
    try:
        # Create a new Vanna client instance to check RAG status
        vanna_client = get_vanna_client_from_env()
        
        # Initialize RAG system to get accurate status
        if hasattr(vanna_client, '_rag_system') and vanna_client._rag_system:
            import asyncio
            try:
                asyncio.run(vanna_client._rag_system.initialize())
            except Exception as e:
                logger.warning(f"RAG initialization failed: {e}")
        rag_available = False
        rag_details = {}
        collection_stats = {}
        
        if hasattr(vanna_client, '_rag_system') and vanna_client._rag_system:
            rag_available = vanna_client._rag_system.is_available()
            rag_details = {
                'vector_database': 'Qdrant Vector Database',
                'embedding_model': 'Enhanced Vector Search',
                'schema_indexed': rag_available,
                'context_enhancement': 'Active' if rag_available else 'Fallback'
            }
            
            # Get collection statistics if available
            if hasattr(vanna_client._rag_system, 'get_collection_stats'):
                collection_stats = vanna_client._rag_system.get_collection_stats()
        
        return {
            "rag_system": {
                "available": rag_available,
                "status": "Active" if rag_available else "Fallback Mode",
                "capabilities": [
                    "Dynamic Schema Understanding",
                    "Vector-based Context Retrieval", 
                    "Intelligent Prompt Enhancement",
                    "Semantic Similarity Search",
                    "Qdrant Vector Database",
                    "Real-time Schema Updates"
                ] if rag_available else [
                    "Basic Schema Context",
                    "Pattern-based Fallback"
                ],
                "details": rag_details,
                "collection_stats": collection_stats
            },
            "sql_generation": {
                "enhanced": rag_available,
                "context_aware": rag_available,
                "fallback_mode": not rag_available,
                "vector_search": "Qdrant Vector DB" if rag_available else "None"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get RAG status: {e}")
        return {
            "rag_system": {
                "available": False,
                "status": "Error",
                "error": str(e)
            }
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.interface.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
