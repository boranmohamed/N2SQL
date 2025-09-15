#!/usr/bin/env python3
"""
Analyze the customer journey question and provide correct SQL queries.
"""
import sqlite3
import pandas as pd

def analyze_customer_journey():
    """Analyze what the customer journey question should actually show."""
    print("🔍 CUSTOMER JOURNEY ANALYSIS")
    print("=" * 50)
    
    conn = sqlite3.connect("vanna_app_clean.db")
    conn.row_factory = sqlite3.Row
    
    print("\n📊 Current Data Structure:")
    print("-" * 30)
    
    # Show users
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    print(f"👥 USERS ({len(users_df)} records):")
    print(users_df.to_string(index=False))
    
    # Show orders  
    orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
    print(f"\n📦 ORDERS ({len(orders_df)} records):")
    print(orders_df.to_string(index=False))
    
    # Show sales
    sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
    print(f"\n💰 SALES ({len(sales_df)} records):")
    print(sales_df.to_string(index=False))
    
    print("\n🔍 RELATIONSHIP ANALYSIS:")
    print("-" * 30)
    
    # Check if usernames match customer_names
    print("❌ USERS.username vs ORDERS.customer_name:")
    print("   Users: john_doe, jane_smith, bob_wilson, alice_brown, charlie_davis")
    print("   Orders: Acme Corp, Tech Solutions, Global Industries, Startup Inc, Enterprise Ltd")
    print("   → NO MATCH! These are completely different customer systems")
    
    print("\n✅ USERS.id vs SALES.customer_id:")
    print("   Sales customer_id: 1, 2, 3, 4")
    print("   Users id: 1, 2, 3, 4, 5")
    print("   → MATCH! Sales link to individual users")
    
    print("\n🎯 WHAT THE QUESTION SHOULD ACTUALLY SHOW:")
    print("-" * 50)
    
    # Individual user journey (users + sales)
    print("1️⃣ INDIVIDUAL USER JOURNEY (Users + Sales):")
    individual_sql = """
    SELECT u.username, u.email,
           s.product_name, s.amount, s.sale_date,
           e.first_name || ' ' || e.last_name as sales_rep
    FROM users u
    LEFT JOIN sales s ON u.id = s.customer_id
    LEFT JOIN employees e ON s.employee_id = e.id
    ORDER BY u.username, s.sale_date
    """
    
    individual_df = pd.read_sql_query(individual_sql, conn)
    print(f"SQL: {individual_sql.strip()}")
    print(f"Results ({len(individual_df)} records):")
    print(individual_df.to_string(index=False))
    
    # Company customer journey (orders only)
    print("\n2️⃣ COMPANY CUSTOMER JOURNEY (Orders only):")
    company_sql = """
    SELECT customer_name, total_amount, status, created_at
    FROM orders
    ORDER BY created_at
    """
    
    company_df = pd.read_sql_query(company_sql, conn)
    print(f"SQL: {company_sql.strip()}")
    print(f"Results ({len(company_df)} records):")
    print(company_df.to_string(index=False))
    
    # Combined view (if we want to show both)
    print("\n3️⃣ COMBINED VIEW (Both systems):")
    combined_sql = """
    SELECT 'Individual User' as customer_type, u.username as customer_name, 
           s.amount as total_amount, s.sale_date as transaction_date,
           'sale' as transaction_type
    FROM users u
    LEFT JOIN sales s ON u.id = s.customer_id
    WHERE s.id IS NOT NULL
    
    UNION ALL
    
    SELECT 'Company Customer' as customer_type, o.customer_name, 
           o.total_amount, o.created_at as transaction_date,
           'order' as transaction_type
    FROM orders o
    
    ORDER BY transaction_date
    """
    
    combined_df = pd.read_sql_query(combined_sql, conn)
    print(f"SQL: {combined_sql.strip()}")
    print(f"Results ({len(combined_df)} records):")
    print(combined_df.to_string(index=False))
    
    conn.close()
    
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 20)
    print("1. The question 'Show me the complete customer journey' is ambiguous")
    print("2. You have TWO separate customer systems:")
    print("   - Individual users (users + sales)")
    print("   - Company customers (orders)")
    print("3. Ask more specific questions:")
    print("   - 'Show me individual user purchases'")
    print("   - 'Show me company orders'")
    print("   - 'Show me sales by user'")
    print("   - 'Show me all transactions (both users and companies)'")

if __name__ == "__main__":
    analyze_customer_journey()
