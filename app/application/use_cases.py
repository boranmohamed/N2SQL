"""
Use cases for the Vanna AI application.
"""
import time
from typing import List, Optional

from ..domain.entities import QueryRequest, QueryResponse, HealthStatus
from ..domain.repositories import QueryRepository, VannaRepository, DatabaseRepository


class ProcessQueryUseCase:
    """Use case for processing natural language queries to SQL."""
    
    def __init__(
        self,
        query_repo: QueryRepository,
        vanna_repo: VannaRepository,
        db_repo: DatabaseRepository,
    ) -> None:
        """Initialize the use case with required repositories."""
        self.query_repo = query_repo
        self.vanna_repo = vanna_repo
        self.db_repo = db_repo
    
    async def execute(self, question: str, user_id: Optional[str] = None) -> QueryResponse:
        """
        Execute the complete NL-to-SQL workflow.
        
        Args:
            question: Natural language question
            user_id: Optional user identifier
            
        Returns:
            QueryResponse with SQL and results
            
        Raises:
            ValueError: If question is invalid
            RuntimeError: If any step fails
        """
        from loguru import logger
        
        logger.info(f"USE CASE: Starting query processing workflow")
        logger.info(f"Question: '{question}'")
        logger.info(f"User ID: {user_id or 'default'}")
        
        # Create and validate query request
        query_request = QueryRequest(question=question, user_id=user_id)
        logger.info(f"Query request created")
        
        # Save the query request
        query_id = await self.query_repo.save_query(query_request)
        logger.info(f"Query saved with ID: {query_id}")
        
        try:
            # Generate SQL using Vanna AI
            logger.info(f"Step 1: Generating SQL using Vanna AI")
            start_time = time.time()
            sql_query = await self.vanna_repo.generate_sql(question)
            vanna_time = (time.time() - start_time) * 1000
            logger.info(f"SQL generation completed in {vanna_time:.2f}ms")
            
            # Execute the generated SQL
            logger.info(f"Step 2: Executing SQL query")
            start_time = time.time()
            results, execution_time = await self.db_repo.execute_query(sql_query)
            db_time = (time.time() - start_time) * 1000
            logger.info(f"SQL execution completed in {db_time:.2f}ms")
            
            # Create response
            total_time = vanna_time + db_time
            response = QueryResponse(
                sql_query=sql_query,
                results=results,
                execution_time_ms=total_time,
                row_count=len(results),
            )
            
            logger.info(f"Response created:")
            logger.info(f"SQL: '{sql_query}'")
            logger.info(f"Rows: {len(results)}")
            logger.info(f"Total time: {total_time:.2f}ms")
            
            # Save the response
            logger.info(f"Step 3: Saving response to repository")
            await self.query_repo.save_response(query_id, response)
            logger.info(f"Response saved successfully")
            
            logger.info(f"Query processing workflow completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Query processing workflow failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            
            # Create error response
            error_response = QueryResponse(
                sql_query="",
                results=[],
                execution_time_ms=0,
                row_count=0,
                error_message=str(e),
            )
            
            # Save error response
            try:
                await self.query_repo.save_response(query_id, error_response)
                logger.info(f"Error response saved to repository")
            except Exception as save_error:
                logger.error(f"Failed to save error response: {save_error}")
            
            raise RuntimeError(f"Failed to process query: {str(e)}") from e


class HealthCheckUseCase:
    """Use case for checking application health."""
    
    def __init__(
        self,
        vanna_repo: VannaRepository,
        db_repo: DatabaseRepository,
        version: str,
    ) -> None:
        """Initialize the use case with required repositories and version."""
        self.vanna_repo = vanna_repo
        self.db_repo = db_repo
        self.version = version
    
    async def execute(self) -> HealthStatus:
        """
        Check the health of all application components.
        
        Returns:
            HealthStatus with current health information
        """
        from loguru import logger
        
        logger.info(f"🏥 HEALTH CHECK: Starting health check")
        logger.info(f"   📋 Version: {self.version}")
        
        # Check Vanna AI connection
        logger.info(f"   🤖 Checking Vanna AI connection...")
        vanna_connected = await self.vanna_repo.check_connection()
        logger.info(f"   🤖 Vanna AI connection: {'Connected' if vanna_connected else 'Disconnected'}")
        
        # Check database connection
        logger.info(f"   🗄️  Checking database connection...")
        db_connected = await self.db_repo.check_connection()
        logger.info(f"   🗄️  Database connection: {'Connected' if db_connected else 'Disconnected'}")
        
        # Determine overall status
        if vanna_connected and db_connected:
            status = "healthy"
            logger.info(f"Overall status: HEALTHY")
        elif not vanna_connected and not db_connected:
            status = "unhealthy"
            logger.error(f"Overall status: UNHEALTHY")
        else:
            status = "degraded"
            logger.warning(f"Overall status: DEGRADED")
        
        health_status = HealthStatus(
            status=status,
            timestamp=None,  # Will be set in __post_init__
            version=self.version,
            database_connected=db_connected,
            vanna_connected=vanna_connected,
        )
        
        logger.info(f"Health check summary:")
        logger.info(f"Status: {health_status.status}")
        logger.info(f"Vanna: {health_status.vanna_connected}")
        logger.info(f"Database: {health_status.database_connected}")
        logger.info(f"Timestamp: {health_status.timestamp}")
        
        return health_status
