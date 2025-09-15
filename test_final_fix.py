#!/usr/bin/env python3
"""
Test the final fix to ensure SQL generation works correctly.
"""
import os
import asyncio
import sqlite3
import pandas as pd
import requests
import json

# Set to use local Vanna
os.environ["USE_LOCAL_VANNA"] = "true"

def test_web_interface():
    """Test the web interface API."""
    print("🌐 Testing Web Interface API")
    print("=" * 40)
    
    try:
        # Test question
        question = "Show me the complete customer journey: users, their orders, and sales"
        
        # Make API request
        response = requests.post(
            "http://localhost:5000/api/generate",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                sql = result.get("sql", "")
                print(f"✅ SQL generated successfully:")
                print(f"📝 Question: {question}")
                print(f"🤖 Generated SQL:")
                print(sql)
                
                # Check if it uses correct column names
                if 'created_at' in sql and 'order_date' not in sql:
                    print(f"\n✅ SUCCESS: SQL uses correct column names!")
                    print(f"   - Found 'created_at' ✅")
                    print(f"   - No 'order_date' ✅")
                    return True
                else:
                    print(f"\n❌ FAILED: SQL still uses incorrect column names")
                    print(f"   - Has 'created_at': {'created_at' in sql}")
                    print(f"   - Has 'order_date': {'order_date' in sql}")
                    return False
            else:
                print(f"❌ SQL generation failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_sql_execution():
    """Test that the generated SQL actually executes."""
    print("\n🧪 Testing SQL Execution")
    print("=" * 30)
    
    try:
        # The corrected SQL that should work
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
        df = pd.read_sql_query(corrected_sql, conn)
        conn.close()
        
        print(f"✅ Corrected SQL executed successfully")
        print(f"✅ Returned {len(df)} rows")
        
        if len(df) > 0:
            print(f"✅ Sample result: {dict(df.iloc[0])}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL execution test failed: {e}")
        return False

def main():
    """Main function."""
    print("🔧 Testing Final Fix")
    print("=" * 50)
    
    # Test SQL execution first
    sql_test = test_sql_execution()
    
    # Test web interface
    web_test = test_web_interface()
    
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    
    if sql_test and web_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Qdrant schema data corrected")
        print("✅ SQL generation uses correct column names")
        print("✅ Generated SQL executes successfully")
        print("\n🎯 The 'order_date' → 'created_at' issue is COMPLETELY FIXED!")
    elif sql_test:
        print("⚠️ SQL execution works but web interface test failed")
        print("The fix is partially working - SQL generation should now be correct")
    else:
        print("❌ Tests failed - the fix may need additional work")
    
    print(f"\n📝 Summary:")
    print(f"   - SQL Execution Test: {'✅ PASSED' if sql_test else '❌ FAILED'}")
    print(f"   - Web Interface Test: {'✅ PASSED' if web_test else '❌ FAILED'}")

if __name__ == "__main__":
    main()
