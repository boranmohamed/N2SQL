#!/usr/bin/env python3
"""
Train Local Vanna with RAG context from Docker Qdrant.
"""
import os
import sys
import asyncio
from datetime import datetime

# Set environment to use local Vanna
os.environ["USE_LOCAL_VANNA"] = "true"

async def train_with_rag():
    """Train local Vanna with RAG context."""
    print("🚀 Training Local Vanna with RAG Context")
    print("=" * 50)
    
    try:
        # Import the local Vanna client
        from app.infrastructure.local_vanna_client import LocalVannaClientRepository
        
        # Create client
        client = LocalVannaClientRepository()
        
        # Initialize client (this will also initialize RAG)
        print("🔧 Initializing client with RAG system...")
        success = await client.initialize()
        
        if not success:
            print("❌ Client initialization failed")
            return False
        
        print("✅ Client initialized successfully with RAG context")
        
        # Test RAG context retrieval
        print("\n🧪 Testing RAG context retrieval...")
        try:
            # This will use the RAG system to get schema context
            rag_context = await client._rag_system.retrieve_relevant_context("Calculate customer lifetime value")
            print(f"✅ RAG context retrieved: {len(rag_context)} items")
            for i, context in enumerate(rag_context[:2]):  # Show first 2 items
                print(f"   Context {i+1}: {context[:100]}...")
        except Exception as e:
            print(f"⚠️ RAG context test failed: {e}")
        
        # Train with DDL schema
        print("\n📚 Training with database schema...")
        try:
            ddl_schema = """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                department TEXT,
                salary REAL,
                hire_date DATE
            );
            
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                amount REAL,
                sale_date DATETIME,
                employee_id INTEGER,
                FOREIGN KEY (customer_id) REFERENCES users(id),
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );
            
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer_name TEXT,
                total_amount REAL,
                order_date DATETIME,
                status TEXT DEFAULT 'pending'
            );
            """
            
            success = await client.train_with_ddl(ddl_schema)
            if success:
                print("✅ DDL training completed successfully")
            else:
                print("❌ DDL training failed")
                
        except Exception as e:
            print(f"❌ DDL training error: {e}")
        
        # Train with specific examples
        print("\n📝 Training with specific examples...")
        examples = [
            ("Calculate customer lifetime value from sales", 
             "SELECT u.username, SUM(s.amount) as lifetime_value FROM users u JOIN sales s ON u.id = s.customer_id GROUP BY u.id, u.username ORDER BY lifetime_value DESC"),
            
            ("Show me all employees in Engineering department", 
             "SELECT * FROM employees WHERE department = 'Engineering'"),
            
            ("What is the total sales amount?", 
             "SELECT SUM(amount) as total_sales FROM sales"),
            
            ("Find pending orders", 
             "SELECT * FROM orders WHERE status = 'pending'"),
            
            ("Show employees with high salary", 
             "SELECT * FROM employees WHERE salary > 70000 ORDER BY salary DESC")
        ]
        
        for question, sql in examples:
            try:
                success = await client.train_with_sql(question, sql)
                if success:
                    print(f"✅ Trained: {question[:50]}...")
                else:
                    print(f"❌ Failed: {question[:50]}...")
            except Exception as e:
                print(f"❌ Training error for '{question}': {e}")
        
        # Test SQL generation
        print("\n🧪 Testing SQL generation...")
        test_questions = [
            "Calculate customer lifetime value",
            "Show me all employees",
            "What is the total sales amount?",
            "Find pending orders"
        ]
        
        for question in test_questions:
            try:
                sql = await client.generate_sql(question)
                print(f"✅ Question: {question}")
                print(f"   SQL: {sql}")
                print()
            except Exception as e:
                print(f"❌ Failed to generate SQL for '{question}': {e}")
        
        print("🎉 Training with RAG context completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

def main():
    """Main function."""
    try:
        # Run async training
        success = asyncio.run(train_with_rag())
        
        if success:
            print("\n✅ All training completed successfully!")
            print("\n📝 Next steps:")
            print("1. Test in web interface: http://localhost:5000")
            print("2. Ask questions like 'Calculate customer lifetime value'")
            print("3. The RAG system will provide context-aware SQL generation")
        else:
            print("\n❌ Training failed - check the errors above")
            
    except Exception as e:
        print(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main()
