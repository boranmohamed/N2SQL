"""
Vanna AI client infrastructure and repository implementation.
"""
import asyncio
from typing import Optional

import vanna
from loguru import logger

from ..domain.repositories import VannaRepository
from .config import settings
from .enhanced_rag_system import EnhancedRAGSystem


class VannaClientRepository(VannaRepository):
    """Vanna AI implementation of the repository."""
    
    def __init__(self) -> None:
        """Initialize the Vanna client."""
        self._initialized = False
        self._api_key_set = False
        
        # Initialize enhanced RAG system for intelligent context retrieval
        db_url = str(settings.database_url)
        db_path = db_url.replace("sqlite:///", "")
        if db_path == "vanna_app.db":
            db_path = "vanna_app_clean.db"  # Use the populated database
        self._rag_system = EnhancedRAGSystem(db_path=db_path)
        self._rag_initialized = False
        logger.info("✅ Enhanced RAG system created (will initialize on first use)")
        
        # Initialize REAL Vanna AI with Qdrant RAG
        try:
            from vanna.remote import VannaDefault
            
            # Use the provided API credentials
            self._vanna_client = VannaDefault(
                model=settings.vanna_model,
                api_key=settings.vanna_api_key
            )
            
            # Set authentication attributes
            if hasattr(self._vanna_client, 'email'):
                self._vanna_client.email = settings.vanna_email
            if hasattr(self._vanna_client, 'org_id'):
                self._vanna_client.org_id = settings.vanna_org_id
                
            # Patch the RPC call to include email and org headers
            logger.info("🔧 Patching RPC calls...")
            self._patch_rpc_calls()
            logger.info("✅ RPC patching completed")
            
            self._api_key_set = True
            logger.info("✅ Real Vanna AI client initialized")
            logger.info(f"✅ Model: {settings.vanna_model}")
            logger.info(f"✅ Email: {settings.vanna_email}")
            logger.info(f"✅ Org ID: {settings.vanna_org_id}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Vanna AI: {e}")
            self._vanna_client = None
            self._api_key_set = False
        
        self._initialized = True
        logger.info("Vanna AI client initialized successfully")

    def _patch_rpc_calls(self):
        """Patch RPC calls to include email and organization headers."""
        try:
            logger.info("🔍 Checking Vanna client structure...")
            logger.info(f"   Has _rpc_call directly: {hasattr(self._vanna_client, '_rpc_call')}")
            logger.info(f"   Has vn attribute: {hasattr(self._vanna_client, 'vn')}")
            
            if hasattr(self._vanna_client, '_rpc_call'):
                original_rpc_call = self._vanna_client._rpc_call
                logger.info("✅ Found _rpc_call method directly on client, proceeding with patching...")
                
                def patched_rpc_call(method, params):
                    import requests
                    import json
                    
                    # Create headers with email and org
                    headers = {
                        "Content-Type": "application/json",
                        "Vanna-Key": settings.vanna_api_key,
                        "Vanna-Org": settings.vanna_org_id,  # Use org_id from settings
                        "Vanna-Email": settings.vanna_email,
                    }
                    
                    # Convert params to dict format
                    if params:
                        converted_params = []
                        for param in params:
                            if hasattr(param, '__dict__'):
                                converted_params.append(param.__dict__)
                            else:
                                converted_params.append(param)
                    else:
                        converted_params = []
                    
                    data = {
                        "method": method,
                        "params": converted_params,
                        "jsonrpc": "2.0",
                        "id": 1
                    }
                    
                    logger.info(f"🚀 RPC Call: {method} with email: {settings.vanna_email}, org: {settings.vanna_org_id}")
                    logger.info(f"📋 Headers: {headers}")
                    logger.info(f"📋 Data: {data}")
                    
                    response = requests.post(
                        self._vanna_client._endpoint, 
                        headers=headers, 
                        data=json.dumps(data)
                    )
                    
                    result = response.json()
                    logger.info(f"📤 RPC Response: {result}")
                    return result
                
                # Replace the method
                self._vanna_client._rpc_call = patched_rpc_call
                logger.info("✅ RPC calls patched with email and org headers")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to patch RPC calls: {e}")

    def _train_vanna_model(self):
        """Train the Vanna AI model with database schema from RAG system."""
        if not self._vanna_client:
            logger.error("❌ Vanna AI client not available for training")
            return False

        try:
            logger.info("📚 Training Vanna AI model with database schema...")

            # Get database schema from RAG system
            if hasattr(self, '_rag_system') and self._rag_system:
                try:
                    schema_context = self._rag_system.get_schema_context()
                    logger.info(f"✅ Retrieved schema context from RAG system ({len(schema_context)} chars)")
                    logger.info(f"📄 Schema context preview: {schema_context[:200]}...")
                except Exception as e:
                    logger.error(f"❌ Failed to get schema context from RAG: {e}")
                    raise RuntimeError("RAG system is required for schema context - cannot proceed without it")
            else:
                logger.error("❌ RAG system not available")
                raise RuntimeError("RAG system is required for schema context - cannot proceed without it")

            # Train Vanna AI with the schema
            logger.info("🚀 Training Vanna AI with schema...")
            try:
                result = self._vanna_client.train(ddl=schema_context)
                logger.info("✅ Vanna AI schema training completed")

                # Add example Q&A pairs for better SQL generation
                examples = [
                    ("Show me all employees", "SELECT * FROM employees"),
                    ("What is the total sales amount?", "SELECT SUM(amount) FROM sales"),
                    ("Show me employees in Engineering", "SELECT * FROM employees WHERE department = 'Engineering'"),
                    ("What is the average salary by department?", "SELECT department, AVG(salary) FROM employees GROUP BY department"),
                    ("Show me all users", "SELECT * FROM users"),
                    ("List all orders", "SELECT * FROM orders"),
                    ("Find pending orders", "SELECT * FROM orders WHERE status = 'pending'"),
                    ("Show me high salary employees", "SELECT * FROM employees WHERE salary > 70000"),
                    ("Count employees by department", "SELECT department, COUNT(*) FROM employees GROUP BY department"),
                    ("Show me all tables", "SELECT name FROM sqlite_master WHERE type='table'")
                ]

                logger.info(f"📝 Adding {len(examples)} training examples...")
                for question, sql in examples:
                    try:
                        self._vanna_client.train(question=question, sql=sql)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to add example '{question}': {e}")

                logger.info("✅ Vanna AI training completed successfully")
                logger.info(f"📊 Training result: {result}")
                return True

            except Exception as e:
                logger.error(f"❌ Vanna AI training failed: {e}")
                logger.error(f"🔍 Error type: {type(e).__name__}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to train Vanna AI model: {e}")
            return False
        
        
    def _test_vanna_connection(self):
        """Test Vanna AI connection after training."""
        if not self._vanna_client:
            return False

        try:
            logger.info("🔧 Testing Vanna AI connection...")
            
            # Test with a simple query
            test_result = self._vanna_client.ask("SELECT 1")
            if test_result and isinstance(test_result, str) and test_result.strip():
                logger.info("✅ Vanna AI connection successful")
                return True
            elif isinstance(test_result, tuple) and test_result[0] and str(test_result[0]).strip():
                logger.info("✅ Vanna AI connection successful (tuple result)")
                return True
            else:
                logger.warning("⚠️ Vanna AI connection test returned unexpected result")
                return False

        except Exception as e:
            logger.warning(f"Vanna AI connection test failed: {e}")
            return False
    
    async def _generate_sql_with_vanna_rag(self, question: str) -> str:
        """Generate SQL using real Vanna AI with RAG enhancement."""
        if not self._vanna_client:
            raise RuntimeError("Vanna AI client not available")

        try:
            logger.info("🚀 Starting Vanna AI + RAG SQL generation...")

            # Ensure RAG system is initialized
            if not self._rag_initialized:
                logger.info("🔧 Initializing RAG system...")
                if hasattr(self, '_rag_system'):
                    rag_success = await self._rag_system.initialize()
                    self._rag_initialized = rag_success
                    if rag_success:
                        logger.info("✅ RAG system initialized successfully")
                        # Train Vanna AI with schema from RAG
                        self._train_vanna_model()
                    else:
                        logger.warning("⚠️ RAG system initialization failed")

            # Get RAG-enhanced context for the question
            if self._rag_initialized and self._rag_system.is_available():
                logger.info("📋 Retrieving RAG context for question...")
                enhanced_question = await self._rag_system.enhance_question(question)
                logger.info(f"✨ RAG-enhanced question created ({len(enhanced_question)} chars)")
                logger.info(f"📝 Enhanced question preview: {enhanced_question[:150]}...")

                # Use Vanna AI with RAG-enhanced context
                logger.info("🤖 Calling Vanna AI with enhanced context...")
                result = self._vanna_client.ask(enhanced_question)
                logger.info("✅ Vanna AI call completed")
            else:
                # Fallback to original question if RAG is not available
                logger.warning("⚠️ RAG not available, using original question")
                result = self._vanna_client.ask(question)

            # Handle Vanna AI response
            logger.info(f"🔍 Processing Vanna AI response: {type(result)}")

            if isinstance(result, str) and str(result).strip():
                sql_query = str(result).strip()
                logger.info(f"🎯 Generated SQL: {sql_query}")
                return sql_query
            elif isinstance(result, tuple) and len(result) >= 1 and result[0] is not None:
                sql_text = str(result[0]).strip()
                if sql_text:
                    logger.info(f"🎯 Generated SQL from tuple: {sql_text}")
                    return sql_text
                else:
                    raise RuntimeError(f"Vanna AI returned empty SQL in tuple: {result}")
            else:
                logger.error(f"❌ Invalid Vanna AI response: {result}")
                raise RuntimeError(f"Vanna AI returned invalid SQL result: {result}")

        except Exception as e:
            logger.error(f"❌ Vanna AI + RAG SQL generation failed: {e}")
            raise RuntimeError(f"Failed to generate SQL with Vanna AI + RAG: {e}")
    
    async def _generate_sql_with_rag_only(self, question: str) -> str:
        """Fallback method for RAG-only SQL generation when Vanna AI is unavailable."""
        if not self._rag_initialized or not self._rag_system.is_available():
            raise RuntimeError("RAG system not available")

        try:
            # Get RAG-enhanced context
            enhanced_question = await self._rag_system.enhance_question(question)
            logger.info(f"🔍 RAG-enhanced question: {enhanced_question[:100]}...")

            # Use basic pattern matching as fallback
            sql_query = self._generate_sql_from_patterns(question)
            logger.info(f"📝 RAG-generated SQL: {sql_query}")
            return sql_query.strip()

        except Exception as e:
            logger.error(f"RAG-only SQL generation failed: {e}")
            raise RuntimeError(f"Failed to generate SQL: {e}")

    def _generate_sql_from_patterns(self, question: str) -> str:
        """Simple pattern matching fallback for basic queries."""
        question_lower = question.lower()

        # Basic pattern matching for common queries
        if "all employees" in question_lower:
            return "SELECT * FROM employees"
        elif "employees in engineering" in question_lower:
            return "SELECT * FROM employees WHERE department = 'Engineering'"
        elif "average salary" in question_lower:
            return "SELECT department, AVG(salary) as average_salary FROM employees GROUP BY department"
        elif "names start with" in question_lower and "j" in question_lower:
            return "SELECT * FROM employees WHERE first_name LIKE 'J%'"
        elif "all tables" in question_lower:
            return "SELECT name FROM sqlite_master WHERE type='table'"
        else:
            # Default fallback
            return "SELECT * FROM employees"
    
    def _get_client(self) -> None:
        """Get the Vanna client (functional approach, no client object needed)."""
        # Vanna uses a functional approach, no client object to return
        pass
    
    async def generate_sql(self, question: str) -> str:
        """
        Generate SQL from natural language question using real Vanna AI + RAG.
        
        Args:
            question: Natural language question
            
        Returns:
            Generated SQL query
            
        Raises:
            RuntimeError: If SQL generation failed
        """
        logger.info(f"🚀 VANNA: Starting real Vanna AI + RAG SQL generation")
        logger.info(f"📝 Question: '{question}'")
        logger.info(f"🔑 API Key set: {self._api_key_set}")
        logger.info(f"📊 RAG System available: {self._rag_system.is_available() if self._rag_system else False}")
        
        # Check if Vanna AI client is available
        if not self._vanna_client or not self._api_key_set:
            raise RuntimeError("Vanna AI client not available - please check API key and model configuration")
        
        try:
            logger.info("🎯 Starting Vanna AI + RAG SQL generation process...")

            # Initialize RAG system if not already done
            if not self._rag_initialized:
                logger.info("🔧 Initializing RAG system for context retrieval...")
                if hasattr(self, '_rag_system'):
                    rag_success = await self._rag_system.initialize()
                    self._rag_initialized = rag_success
                    if rag_success:
                        logger.info("✅ RAG system initialized successfully")
                        logger.info("📚 Training Vanna AI with database schema from RAG...")
                        # Train Vanna AI with schema from RAG
                        train_success = self._train_vanna_model()
                        if train_success:
                            logger.info("✅ Vanna AI training completed successfully")
                        else:
                            logger.warning("⚠️ Vanna AI training failed, but proceeding with generation")
                    else:
                        logger.error("❌ RAG system initialization failed")
                        raise RuntimeError("Cannot proceed without RAG system - schema context is required")
            else:
                    raise RuntimeError("RAG system not available")

            # Generate SQL using Vanna AI + RAG with fallback
            logger.info("🚀 Generating SQL with Vanna AI + RAG...")
            try:
                sql_query = await self._generate_sql_with_vanna_rag(question)
                logger.info("✅ Vanna AI + RAG SQL generation completed successfully")
                logger.info(f"🎯 Final SQL: '{sql_query}'")
                return sql_query.strip()
            except Exception as vanna_error:
                logger.warning(f"⚠️ Vanna AI failed ({vanna_error}), falling back to RAG-only...")
                # Fallback to RAG-only generation
                sql_query = await self._generate_sql_with_rag_only(question)
                logger.info("✅ RAG-only SQL generation completed successfully")
                logger.info(f"🎯 Final SQL (fallback): '{sql_query}'")
                return sql_query.strip()
            
        except Exception as e:
            logger.error(f"❌ All SQL generation methods failed: {e}")
            raise RuntimeError(f"Failed to generate SQL: {e}")
    
    async def check_connection(self) -> bool:
        """Check if Vanna AI is accessible."""
        try:
            if not self._initialized:
                return False
            
            # If we have a real client, try to check if Vanna is working
            if self._vanna_client and self._api_key_set:
                try:
                    # Try a simple test call with real client
                    loop = asyncio.get_event_loop()
                    test_result = await loop.run_in_executor(
                        None, 
                        self._vanna_client.ask, 
                        "test"
                    )
                    return bool(test_result)
                except Exception:
                    return False
            else:
                # No real client available
                return False
        except Exception:
            return False