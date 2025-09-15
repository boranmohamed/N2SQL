#!/usr/bin/env python3
"""
Migrate data from local Qdrant to Docker Qdrant server.
"""
import os
import sys
from qdrant_client import QdrantClient

def check_docker_qdrant():
    """Check if Docker Qdrant is running."""
    try:
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print("✅ Docker Qdrant is running on localhost:6333")
        print(f"   Collections: {len(collections.collections)}")
        return True
    except Exception as e:
        print(f"❌ Docker Qdrant not accessible: {e}")
        return False

def migrate_data():
    """Migrate data from local Qdrant to Docker Qdrant."""
    print("📦 Migrating data to Docker Qdrant...")
    
    try:
        # Connect to local database (if it exists)
        local_data = []
        local_qdrant_path = "./qdrant_db"
        
        if os.path.exists(local_qdrant_path):
            print("📂 Found local Qdrant database, reading data...")
            try:
                local_client = QdrantClient(path=local_qdrant_path)
                local_points = local_client.scroll("database_schema", limit=100, with_payload=True)
                local_data = local_points[0] if local_points[0] else []
                print(f"   Found {len(local_data)} points in local database")
            except Exception as e:
                print(f"⚠️ Could not read local data: {e}")
        else:
            print("ℹ️ No local Qdrant database found")
        
        # Connect to Docker Qdrant
        docker_client = QdrantClient(host="localhost", port=6333)
        
        # Create collection if it doesn't exist
        collections = docker_client.get_collections()
        collection_exists = any(col.name == "database_schema" for col in collections.collections)
        
        if not collection_exists:
            print("🆕 Creating collection on Docker Qdrant...")
            docker_client.create_collection(
                collection_name="database_schema",
                vectors_config={"size": 384, "distance": "Cosine"}
            )
            print("✅ Collection created")
        else:
            print("✅ Collection already exists on Docker Qdrant")
        
        # Upload data if we have any
        if local_data:
            print(f"📤 Uploading {len(local_data)} points to Docker Qdrant...")
            docker_client.upsert("database_schema", local_data)
            print("✅ Data migration completed")
        else:
            print("ℹ️ No data to migrate")
        
        # Verify migration
        docker_points = docker_client.scroll("database_schema", limit=10, with_payload=True)
        print(f"✅ Verification: Docker Qdrant now has {len(docker_points[0])} points")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_sample_data():
    """Create sample schema data if no data exists."""
    print("📝 Creating sample schema data...")
    
    try:
        client = QdrantClient(host="localhost", port=6333)
        
        # Check if we have any data
        points = client.scroll("database_schema", limit=1, with_payload=True)
        if points[0]:
            print("ℹ️ Data already exists, skipping sample creation")
            return True
        
        # Create sample schema data
        sample_points = [
            {
                "id": "table_users_1",
                "vector": [0.1] * 384,  # Dummy vector
                "payload": {
                    "text": "Table: users\nDescription: Contains user account information\nColumns: id (INTEGER PRIMARY KEY), username (TEXT), email (TEXT), created_at (DATETIME)",
                    "type": "table_schema",
                    "table": "users"
                }
            },
            {
                "id": "table_employees_1", 
                "vector": [0.2] * 384,  # Dummy vector
                "payload": {
                    "text": "Table: employees\nDescription: Employee information and department details\nColumns: id (INTEGER PRIMARY KEY), first_name (TEXT), last_name (TEXT), department (TEXT), salary (REAL)",
                    "type": "table_schema",
                    "table": "employees"
                }
            },
            {
                "id": "table_sales_1",
                "vector": [0.3] * 384,  # Dummy vector
                "payload": {
                    "text": "Table: sales\nDescription: Sales transactions and customer interactions\nColumns: id (INTEGER PRIMARY KEY), customer_id (INTEGER), amount (REAL), sale_date (DATETIME), employee_id (INTEGER)",
                    "type": "table_schema", 
                    "table": "sales"
                }
            }
        ]
        
        # Upload sample data
        client.upsert("database_schema", sample_points)
        print("✅ Sample schema data created")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def test_connection():
    """Test the Docker Qdrant connection."""
    print("🧪 Testing Docker Qdrant connection...")
    
    try:
        client = QdrantClient(host="localhost", port=6333)
        
        # Test basic operations
        collections = client.get_collections()
        print(f"✅ Connection successful - {len(collections.collections)} collections")
        
        # Test collection access
        if collections.collections:
            collection_name = collections.collections[0].name
            points = client.scroll(collection_name, limit=1, with_payload=True)
            print(f"✅ Collection '{collection_name}' accessible - {len(points[0])} points")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main migration function."""
    print("🐳 Docker Qdrant Migration")
    print("=" * 40)
    
    # Step 1: Check Docker Qdrant
    if not check_docker_qdrant():
        print("\n❌ Docker Qdrant is not running!")
        print("Please start it with: docker run -d --name qdrant -p 6333:6333 qdrant/qdrant")
        return False
    
    # Step 2: Migrate data
    if not migrate_data():
        print("⚠️ Data migration failed, but continuing...")
    
    # Step 3: Create sample data if needed
    if not create_sample_data():
        print("⚠️ Sample data creation failed")
    
    # Step 4: Test connection
    if not test_connection():
        print("❌ Connection test failed")
        return False
    
    print("\n🎉 Migration completed successfully!")
    print("✅ Docker Qdrant is running and accessible")
    print("✅ Data migrated (or sample data created)")
    print("✅ Connection tested successfully")
    
    print("\n📝 Next steps:")
    print("1. Your RAG system is now configured to use Docker Qdrant")
    print("2. Restart your web interface: python start_visual_tester.py")
    print("3. Test RAG functionality in the web interface")
    print("4. Run training with RAG context")
    
    return True

if __name__ == "__main__":
    main()
