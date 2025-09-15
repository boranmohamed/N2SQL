#!/usr/bin/env python3
"""Check database schema to understand the column structure."""
import sqlite3

def check_schema():
    conn = sqlite3.connect('vanna_app_clean.db')
    cursor = conn.cursor()
    
    tables = ['users', 'employees', 'sales', 'orders']
    
    for table in tables:
        print(f"\n{table.upper()} table columns:")
        cursor.execute(f'PRAGMA table_info({table})')
        for row in cursor.fetchall():
            print(f"  {row[1]} ({row[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
