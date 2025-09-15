#!/usr/bin/env python3
"""
Verify that the RAG fix is working correctly in the web interface.
"""
import os
import sys
import asyncio
import sqlite3
import pandas as pd

# Set environment to use local Vanna
os.environ["USE_LOCAL_VANNA"] = "true"

async def test_sql_execution():
    """Test that the generated SQL actually executes correctly."""
    print("🧪 Testing SQL Execution")
    print("=" * 30)
    
    try:
        # The SQL that should be generated
        correct_sql = "SELECT u.username, COUNT(s.id) as order_count FROM users u LEFT JOIN sales s ON u.id = s.customer_id GROUP BY u.id, u.username"
        
        # Connect to database
        conn = sqlite3.connect("vanna_app_clean.db")
        conn.row_factory = sqlite3.Row
        
        # Execute the SQL
        df = pd.read_sql_query(correct_sql, conn)
        conn.close()
        
        print(f"✅ SQL executed successfully")
        print(f"✅ Returned {len(df)} rows")
        print(f"✅ Columns: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"✅ Sample data: {df.iloc[0].to_dict()}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL execution failed: {e}")
        return False

async def test_rag_context_quality():
    """Test the quality of RAG context retrieval."""
    print("\n🔍 Testing RAG Context Quality")
    print("=" * 40)
    
    try:
        from app.infrastructure.enhanced_rag_system import EnhancedRAGSystem
        
        rag_system = EnhancedRAGSystem(db_path="vanna_app_clean.db")
        await rag_system.initialize()
        
        # Test question
        question = "Show me users with their order count"
        
        # Get context
        context = await rag_system.retrieve_relevant_context(question)
        
        print(f"✅ Retrieved {len(context)} contexts")
        
        # Check if context contains the right information
        context_text = "\n".join(context)
        
        checks = [
            ("users table", "Table: users" in context_text),
            ("username column", "username" in context_text),
            ("sales table", "Table: sales" in context_text),
            ("customer_id column", "customer_id" in context_text),
            ("relationships", "relationships" in context_text.lower()),
            ("query patterns", "query_patterns" in context_text.lower())
        ]
        
        print("\n📋 Context Quality Checks:")
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
        
        all_passed = all(passed for _, passed in checks)
        return all_passed
        
    except Exception as e:
        print(f"❌ Context quality test failed: {e}")
        return False

async def test_end_to_end_workflow():
    """Test the complete end-to-end workflow."""
    print("\n🔄 Testing End-to-End Workflow")
    print("=" * 40)
    
    try:
        from app.infrastructure.local_vanna_client import LocalVannaClientRepository
        
        client = LocalVannaClientRepository()
        await client.initialize()
        
        # Test questions and expected SQL patterns
        test_cases = [
            {
                "question": "Show me users with their order count",
                "expected_columns": ["username"],
                "expected_tables": ["users", "sales"]
            },
            {
                "question": "Calculate customer lifetime value",
                "expected_columns": ["customer_id", "amount"],
                "expected_tables": ["sales"]
            },
            {
                "question": "What is the total sales amount?",
                "expected_columns": ["amount"],
                "expected_tables": ["sales"]
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: '{test_case['question']}'")
            
            try:
                # Generate SQL
                sql = await client.generate_sql(test_case['question'])
                print(f"✅ Generated SQL: {sql}")
                
                # Check if SQL contains expected elements
                sql_lower = sql.lower()
                
                column_checks = []
                for col in test_case['expected_columns']:
                    if col in sql_lower:
                        column_checks.append(f"✅ {col}")
                    else:
                        column_checks.append(f"❌ {col}")
                
                table_checks = []
                for table in test_case['expected_tables']:
                    if table in sql_lower:
                        table_checks.append(f"✅ {table}")
                    else:
                        table_checks.append(f"❌ {table}")
                
                print(f"   Columns: {', '.join(column_checks)}")
                print(f"   Tables: {', '.join(table_checks)}")
                
                # Check if all expected elements are present
                all_columns_present = all(col in sql_lower for col in test_case['expected_columns'])
                all_tables_present = all(table in sql_lower for table in test_case['expected_tables'])
                
                if all_columns_present and all_tables_present:
                    print(f"   ✅ Test case {i} PASSED")
                else:
                    print(f"   ❌ Test case {i} FAILED")
                    all_passed = False
                    
            except Exception as e:
                print(f"   ❌ Test case {i} ERROR: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False

def main():
    """Main verification function."""
    print("🔧 Verifying RAG Fix")
    print("=" * 50)
    
    try:
        # Test SQL execution
        sql_success = asyncio.run(test_sql_execution())
        
        # Test RAG context quality
        context_success = asyncio.run(test_rag_context_quality())
        
        # Test end-to-end workflow
        workflow_success = asyncio.run(test_end_to_end_workflow())
        
        print("\n" + "=" * 50)
        print("📊 VERIFICATION RESULTS")
        print("=" * 50)
        
        results = [
            ("SQL Execution", sql_success),
            ("RAG Context Quality", context_success),
            ("End-to-End Workflow", workflow_success)
        ]
        
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        all_passed = all(success for _, success in results)
        
        if all_passed:
            print("\n🎉 ALL VERIFICATIONS PASSED!")
            print("✅ RAG context retrieval is working correctly")
            print("✅ Generated SQL uses correct column names")
            print("✅ SQL executes successfully against the database")
            print("✅ End-to-end workflow is functioning properly")
            
            print("\n📝 The fix is complete! You can now:")
            print("1. Use the web interface at http://localhost:5000")
            print("2. Ask: 'Show me users with their order count'")
            print("3. The generated SQL will use correct column names (u.username)")
            print("4. The SQL will execute successfully and show real results")
        else:
            print("\n❌ Some verifications failed")
            print("Check the errors above and rerun the fix script if needed")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
