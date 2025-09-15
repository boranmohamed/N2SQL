#!/usr/bin/env python3
"""
Integration script to ensure your system always uses REAL database schema.
This integrates with your existing RAG system and Vanna training.
"""
import os
import asyncio
from loguru import logger

# Set to use local Vanna
os.environ["USE_LOCAL_VANNA"] = "true"

from real_schema_extractor import RealSchemaExtractor
from app.infrastructure.vanna_factory import get_vanna_client_from_env

async def integrate_real_schema_system():
    """
    Integrate real schema extraction into your existing system.
    This ensures Qdrant always has the correct schema.
    """
    print("🔧 INTEGRATING REAL SCHEMA SYSTEM")
    print("=" * 60)
    
    try:
        # Step 1: Extract and store real schema
        print("📋 Step 1: Extracting and storing REAL database schema...")
        extractor = RealSchemaExtractor(db_path="vanna_app_clean.db")
        
        schema_success = await extractor.extract_and_store_real_schema()
        
        if not schema_success:
            print("❌ Failed to extract and store real schema")
            return False
        
        print("✅ Real schema extracted and stored successfully")
        
        # Step 2: Retrain Vanna with real schema
        print("\n🎓 Step 2: Retraining Vanna with real schema...")
        
        client = get_vanna_client_from_env()
        await client.initialize()
        
        # Get real schema for training
        real_schema = await extractor._extract_real_database_schema()
        
        # Generate correct DDL from real schema
        ddl_schema = generate_ddl_from_real_schema(real_schema)
        
        # Train with correct DDL
        ddl_success = await client.train_with_ddl(ddl_schema)
        
        if ddl_success:
            print("✅ DDL training completed with real schema")
        else:
            print("❌ DDL training failed")
            return False
        
        # Step 3: Train with corrected examples
        print("\n📝 Step 3: Training with corrected examples...")
        
        corrected_examples = get_corrected_training_examples(real_schema)
        
        for question, sql in corrected_examples:
            try:
                success = await client.train_with_sql(question, sql)
                if success:
                    print(f"✅ Trained: {question[:50]}...")
                else:
                    print(f"❌ Failed: {question[:50]}...")
            except Exception as e:
                print(f"❌ Training error for '{question}': {e}")
        
        # Step 4: Test the integration
        print("\n🧪 Step 4: Testing the integration...")
        
        test_success = await test_sql_generation_with_real_schema(client)
        
        if test_success:
            print("✅ Integration test passed!")
            return True
        else:
            print("❌ Integration test failed")
            return False
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_ddl_from_real_schema(real_schema):
    """Generate DDL from real schema."""
    ddl_parts = []
    
    for table_name, table_info in real_schema.items():
        ddl_parts.append(f"CREATE TABLE {table_name} (")
        
        column_defs = []
        for col in table_info.columns:
            col_def = f"    {col.name} {col.type}"
            if col.primary_key:
                col_def += " PRIMARY KEY"
            if col.not_null and not col.primary_key:
                col_def += " NOT NULL"
            if col.default_value:
                col_def += f" DEFAULT {col.default_value}"
            column_defs.append(col_def)
        
        ddl_parts.append(",\n".join(column_defs))
        ddl_parts.append(");")
        ddl_parts.append("")
    
    return "\n".join(ddl_parts)

def get_corrected_training_examples(real_schema):
    """Get corrected training examples based on real schema."""
    # Check if orders table has created_at or order_date
    orders_columns = [col.name for col in real_schema.get('orders', {}).columns] if 'orders' in real_schema else []
    
    # Use correct column name based on actual schema
    date_column = "created_at" if "created_at" in orders_columns else "order_date"
    
    examples = [
        ("Show me the complete customer journey: users, their orders, and sales", 
         f"""SELECT u.username, o.id as order_id, o.total_amount,
                   s.id as sale_id, s.amount as sale_amount,
                   e.first_name, e.last_name
            FROM users u
            LEFT JOIN sales s ON u.id = s.customer_id
            LEFT JOIN orders o ON u.username = o.customer_name
            LEFT JOIN employees e ON s.employee_id = e.id
            ORDER BY u.username, o.{date_column}, s.sale_date"""),
        
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
    
    return examples

async def test_sql_generation_with_real_schema(client):
    """Test SQL generation with real schema."""
    try:
        # Test the problematic question
        question = "Show me the complete customer journey: users, their orders, and sales"
        
        print(f"📝 Testing question: {question}")
        
        # Generate SQL
        sql = await client.generate_sql(question)
        print(f"🤖 Generated SQL:")
        print(sql)
        
        # Check if it uses correct column names
        if 'created_at' in sql and 'order_date' not in sql:
            print("✅ SUCCESS: SQL uses correct column names!")
            return True
        elif 'order_date' in sql and 'created_at' not in sql:
            print("⚠️ WARNING: SQL still uses 'order_date' instead of 'created_at'")
            print("This might be due to cached training data")
            return False
        else:
            print("ℹ️ INFO: SQL doesn't contain date columns")
            return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def create_schema_sync_script():
    """Create a script to sync schema regularly."""
    sync_script = '''#!/usr/bin/env python3
"""
Schema Sync Script - Run this regularly to ensure Qdrant has real schema.
Add this to your cron job or run it before important operations.
"""
import asyncio
from real_schema_extractor import RealSchemaExtractor

async def sync_schema():
    """Sync Qdrant with real database schema."""
    extractor = RealSchemaExtractor(db_path="vanna_app_clean.db")
    success = await extractor.extract_and_store_real_schema()
    
    if success:
        print("✅ Schema synced successfully")
    else:
        print("❌ Schema sync failed")

if __name__ == "__main__":
    asyncio.run(sync_schema())
'''
    
    with open("sync_schema.py", "w") as f:
        f.write(sync_script)
    
    print("📝 Created sync_schema.py for regular schema updates")

def main():
    """Main function."""
    print("🚀 REAL SCHEMA INTEGRATION")
    print("=" * 60)
    
    try:
        # Run integration
        success = asyncio.run(integrate_real_schema_system())
        
        if success:
            print("\n🎉 INTEGRATION COMPLETE!")
            print("✅ Real schema extracted and stored")
            print("✅ Vanna retrained with correct schema")
            print("✅ System now uses actual database structure")
            
            # Create sync script
            asyncio.run(create_schema_sync_script())
            
            print("\n📝 Next steps:")
            print("1. Test with web interface: python vanna_visual_tester.py")
            print("2. Ask: 'Show me the complete customer journey: users, their orders, and sales'")
            print("3. Run sync_schema.py regularly to keep Qdrant updated")
            print("4. Use verify_schema_match.py to check schema accuracy")
        else:
            print("\n❌ INTEGRATION FAILED!")
            print("Check the errors above and try again")
            
    except Exception as e:
        print(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main()
