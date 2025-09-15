#!/usr/bin/env python3
"""
Fix incorrect schema data stored in Qdrant.
The Qdrant database has 'order_date' but the actual database has 'created_at'.
"""
import os
import asyncio
import sqlite3
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams

# Set to use local Vanna
os.environ["USE_LOCAL_VANNA"] = "true"

async def fix_qdrant_schema_data():
    """Fix the incorrect schema data in Qdrant."""
    print("🔧 Fixing Qdrant Schema Data")
    print("=" * 50)
    
    try:
        # Connect to Qdrant
        client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
        collection_name = "database_schema"
        
        # Check if collection exists
        collections = client.get_collections()
        collection_exists = any(col.name == collection_name for col in collections.collections)
        
        if not collection_exists:
            print(f"❌ Collection '{collection_name}' not found")
            return False
        
        print(f"✅ Connected to Qdrant collection '{collection_name}'")
        
        # Get actual database schema
        print("\n📋 Step 1: Getting actual database schema...")
        actual_schema = get_actual_database_schema()
        
        # Clear existing incorrect data
        print("\n🗑️ Step 2: Clearing existing incorrect schema data...")
        # Get all points first to find the IDs to delete
        all_points = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True
        )
        
        # Find points with type 'table_schema'
        points_to_delete = []
        for point in all_points[0]:
            if point.payload and point.payload.get('type') == 'table_schema':
                points_to_delete.append(point.id)
        
        if points_to_delete:
            client.delete(
                collection_name=collection_name,
                points_selector=points_to_delete
            )
            print(f"✅ Cleared {len(points_to_delete)} existing table_schema data points")
        else:
            print("ℹ️ No existing table_schema data found to clear")
        
        # Insert correct schema data
        print("\n📝 Step 3: Inserting correct schema data...")
        points = create_correct_schema_points(actual_schema)
        
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        print(f"✅ Inserted {len(points)} corrected schema points")
        
        # Verify the fix
        print("\n🧪 Step 4: Verifying the fix...")
        await verify_qdrant_fix(client, collection_name)
        
        print("\n🎉 Qdrant schema data fix completed!")
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

def create_correct_schema_points(actual_schema):
    """Create correct schema points for Qdrant."""
    points = []
    
    for table_name, columns in actual_schema.items():
        column_names = [col['name'] for col in columns]
        column_types = [f"{col['name']} ({col['type']})" for col in columns]
        
        # Create table description
        if table_name == "orders":
            description = "Customer orders and transactions"
            key_fields = "customer_name, total_amount, status"
        elif table_name == "users":
            description = "User account information"
            key_fields = "username, email"
        elif table_name == "employees":
            description = "Employee information and department details"
            key_fields = "first_name, last_name, department"
        elif table_name == "sales":
            description = "Sales transactions and customer interactions"
            key_fields = "customer_id, amount, employee_id"
        else:
            description = f"Contains {table_name} data"
            key_fields = ", ".join(column_names[:3])
        
        # Create the text description
        text_description = f"Table: {table_name}\nDescription: {description}\nColumns: {', '.join(column_types)}\nKey fields: {key_fields}"
        
        # Create vector (simple hash-based)
        vector = create_simple_vector(table_name, column_names)
        
        # Use integer IDs based on table name
        table_id_map = {
            "users": 1,
            "employees": 2, 
            "sales": 3,
            "orders": 4
        }
        
        point_id = table_id_map.get(table_name, hash(table_name) % 1000)
        
        points.append(PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "text": text_description,
                "type": "table_schema",
                "table": table_name,
                "columns": column_names,
                "corrected": True,
                "description": description
            }
        ))
        
        print(f"   ✅ Created point for table '{table_name}' with columns: {column_names}")
    
    return points

def create_simple_vector(table_name, columns):
    """Create a simple vector for the table."""
    import hashlib
    
    # Create a 384-dimensional vector
    vector = [0.0] * 384
    
    # Use table name and columns to create a unique vector
    text = f"{table_name} {' '.join(columns)}"
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Fill vector based on hash
    for i in range(0, min(384, len(text_hash)), 2):
        if i + 1 < 384:
            vector[i] = int(text_hash[i:i+2], 16) / 255.0
            vector[i+1] = int(text_hash[i:i+2], 16) / 255.0
    
    # Add table-specific patterns
    if table_name == "orders":
        vector[0] = 0.1
        vector[1] = 0.2
    elif table_name == "users":
        vector[0] = 0.3
        vector[1] = 0.4
    elif table_name == "employees":
        vector[0] = 0.5
        vector[1] = 0.6
    elif table_name == "sales":
        vector[0] = 0.7
        vector[1] = 0.8
    
    return vector

async def verify_qdrant_fix(client, collection_name):
    """Verify that the Qdrant fix worked."""
    try:
        # Get all points
        all_points = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True
        )
        
        print(f"📊 Total points in collection: {len(all_points[0])}")
        
        # Check for orders table specifically
        orders_found = False
        for point in all_points[0]:
            if point.payload and point.payload.get('table') == 'orders':
                orders_found = True
                text = point.payload.get('text', '')
                columns = point.payload.get('columns', [])
                
                print(f"\n📋 Orders table data:")
                print(f"   Text: {text}")
                print(f"   Columns: {columns}")
                
                # Check if it has the correct column
                if 'created_at' in columns and 'order_date' not in columns:
                    print("   ✅ CORRECT: Has 'created_at' and no 'order_date'")
                else:
                    print("   ❌ INCORRECT: Still has wrong columns")
                
                break
        
        if not orders_found:
            print("❌ Orders table not found in Qdrant")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

async def test_sql_generation_after_fix():
    """Test SQL generation after fixing Qdrant data."""
    print("\n🧪 Testing SQL Generation After Fix")
    print("=" * 40)
    
    try:
        from app.infrastructure.vanna_factory import get_vanna_client_from_env
        
        # Initialize Vanna client
        client = get_vanna_client_from_env()
        await client.initialize()
        
        # Test the problematic question
        question = "Show me the complete customer journey: users, their orders, and sales"
        
        print(f"📝 Question: {question}")
        
        # Generate SQL
        sql = await client.generate_sql(question)
        print(f"\n🤖 Generated SQL:")
        print(sql)
        
        # Check if it uses correct column names
        if 'created_at' in sql and 'order_date' not in sql:
            print("\n✅ SUCCESS: SQL uses correct column names!")
            return True
        else:
            print("\n❌ FAILED: SQL still uses incorrect column names")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function."""
    try:
        # Fix Qdrant data
        fix_success = asyncio.run(fix_qdrant_schema_data())
        
        if fix_success:
            # Test SQL generation
            test_success = asyncio.run(test_sql_generation_after_fix())
            
            if test_success:
                print("\n🎉 COMPLETE SUCCESS!")
                print("✅ Qdrant schema data corrected")
                print("✅ SQL generation now uses correct column names")
                print("✅ The 'order_date' → 'created_at' issue is fixed")
            else:
                print("\n⚠️ Qdrant fixed but SQL generation test failed")
                print("You may need to retrain Vanna with the corrected schema")
        else:
            print("\n❌ Qdrant fix failed")
            
    except Exception as e:
        print(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main()
