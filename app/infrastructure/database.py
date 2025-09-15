"""
Database infrastructure and repository implementation.
"""
import time
import sqlite3
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..domain.repositories import DatabaseRepository
from .config import settings


class DatabaseManager:
    """Manages database connections and provides repository instances."""
    
    def __init__(self) -> None:
        """Initialize the database manager."""
        self._initialized = False
        self._db_path = self._get_db_path()
    
    def _get_db_path(self) -> str:
        """Get the database file path."""
        db_url = str(settings.database_url)
        if db_url.startswith("sqlite:///"):
            return db_url.replace("sqlite:///", "")
        elif db_url.startswith("sqlite://"):
            return db_url.replace("sqlite://", "")
        else:
            return "vanna_app_clean.db"
    
    async def initialize_database(self) -> None:
        """Initialize the database with tables and sample data."""
        from loguru import logger
        import os
        
        if self._initialized:
            return
            
        try:
            logger.info(f"🗄️  DATABASE: Starting initialization")
            logger.info(f"   📁 Database path: {self._db_path}")
            
            # Force delete any existing corrupted database
            if os.path.exists(self._db_path):
                logger.info(f"   🗑️  Removing existing database file")
                os.remove(self._db_path)
                logger.info(f"   ✅ Existing database file removed")
            
            # Create tables first
            logger.info(f"   📋 Step 1: Creating database tables")
            self._create_tables()
            logger.info(f"   ✅ Tables created successfully")
            
            # Insert sample data
            logger.info(f"   📊 Step 2: Inserting sample data")
            self._insert_sample_data()
            logger.info(f"   ✅ Sample data inserted successfully")
            
            self._initialized = True
            logger.info(f"   🎉 Database initialization completed successfully")
            
            # Test the database
            logger.info(f"   🧪 Testing database functionality...")
            self._test_database()
            logger.info(f"   ✅ Database test passed")
            
        except Exception as e:
            logger.error(f"   ❌ Database initialization failed: {e}")
            logger.error(f"   📋 Error type: {type(e).__name__}")
            raise
    
    def _test_database(self) -> None:
        """Test basic database functionality."""
        from loguru import logger
        
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            logger.info(f"      👥 Users table has {user_count} records")
            
            cursor.execute("SELECT COUNT(*) FROM employees")
            emp_count = cursor.fetchone()[0]
            logger.info(f"      👷 Employees table has {emp_count} records")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"      ❌ Database test failed: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create database tables using native sqlite3."""
        from loguru import logger
        
        logger.info(f"      🚀 Creating tables...")
        
        # Create each table individually
        tables = [
            ("users", """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """),
            ("employees", """
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    department TEXT,
                    salary REAL,
                    hire_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ("sales", """
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    sale_date TEXT NOT NULL,
                    customer_id INTEGER,
                    employee_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ("orders", """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        ]
        
        # Connect and create tables
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        try:
            for table_name, create_sql in tables:
                logger.info(f"      📋 Creating table: {table_name}")
                cursor.execute(create_sql)
                logger.info(f"      ✅ Table {table_name} created successfully")
            
            conn.commit()
            logger.info(f"      🎉 All tables created successfully")
            
        finally:
            cursor.close()
            conn.close()
    
    def _insert_sample_data(self) -> None:
        """Insert sample data into tables."""
        from loguru import logger
        
        logger.info(f"      📊 Inserting sample data...")
        
        # Connect and insert data
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        try:
            # Insert sample users
            logger.info(f"         👥 Inserting 5 sample users")
            cursor.execute("""
                INSERT INTO users (username, email) VALUES
                ('john_doe', 'john.doe@example.com'),
                ('jane_smith', 'jane.smith@example.com'),
                ('bob_wilson', 'bob.wilson@example.com'),
                ('alice_brown', 'alice.brown@example.com'),
                ('charlie_davis', 'charlie.davis@example.com')
            """)
            
            # Insert sample employees
            logger.info(f"         👷 Inserting 5 sample employees")
            cursor.execute("""
                INSERT INTO employees (first_name, last_name, email, department, salary, hire_date) VALUES
                ('John', 'Doe', 'john.doe@company.com', 'Engineering', 75000.00, '2022-02-15'),
                ('Jane', 'Smith', 'jane.smith@company.com', 'Marketing', 65000.00, '2022-03-20'),
                ('Bob', 'Wilson', 'bob.wilson@company.com', 'Sales', 70000.00, '2021-12-10'),
                ('Alice', 'Brown', 'alice.brown@company.com', 'Engineering', 80000.00, '2021-09-05'),
                ('Charlie', 'Davis', 'charlie.davis@company.com', 'HR', 60000.00, '2022-04-01')
            """)
            
            # Insert sample sales
            logger.info(f"         💰 Inserting 5 sample sales")
            cursor.execute("""
                INSERT INTO sales (product_name, amount, sale_date, customer_id, employee_id) VALUES
                ('Laptop', 1200.00, '2024-01-15', 1, 3),
                ('Mouse', 25.00, '2024-01-16', 2, 3),
                ('Keyboard', 80.00, '2024-01-17', 3, 3),
                ('Monitor', 300.00, '2024-01-18', 1, 3),
                ('Headphones', 150.00, '2024-01-19', 4, 3)
            """)
            
            # Insert sample orders
            logger.info(f"         📦 Inserting 5 sample orders")
            cursor.execute("""
                INSERT INTO orders (customer_name, total_amount, status) VALUES
                ('Acme Corp', 1500.00, 'completed'),
                ('Tech Solutions', 800.00, 'processing'),
                ('Global Industries', 2200.00, 'pending'),
                ('Startup Inc', 450.00, 'completed'),
                ('Enterprise Ltd', 3200.00, 'processing')
            """)
            
            conn.commit()
            logger.info(f"      ✅ Sample data inserted successfully")
            
        finally:
            cursor.close()
            conn.close()
    
    async def check_connection(self) -> bool:
        """Check if the database is accessible."""
        try:
            # Initialize database if not already done
            if not self._initialized:
                await self.initialize_database()
                
            # Test connection with native SQLite
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True
        except Exception:
            return False


class SQLiteDatabaseRepository(DatabaseRepository):
    """SQLite implementation of the database repository."""
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize the repository with a database manager."""
        self.db_manager = db_manager
    
    async def execute_query(self, sql: str) -> tuple[List[Dict[str, Any]], float]:
        """
        Execute a SQL query and return results with execution time.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Tuple of (results, execution_time_ms)
            
        Raises:
            Exception: If query execution fails
        """
        from loguru import logger
        
        logger.info(f"🗄️  DATABASE: Executing SQL query")
        logger.info(f"   🎯 SQL: '{sql}'")
        
        start_time = time.time()
        
        try:
            # Use native SQLite for query execution
            conn = sqlite3.connect(self.db_manager._db_path)
            cursor = conn.cursor()
            
            logger.info(f"   🔌 Database connection established")
            
            cursor.execute(sql)
            logger.info(f"   ✅ SQL executed successfully")
            
            # Get column names from cursor description
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
            else:
                columns = []
            
            # Fetch all results
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"   📊 Query results:")
            logger.info(f"      📋 Columns: {columns}")
            logger.info(f"      📈 Row count: {len(results)}")
            logger.info(f"      ⏱️  Execution time: {execution_time:.2f}ms")
            
            if results:
                logger.info(f"      📝 Sample result: {results[0] if len(results) > 0 else 'No results'}")
            
            cursor.close()
            conn.close()
            
            return results, execution_time
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"   ❌ Database query failed: {e}")
            logger.error(f"   📋 Error type: {type(e).__name__}")
            logger.error(f"   ⏱️  Failed after: {execution_time:.2f}ms")
            raise Exception(f"Query execution failed: {str(e)}") from e
    
    async def check_connection(self) -> bool:
        """Check if the database is accessible."""
        return await self.db_manager.check_connection()


# Global database manager instance
db_manager = DatabaseManager()
