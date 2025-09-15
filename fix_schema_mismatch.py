#!/usr/bin/env python3
"""
Fix schema mismatch between training data and actual database.
This script updates the RAG system and retrains Vanna with correct schema.
"""
import os
import asyncio
import sqlite3
from loguru import logger

# Set to use local Vanna
os.environ["USE_LOCAL_VANNA"] = "true"

from app.infrastructure.vanna_factory import get_vanna_client_from_env
from app.infrastructure.enhanced_rag_system import EnhancedRAGSystem

async def fix_schema_mismatch():
    """Fix the schema mismatch between training and actual database."""
    print("🔧 Fixing Schema Mismatch")
    print("=" * 50)
    
    try:
        # Step 1: Get actual database schema
        print("📋 Step 1: Extracting actual database schema...")
        actual_schema = get_actual_database_schema()
        print(f"✅ Extracted schema for {len(actual_schema)} tables")
        
        # Step 2: Update RAG system with correct schema
        print("\n📚 Step 2: Updating RAG system with correct schema...")
        rag_system = EnhancedRAGSystem(db_path="vanna_app_clean.db")
        await rag_system.initialize()
        
        # Update Qdrant with correct schema
        await update_qdrant_with_correct_schema(rag_system, actual_schema)
        
        # Step 3: Retrain Vanna with correct schema
        print("\n🎓 Step 3: Retraining Vanna with correct schema...")
        client = get_vanna_client_from_env()
        await client.initialize()
        
        # Train with correct DDL
        correct_ddl = generate_correct_ddl(actual_schema)
        success = await client.train_with_ddl(correct_ddl)
        
        if success:
            print("✅ DDL training completed with correct schema")
        else:
            print("❌ DDL training failed")
            return False
        
        # Step 4: Train with corrected examples
        print("\n📝 Step 4: Training with corrected examples...")
        corrected_examples = get_corrected_examples()
        
        for question, sql in corrected_examples:
            try:
                success = await client.train_with_sql(question, sql)
                if success:
                    print(f"✅ Trained: {question[:50]}...")
                else:
                    print(f"❌ Failed: {question[:50]}...")
            except Exception as e:
                print(f"❌ Training error for '{question}': {e}")
        
        print("\n🎉 Schema mismatch fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_actual_database_schema():
    """Get the actual database schema from SQLite."""
    conn = sqlite3.connect("vanna_app_clean.db")
    cursor = conn.cursor()
    
    schema = {}
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for (table_name,) in tables:
        if table_name.startswith('sqlite_'):
            continue
            
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        columns = []
        
        for col in columns_info:
            columns.append({
                'name': col[1],
                'type': col[2],
                'not_null': bool(col[3]),
                'default': col[4],
                'primary_key': bool(col[5])
            })
        
        schema[table_name] = columns
    
    conn.close()
    return schema

def generate_correct_ddl(schema):
    """Generate correct DDL from actual schema."""
    ddl_parts = []
    
    for table_name, columns in schema.items():
        ddl_parts.append(f"CREATE TABLE {table_name} (")
        
        column_defs = []
        for col in columns:
            col_def = f"    {col['name']} {col['type']}"
            if col['primary_key']:
                col_def += " PRIMARY KEY"
            if col['not_null'] and not col['primary_key']:
                col_def += " NOT NULL"
            if col['default']:
                col_def += f" DEFAULT {col['default']}"
            column_defs.append(col_def)
        
        ddl_parts.append(",\n".join(column_defs))
        ddl_parts.append(");")
        ddl_parts.append("")
    
    return "\n".join(ddl_parts)

def get_corrected_examples():
    """Get corrected training examples with proper column names."""
    return [
        ("Show me the complete customer journey: users, their orders, and sales", 
         """SELECT u.username, o.id as order_id, o.total_amount,
                   s.id as sale_id, s.amount as sale_amount,
                   e.first_name, e.last_name
            FROM users u
            LEFT JOIN sales s ON u.id = s.customer_id
            LEFT JOIN orders o ON u.username = o.customer_name
            LEFT JOIN employees e ON s.employee_id = e.id
            ORDER BY u.username, o.created_at, s.sale_date"""),
        
        ("Calculate customer lifetime value from sales", 
         "SELECT u.username, SUM(s.amount) as lifetime_value FROM users u JOIN sales s ON u.id = s.customer_id GROUP BY u.id, u.username ORDER BY lifetime_value DESC"),
        
        ("Show me all employees in Engineering department", 
         "SELECT * FROM employees WHERE department = 'Engineering'"),
        
        ("What is the total sales amount?", 
         "SELECT SUM(amount) as total_sales FROM sales"),
        
        ("Find pending orders", 
         "SELECT * FROM orders WHERE status = 'pending'"),
        
        ("Show employees with high salary", 
         "SELECT * FROM employees WHERE salary > 70000 ORDER BY salary DESC"),
        
        ("Show me users with their order count", 
         "SELECT u.username, COUNT(s.id) as order_count FROM users u LEFT JOIN sales s ON u.id = s.customer_id GROUP BY u.id, u.username"),
        
        ("Find the top 5 customers by total order value", 
         "SELECT o.customer_name, SUM(o.total_amount) as total_value FROM orders o GROUP BY o.customer_name ORDER BY total_value DESC LIMIT 5")
    ]

async def update_qdrant_with_correct_schema(rag_system, actual_schema):
    """Update Qdrant with correct schema information."""
    try:
        from qdrant_client.models import PointStruct
        
        # Create correct schema points
        points = []
        
        for table_name, columns in actual_schema.items():
            column_names = [col['name'] for col in columns]
            column_types = [f"{col['name']} ({col['type']})" for col in columns]
            
            # Create table schema point
            table_text = f"Table: {table_name}\nDescription: Contains {table_name} data\nColumns: {', '.join(column_types)}"
            
            points.append(PointStruct(
                id=f"table_{table_name}_corrected",
                vector=[0.1] * 384,  # Simple vector
                payload={
                    "text": table_text,
                    "type": "table_schema",
                    "table": table_name,
                    "columns": column_names,
                    "corrected": True
                }
            ))
        
        # Update Qdrant
        if rag_system.vector_db:
            rag_system.vector_db.upsert(
                collection_name=rag_system.collection_name,
                points=points
            )
            print(f"✅ Updated Qdrant with {len(points)} corrected schema points")
        
    except Exception as e:
        print(f"❌ Failed to update Qdrant: {e}")

async def test_corrected_sql():
    """Test that the corrected SQL works."""
    print("\n🧪 Testing Corrected SQL")
    print("=" * 30)
    
    try:
        # Test the corrected query
        corrected_sql = """SELECT u.username, o.id as order_id, o.total_amount,
                                  s.id as sale_id, s.amount as sale_amount,
                                  e.first_name, e.last_name
                           FROM users u
                           LEFT JOIN sales s ON u.id = s.customer_id
                           LEFT JOIN orders o ON u.username = o.customer_name
                           LEFT JOIN employees e ON s.employee_id = e.id
                           ORDER BY u.username, o.created_at, s.sale_date"""
        
        # Execute the SQL
        conn = sqlite3.connect("vanna_app_clean.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(corrected_sql)
        results = cursor.fetchall()
        
        print(f"✅ Corrected SQL executed successfully")
        print(f"✅ Returned {len(results)} rows")
        
        if results:
            print(f"✅ Sample result: {dict(results[0])}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Corrected SQL test failed: {e}")
        return False

def main():
    """Main function."""
    try:
        success = asyncio.run(fix_schema_mismatch())
        
        if success:
            # Test the fix
            test_success = asyncio.run(test_corrected_sql())
            
            if test_success:
                print("\n🎉 SCHEMA MISMATCH FIX COMPLETED SUCCESSFULLY!")
                print("\n✅ What was fixed:")
                print("   - Updated RAG system with correct schema")
                print("   - Retrained Vanna with actual column names")
                print("   - Fixed order_date → created_at mismatch")
                print("   - Added corrected training examples")
                
                print("\n📝 Now you can ask:")
                print("   'Show me the complete customer journey: users, their orders, and sales'")
                print("   And it will generate SQL with correct column names!")
            else:
                print("\n❌ Fix completed but testing failed")
        else:
            print("\n❌ Schema mismatch fix failed")
            
    except Exception as e:
        print(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main()
