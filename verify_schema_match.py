#!/usr/bin/env python3
"""
Verify that Qdrant schema truly matches the actual database structure.
This ensures the RAG system has accurate schema information.
"""
import sqlite3
from qdrant_client import QdrantClient
from typing import Dict, List, Any

def verify_schema_match():
    """Verify that Qdrant schema matches actual database."""
    print("🔍 SCHEMA MATCH VERIFICATION")
    print("=" * 50)
    
    try:
        # Connect to Qdrant
        qdrant_client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
        collection_name = "database_schema"
        
        # Get all points from Qdrant
        all_points = qdrant_client.scroll(
            collection_name=collection_name,
            limit=1000,
            with_payload=True
        )
        
        print(f"📊 Found {len(all_points[0])} points in Qdrant")
        
        # Get actual database schema
        print("\n📋 Getting actual database schema...")
        real_schema = get_real_database_schema()
        
        # Compare each table
        print("\n🔍 Comparing Qdrant vs Database:")
        print("-" * 50)
        
        all_match = True
        
        for table_name, real_columns in real_schema.items():
            print(f"\n📊 Table: {table_name}")
            
            # Find table in Qdrant
            qdrant_table = None
            for point in all_points[0]:
                if (point.payload and 
                    point.payload.get('table') == table_name and 
                    point.payload.get('type') == 'table_schema'):
                    qdrant_table = point.payload
                    break
            
            if not qdrant_table:
                print(f"   ❌ Table not found in Qdrant")
                all_match = False
                continue
            
            # Get Qdrant columns
            qdrant_columns = qdrant_table.get('columns', [])
            
            # Compare columns
            real_set = set(real_columns)
            qdrant_set = set(qdrant_columns)
            
            if real_set == qdrant_set:
                print(f"   ✅ Columns match perfectly")
                print(f"   📝 Columns: {real_columns}")
            else:
                print(f"   ❌ Column mismatch!")
                print(f"   🗄️  Database: {sorted(real_columns)}")
                print(f"   🗃️  Qdrant:   {sorted(qdrant_columns)}")
                
                missing_in_qdrant = real_set - qdrant_set
                extra_in_qdrant = qdrant_set - real_set
                
                if missing_in_qdrant:
                    print(f"   ⚠️  Missing in Qdrant: {missing_in_qdrant}")
                if extra_in_qdrant:
                    print(f"   ⚠️  Extra in Qdrant: {extra_in_qdrant}")
                
                all_match = False
            
            # Check if marked as real schema
            is_real = qdrant_table.get('is_real_schema', False)
            if is_real:
                print(f"   ✅ Marked as real schema")
            else:
                print(f"   ⚠️  Not marked as real schema")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        if all_match:
            print("🎉 PERFECT MATCH!")
            print("✅ Qdrant schema matches database exactly")
            print("✅ RAG system has accurate schema information")
            print("✅ SQL generation should work correctly")
        else:
            print("❌ MISMATCH DETECTED!")
            print("⚠️  Qdrant schema does not match database")
            print("⚠️  RAG system may provide incorrect information")
            print("⚠️  SQL generation may fail or be incorrect")
        
        return all_match
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def get_real_database_schema() -> Dict[str, List[str]]:
    """Get the real schema from the database."""
    schema = {}
    
    try:
        conn = sqlite3.connect("vanna_app_clean.db")
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            if table_name.startswith('sqlite_'):
                continue
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            schema[table_name] = columns
        
        conn.close()
        return schema
        
    except Exception as e:
        print(f"❌ Failed to get database schema: {e}")
        return {}

def show_detailed_comparison():
    """Show detailed comparison between Qdrant and database."""
    print("\n🔍 DETAILED SCHEMA COMPARISON")
    print("=" * 60)
    
    try:
        # Get Qdrant data
        qdrant_client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
        all_points = qdrant_client.scroll(
            collection_name="database_schema",
            limit=1000,
            with_payload=True
        )
        
        # Get database data
        real_schema = get_real_database_schema()
        
        print("\n📊 SIDE-BY-SIDE COMPARISON:")
        print("-" * 60)
        
        for table_name in real_schema.keys():
            print(f"\n🗂️  TABLE: {table_name}")
            print("   " + "=" * 40)
            
            # Database columns
            db_columns = real_schema[table_name]
            print(f"   🗄️  DATABASE: {db_columns}")
            
            # Qdrant columns
            qdrant_columns = None
            for point in all_points[0]:
                if (point.payload and 
                    point.payload.get('table') == table_name and 
                    point.payload.get('type') == 'table_schema'):
                    qdrant_columns = point.payload.get('columns', [])
                    break
            
            if qdrant_columns:
                print(f"   🗃️  QDRANT:   {qdrant_columns}")
                
                # Show differences
                db_set = set(db_columns)
                qdrant_set = set(qdrant_columns)
                
                if db_set == qdrant_set:
                    print(f"   ✅ PERFECT MATCH")
                else:
                    missing = db_set - qdrant_set
                    extra = qdrant_set - db_set
                    
                    if missing:
                        print(f"   ❌ MISSING: {missing}")
                    if extra:
                        print(f"   ❌ EXTRA:   {extra}")
            else:
                print(f"   ❌ NOT FOUND IN QDRANT")
        
    except Exception as e:
        print(f"❌ Detailed comparison failed: {e}")

def main():
    """Main function."""
    print("🔍 SCHEMA VERIFICATION TOOL")
    print("=" * 60)
    
    # Basic verification
    match = verify_schema_match()
    
    # Detailed comparison
    show_detailed_comparison()
    
    print("\n" + "=" * 60)
    if match:
        print("🎉 VERIFICATION COMPLETE - SCHEMAS MATCH!")
    else:
        print("❌ VERIFICATION COMPLETE - SCHEMAS DO NOT MATCH!")
        print("💡 Run 'python real_schema_extractor.py' to fix the mismatch")

if __name__ == "__main__":
    main()
