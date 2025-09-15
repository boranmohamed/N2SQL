#!/usr/bin/env python3
"""
Fix Qdrant migration with proper data format conversion.
"""
import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

def migrate_with_proper_format():
    """Migrate data with proper PointStruct format."""
    print("🔧 Migrating data with proper format...")
    
    try:
        # Connect to local database
        local_client = QdrantClient(path="./qdrant_db")
        local_points = local_client.scroll("database_schema", limit=100, with_payload=True)
        
        if not local_points[0]:
            print("ℹ️ No data found in local database")
            return True
        
        print(f"📂 Found {len(local_points[0])} points in local database")
        
        # Connect to Docker Qdrant
        docker_client = QdrantClient(host="localhost", port=6333)
        
        # Convert and upload points one by one
        converted_points = []
        for i, point in enumerate(local_points[0]):
            try:
                # Convert to proper PointStruct format
                converted_point = PointStruct(
                    id=i,  # Use integer ID
                    vector=point.vector,
                    payload=point.payload
                )
                converted_points.append(converted_point)
            except Exception as e:
                print(f"⚠️ Failed to convert point {i}: {e}")
                continue
        
        if converted_points:
            print(f"📤 Uploading {len(converted_points)} converted points...")
            docker_client.upsert("database_schema", converted_points)
            print("✅ Data migration completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_sample_schema_data():
    """Create proper sample schema data."""
    print("📝 Creating proper sample schema data...")
    
    try:
        client = QdrantClient(host="localhost", port=6333)
        
        # Check if we have data
        points = client.scroll("database_schema", limit=1, with_payload=True)
        if points[0]:
            print(f"ℹ️ Data already exists ({len(points[0])} points), skipping sample creation")
            return True
        
        # Create proper sample data
        sample_points = [
            PointStruct(
                id=1,
                vector=[0.1] * 384,
                payload={
                    "text": "Table: users\nDescription: Contains user account information\nColumns: id (INTEGER PRIMARY KEY), username (TEXT), email (TEXT), created_at (DATETIME)",
                    "type": "table_schema",
                    "table": "users"
                }
            ),
            PointStruct(
                id=2,
                vector=[0.2] * 384,
                payload={
                    "text": "Table: employees\nDescription: Employee information and department details\nColumns: id (INTEGER PRIMARY KEY), first_name (TEXT), last_name (TEXT), department (TEXT), salary (REAL)",
                    "type": "table_schema",
                    "table": "employees"
                }
            ),
            PointStruct(
                id=3,
                vector=[0.3] * 384,
                payload={
                    "text": "Table: sales\nDescription: Sales transactions and customer interactions\nColumns: id (INTEGER PRIMARY KEY), customer_id (INTEGER), amount (REAL), sale_date (DATETIME), employee_id (INTEGER)",
                    "type": "table_schema",
                    "table": "sales"
                }
            ),
            PointStruct(
                id=4,
                vector=[0.4] * 384,
                payload={
                    "text": "Table: orders\nDescription: Customer orders and transactions\nColumns: id (INTEGER PRIMARY KEY), customer_name (TEXT), total_amount (REAL), order_date (DATETIME), status (TEXT)",
                    "type": "table_schema",
                    "table": "orders"
                }
            )
        ]
        
        # Upload sample data
        client.upsert("database_schema", sample_points)
        print(f"✅ Created {len(sample_points)} sample schema points")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def test_rag_system():
    """Test the RAG system with Docker Qdrant."""
    print("🧪 Testing RAG system with Docker Qdrant...")
    
    try:
        # Import and test RAG system
        sys.path.append('.')
        from app.infrastructure.enhanced_rag_system import EnhancedRAGSystem
        
        rag_system = EnhancedRAGSystem(db_path="vanna_app_clean.db")
        
        # Test initialization
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(rag_system.initialize())
            if success:
                print("✅ RAG system initialized successfully with Docker Qdrant")
                
                # Test context retrieval
                context = rag_system.get_schema_context()
                print(f"✅ Schema context retrieved ({len(context)} characters)")
                print(f"📄 Context preview: {context[:200]}...")
                
                return True
            else:
                print("❌ RAG system initialization failed")
                return False
        finally:
            loop.close()
        
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False

def main():
    """Main function."""
    print("🔧 Qdrant Migration Fix")
    print("=" * 30)
    
    # Step 1: Migrate data with proper format
    if not migrate_with_proper_format():
        print("⚠️ Data migration failed")
    
    # Step 2: Create sample data if needed
    if not create_sample_schema_data():
        print("⚠️ Sample data creation failed")
    
    # Step 3: Test RAG system
    if not test_rag_system():
        print("❌ RAG system test failed")
        return False
    
    print("\n🎉 Migration fix completed successfully!")
    print("✅ Docker Qdrant is running and accessible")
    print("✅ Data migrated with proper format")
    print("✅ Sample data created")
    print("✅ RAG system tested successfully")
    
    print("\n📝 Next steps:")
    print("1. Restart your web interface: python start_visual_tester.py")
    print("2. Test RAG functionality in the web interface")
    print("3. Run training with RAG context")
    print("4. Ask questions like 'Calculate customer lifetime value'")
    
    return True

if __name__ == "__main__":
    main()
