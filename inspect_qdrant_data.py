#!/usr/bin/env python3
"""
Inspect what's currently stored in Qdrant vs what should be there.
"""
import sqlite3
from qdrant_client import QdrantClient

def inspect_qdrant_vs_database():
    """Compare Qdrant data with actual database schema."""
    print("🔍 Inspecting Qdrant vs Database Schema")
    print("=" * 50)
    
    try:
        # Connect to Qdrant
        client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
        collection_name = "database_schema"
        
        # Get all points from Qdrant
        all_points = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True
        )
        
        print(f"📊 Found {len(all_points[0])} points in Qdrant")
        
        # Get actual database schema
        conn = sqlite3.connect("vanna_app_clean.db")
        cursor = conn.cursor()
        
        # Get orders table schema
        cursor.execute("PRAGMA table_info(orders)")
        actual_columns = [col[1] for col in cursor.fetchall()]
        
        conn.close()
        
        print(f"\n📋 Actual database orders table columns: {actual_columns}")
        
        # Find orders table in Qdrant
        orders_point = None
        for point in all_points[0]:
            if point.payload and point.payload.get('table') == 'orders':
                orders_point = point
                break
        
        if orders_point:
            print(f"\n📦 Qdrant orders table data:")
            print(f"   Text: {orders_point.payload.get('text', '')}")
            print(f"   Columns: {orders_point.payload.get('columns', [])}")
            
            qdrant_columns = orders_point.payload.get('columns', [])
            
            print(f"\n🔍 Comparison:")
            print(f"   Database has: {actual_columns}")
            print(f"   Qdrant has:   {qdrant_columns}")
            
            # Check for the specific issue
            if 'order_date' in qdrant_columns and 'created_at' not in qdrant_columns:
                print(f"\n❌ ISSUE FOUND:")
                print(f"   - Qdrant has 'order_date' but database has 'created_at'")
                print(f"   - This is why Vanna generates incorrect SQL")
            elif 'created_at' in qdrant_columns and 'order_date' not in qdrant_columns:
                print(f"\n✅ CORRECT:")
                print(f"   - Qdrant matches database schema")
            else:
                print(f"\n⚠️ PARTIAL MATCH:")
                print(f"   - Some columns match, some don't")
        else:
            print(f"\n❌ Orders table not found in Qdrant")
        
        # Show all tables in Qdrant
        print(f"\n📊 All tables in Qdrant:")
        for point in all_points[0]:
            if point.payload and point.payload.get('type') == 'table_schema':
                table_name = point.payload.get('table', 'unknown')
                columns = point.payload.get('columns', [])
                print(f"   {table_name}: {columns}")
        
    except Exception as e:
        print(f"❌ Inspection failed: {e}")

if __name__ == "__main__":
    inspect_qdrant_vs_database()
