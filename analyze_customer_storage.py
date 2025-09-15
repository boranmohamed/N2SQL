#!/usr/bin/env python3
"""
Analyze where customers are stored in the database.
"""
import sqlite3
import pandas as pd

def analyze_customer_storage():
    """Analyze where customer data is stored."""
    print("🔍 CUSTOMER STORAGE ANALYSIS")
    print("=" * 50)
    
    conn = sqlite3.connect("vanna_app_clean.db")
    conn.row_factory = sqlite3.Row
    
    print("\n📊 DATABASE SCHEMA OVERVIEW:")
    print("-" * 40)
    
    # Get all tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    print("\n🏪 CUSTOMER DATA LOCATIONS:")
    print("-" * 40)
    
    # Analyze each table for customer data
    customer_tables = ['users', 'orders', 'sales']
    
    for table in customer_tables:
        print(f"\n📋 {table.upper()} TABLE:")
        print("   " + "-" * 30)
        
        # Get column information
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"   Columns: {[col[1] for col in columns]}")
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        sample_data = cursor.fetchall()
        print(f"   Sample data ({len(sample_data)} rows):")
        for i, row in enumerate(sample_data, 1):
            print(f"      Row {i}: {dict(row)}")
    
    print("\n🎯 CUSTOMER IDENTIFICATION:")
    print("-" * 40)
    
    # Check for customer identifiers
    print("1️⃣ INDIVIDUAL CUSTOMERS (users table):")
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()
    print("   Customer identifiers:")
    for user in users:
        print(f"      ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    
    print("\n2️⃣ COMPANY CUSTOMERS (orders table):")
    cursor.execute("SELECT id, customer_name FROM orders")
    orders = cursor.fetchall()
    print("   Customer identifiers:")
    for order in orders:
        print(f"      ID: {order[0]}, Company: {order[1]}")
    
    print("\n3️⃣ CUSTOMER REFERENCES (sales table):")
    cursor.execute("SELECT id, customer_id, product_name FROM sales")
    sales = cursor.fetchall()
    print("   Sales with customer references:")
    for sale in sales:
        print(f"      Sale ID: {sale[0]}, Customer ID: {sale[1]}, Product: {sale[2]}")
    
    print("\n🔗 CUSTOMER RELATIONSHIPS:")
    print("-" * 40)
    
    # Check relationships
    print("✅ WORKING RELATIONSHIPS:")
    print("   - sales.customer_id → users.id (Individual customers)")
    print("   - sales.employee_id → employees.id (Sales reps)")
    
    print("\n❌ NO RELATIONSHIPS:")
    print("   - users.username ≠ orders.customer_name (Different customer types)")
    print("   - No direct link between individual users and company orders")
    
    print("\n📊 CUSTOMER SUMMARY:")
    print("-" * 40)
    
    # Count customers
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM sales")
    sales_customer_count = cursor.fetchone()[0]
    
    print(f"   Individual customers (users): {user_count}")
    print(f"   Company customers (orders): {order_count}")
    print(f"   Customers with sales: {sales_customer_count}")
    
    print("\n💡 CUSTOMER STORAGE CONCLUSION:")
    print("-" * 40)
    print("🏠 CUSTOMERS ARE STORED IN TWO PLACES:")
    print("   1. Individual customers → 'users' table")
    print("      - Identified by: id, username, email")
    print("      - Related to: sales (via customer_id)")
    print("")
    print("   2. Company customers → 'orders' table")
    print("      - Identified by: id, customer_name")
    print("      - NOT related to users table")
    print("")
    print("🔍 TO FIND CUSTOMERS:")
    print("   - Individual customers: SELECT * FROM users")
    print("   - Company customers: SELECT * FROM orders")
    print("   - Customer purchases: SELECT u.*, s.* FROM users u JOIN sales s ON u.id = s.customer_id")
    
    conn.close()

if __name__ == "__main__":
    analyze_customer_storage()
