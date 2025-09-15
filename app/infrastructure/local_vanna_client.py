"""
Local Vanna AI client for connecting to the local Vanna server.
"""
import asyncio
import httpx
from typing import Optional, Dict, Any, List
from loguru import logger
from pydantic import BaseModel

from .config import settings
from .enhanced_rag_system import EnhancedRAGSystem


class LocalVannaRequest(BaseModel):
    """Request model for local Vanna server."""
    question: str
    user_id: Optional[str] = None


class LocalVannaResponse(BaseModel):
    """Response model from local Vanna server."""
    question: str
    sql: str
    success: bool
    message: str


class LocalTrainingRequest(BaseModel):
    """Training request model for local Vanna server."""
    question: str
    sql: str
    ddl: Optional[str] = None
    documentation: Optional[str] = None


class LocalVannaClientRepository:
    """Local Vanna AI client connecting to local server with RAG integration."""
    
    def __init__(self) -> None:
        """Initialize the local Vanna client."""
        self._initialized = False
        self._server_url = getattr(settings, 'local_vanna_server_url', 'http://localhost:8001')
        self._timeout = getattr(settings, 'local_vanna_timeout', 30)
        self._max_retries = getattr(settings, 'local_vanna_max_retries', 3)
        
        # Initialize enhanced RAG system for intelligent context retrieval
        db_url = str(settings.database_url)
        db_path = db_url.replace("sqlite:///", "")
        if db_path == "vanna_app.db":
            db_path = "vanna_app_clean.db"  # Use the populated database
        self._rag_system = EnhancedRAGSystem(db_path=db_path)
        self._rag_initialized = False
        logger.info("✅ Enhanced RAG system created (will initialize on first use)")
        
        # Initialize HTTP client with longer timeout for training
        self._http_client = httpx.AsyncClient(
            timeout=60.0,  # 60 seconds for training operations
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        
        logger.info(f"🔗 Local Vanna client initialized for server: {self._server_url}")
    
    async def _initialize_rag_system(self) -> None:
        """Initialize the RAG system on first use."""
        if not self._rag_initialized:
            try:
                await self._rag_system.initialize()
                self._rag_initialized = True
                logger.info("✅ Enhanced RAG system initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize RAG system: {e}")
                raise
    
    async def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict[str, Any]] = None,
        retries: int = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to local Vanna server with retry logic."""
        if retries is None:
            retries = self._max_retries
            
        url = f"{self._server_url}{endpoint}"
        
        # Use custom timeout if provided, otherwise use client default
        client_timeout = timeout if timeout else None
        
        for attempt in range(retries + 1):
            try:
                if method.upper() == "GET":
                    response = await self._http_client.get(url, timeout=client_timeout)
                elif method.upper() == "POST":
                    response = await self._http_client.post(url, json=data, timeout=client_timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except httpx.TimeoutException:
                logger.warning(f"⏱️ Timeout on attempt {attempt + 1}/{retries + 1} for {url}")
                if attempt == retries:
                    raise Exception(f"Request timeout after {retries + 1} attempts")
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:  # Server error - retry
                    logger.warning(f"🔄 Server error {e.response.status_code} on attempt {attempt + 1}/{retries + 1}")
                    if attempt == retries:
                        raise Exception(f"Server error after {retries + 1} attempts: {e.response.status_code}")
                else:  # Client error - don't retry
                    raise Exception(f"Client error: {e.response.status_code} - {e.response.text}")
                    
            except Exception as e:
                logger.warning(f"🔄 Request failed on attempt {attempt + 1}/{retries + 1}: {e}")
                if attempt == retries:
                    raise Exception(f"Request failed after {retries + 1} attempts: {e}")
            
            # Wait before retry
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Unexpected error in request retry logic")
    
    async def _check_server_health(self) -> bool:
        """Check if the local Vanna server is healthy."""
        try:
            response = await self._make_request("/health")
            return response.get("status") == "healthy" and response.get("vanna_initialized", False)
        except Exception as e:
            logger.error(f"❌ Local Vanna server health check failed: {e}")
            return False
    
    async def initialize(self) -> bool:
        """Initialize the local Vanna client."""
        try:
            # Check server health
            if not await self._check_server_health():
                raise Exception("Local Vanna server is not healthy")
            
            # Initialize RAG system
            await self._initialize_rag_system()
            
            self._initialized = True
            logger.info("✅ Local Vanna client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize local Vanna client: {e}")
            return False
    
    async def generate_sql(self, question: str, user_id: Optional[str] = None) -> str:
        """Generate SQL from natural language question."""
        if not self._initialized:
            if not await self.initialize():
                raise Exception("Local Vanna client not initialized")
        
        try:
            # Get RAG context for the question
            rag_context = ""
            if self._rag_initialized:
                try:
                    rag_context_list = await self._rag_system.retrieve_relevant_context(question)
                    rag_context = "\n".join(rag_context_list) if rag_context_list else ""
                    logger.info(f"🔍 Retrieved RAG context: {len(rag_context)} characters")
                except Exception as e:
                    logger.warning(f"⚠️ RAG context retrieval failed: {e}")
            
            # Prepare the enhanced question with RAG context
            enhanced_question = question
            if rag_context:
                enhanced_question = f"{question}\n\nContext: {rag_context}"
            
            # Send request to local Vanna server
            request_data = LocalVannaRequest(question=enhanced_question, user_id=user_id)
            response_data = await self._make_request(
                "/generate_sql", 
                method="POST", 
                data=request_data.dict()
            )
            
            response = LocalVannaResponse(**response_data)
            
            if not response.success:
                raise Exception(f"SQL generation failed: {response.message}")
            
            logger.info(f"✅ Generated SQL for question: {question[:100]}...")
            return response.sql
            
        except Exception as e:
            logger.error(f"❌ Failed to generate SQL: {e}")
            raise
    
    async def train_with_sql(self, question: str, sql: str, user_id: Optional[str] = None) -> bool:
        """Train the local Vanna model with a question-SQL pair."""
        if not self._initialized:
            if not await self.initialize():
                raise Exception("Local Vanna client not initialized")
        
        try:
            request_data = LocalTrainingRequest(question=question, sql=sql)
            response = await self._make_request(
                "/train", 
                method="POST", 
                data=request_data.dict(),
                timeout=60.0  # 60 seconds for training
            )
            
            success = response.get("success", False)
            if success:
                logger.info(f"✅ Trained Vanna with question: {question[:100]}...")
            else:
                logger.warning(f"⚠️ Training response: {response.get('message', 'Unknown error')}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to train Vanna: {e}")
            return False
    
    async def train_with_ddl(self, ddl: str, user_id: Optional[str] = None) -> bool:
        """Train the local Vanna model with DDL."""
        if not self._initialized:
            if not await self.initialize():
                raise Exception("Local Vanna client not initialized")
        
        try:
            request_data = LocalTrainingRequest(question="", sql="", ddl=ddl)
            response = await self._make_request(
                "/train", 
                method="POST", 
                data=request_data.dict(),
                timeout=60.0  # 60 seconds for training
            )
            
            success = response.get("success", False)
            if success:
                logger.info(f"✅ Trained Vanna with DDL: {ddl[:100]}...")
            else:
                logger.warning(f"⚠️ Training response: {response.get('message', 'Unknown error')}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to train Vanna with DDL: {e}")
            return False
    
    async def get_training_data(self) -> List[Dict[str, Any]]:
        """Get all training data from the local Vanna server."""
        if not self._initialized:
            if not await self.initialize():
                raise Exception("Local Vanna client not initialized")
        
        try:
            response = await self._make_request("/training_data")
            return response.get("training_data", [])
            
        except Exception as e:
            logger.error(f"❌ Failed to get training data: {e}")
            return []
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if hasattr(self, '_http_client'):
            await self._http_client.aclose()
        logger.info("🔒 Local Vanna client closed")


# Factory function for dependency injection
def create_local_vanna_client() -> LocalVannaClientRepository:
    """Create and return a local Vanna client instance."""
    return LocalVannaClientRepository()
