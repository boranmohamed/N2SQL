#!/usr/bin/env python3
"""
Test script to demonstrate the SQL generation issue and verify the fix.
"""
import os
import asyncio
import sqlite3
import pandas as pd

# Set to use local Vanna
os.environ["USE_LOCAL_VANNA"] = "true"

from app.infrastructure.vanna_factory import get_vanna_client_from_env

async def test_current_issue():
    """Test the current SQL generation issue."""
    print("🔍 Testing Current SQL Generation Issue")
    print("=" * 50)
    
    try:
        # Initialize Vanna client
        client = get_vanna_client_from_env()
        await client.initialize()
        
        # Test question that causes the issue
        question = "Show me the complete customer journey: users, their orders, and sales"
        
        print(f"📝 Question: {question}")
        print("\n🤖 Generated SQL:")
        
        # Generate SQL
        sql = await client.generate_sql(question)
        print(sql)
        
        print("\n🧪 Testing SQL Execution:")
        
        # Try to execute the generated SQL
        try:
            conn = sqlite3.connect("vanna_app_clean.db")
            conn.row_factory = sqlite3.Row
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            print("✅ SQL executed successfully!")
            print(f"✅ Returned {len(df)} rows")
            if len(df) > 0:
                print(f"✅ Sample data: {df.iloc[0].to_dict()}")
                
        except Exception as e:
            print(f"❌ SQL execution failed: {e}")
            print("\n🔧 This is the issue we need to fix!")
            
            # Show the corrected SQL
            print("\n✅ Here's the corrected SQL that would work:")
            corrected_sql = """SELECT u.username, o.id as order_id, o.total_amount,
                                      s.id as sale_id, s.amount as sale_amount,
                                      e.first_name, e.last_name
                               FROM users u
                               LEFT JOIN sales s ON u.id = s.customer_id
                               LEFT JOIN orders o ON u.username = o.customer_name
                               LEFT JOIN employees e ON s.employee_id = e.id
                               ORDER BY u.username, o.created_at, s.sale_date"""
            
            print(corrected_sql)
            
            # Test the corrected SQL
            print("\n🧪 Testing corrected SQL:")
            try:
                conn = sqlite3.connect("vanna_app_clean.db")
                conn.row_factory = sqlite3.Row
                df = pd.read_sql_query(corrected_sql, conn)
                conn.close()
                
                print("✅ Corrected SQL executed successfully!")
                print(f"✅ Returned {len(df)} rows")
                if len(df) > 0:
                    print(f"✅ Sample data: {df.iloc[0].to_dict()}")
                    
            except Exception as e2:
                print(f"❌ Even corrected SQL failed: {e2}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def show_database_schema():
    """Show the actual database schema."""
    print("\n📋 Actual Database Schema")
    print("=" * 30)
    
    try:
        conn = sqlite3.connect("vanna_app_clean.db")
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            if table_name.startswith('sqlite_'):
                continue
                
            print(f"\n📊 Table: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                pk_str = " (PRIMARY KEY)" if pk else ""
                nn_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"   {col_name} ({col_type}){pk_str}{nn_str}{default_str}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Failed to show schema: {e}")

def main():
    """Main function."""
    print("🔍 SQL Generation Issue Analysis")
    print("=" * 50)
    
    # Show actual database schema
    show_database_schema()
    
    # Test the current issue
    asyncio.run(test_current_issue())
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print("❌ ISSUE: Vanna generates 'o.order_date' but database has 'o.created_at'")
    print("🔧 CAUSE: Training data uses wrong column names")
    print("✅ SOLUTION: Run fix_schema_mismatch.py to retrain with correct schema")

if __name__ == "__main__":
    main()
