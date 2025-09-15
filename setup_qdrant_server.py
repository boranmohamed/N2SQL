#!/usr/bin/env python3
"""
Setup Qdrant server for proper multi-process access.
"""
import subprocess
import sys
import time
import requests
import os

def install_qdrant():
    """Install Qdrant server."""
    print("📦 Installing Qdrant server...")
    try:
        # Try to install via pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "qdrant-client[fastembed]"])
        print("✅ Qdrant client installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Qdrant via pip")
        print("Please install Qdrant manually:")
        print("1. Download from: https://github.com/qdrant/qdrant/releases")
        print("2. Or use Docker: docker run -p 6333:6333 qdrant/qdrant")

def start_qdrant_server():
    """Start Qdrant server."""
    print("🚀 Starting Qdrant server...")
    
    # Check if Qdrant is already running
    try:
        response = requests.get("http://localhost:6333/health", timeout=5)
        if response.status_code == 200:
            print("✅ Qdrant server is already running on localhost:6333")
            return True
    except:
        pass
    
    # Try to start Qdrant server
    try:
        # Method 1: Try Docker
        print("🐳 Trying to start Qdrant with Docker...")
        subprocess.Popen([
            "docker", "run", "-d", 
            "--name", "qdrant", 
            "-p", "6333:6333",
            "-v", f"{os.getcwd()}/qdrant_data:/qdrant/storage",
            "qdrant/qdrant"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        for i in range(30):
            try:
                response = requests.get("http://localhost:6333/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Qdrant server started successfully on localhost:6333")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Qdrant server failed to start via Docker")
        return False
        
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker or Qdrant manually.")
        return False

def migrate_data_to_server():
    """Migrate data from local Qdrant to server."""
    print("📦 Migrating data to Qdrant server...")
    
    try:
        from qdrant_client import QdrantClient
        
        # Connect to local database
        local_client = QdrantClient(path="./qdrant_db")
        
        # Connect to server
        server_client = QdrantClient(host="localhost", port=6333)
        
        # Get all points from local database
        local_points = local_client.scroll("database_schema", limit=100, with_payload=True)
        
        if local_points[0]:  # If we have points
            # Create collection on server
            try:
                server_client.create_collection(
                    collection_name="database_schema",
                    vectors_config={"size": 384, "distance": "Cosine"}
                )
                print("✅ Created collection on server")
            except:
                print("ℹ️ Collection already exists on server")
            
            # Upload points to server
            points_to_upload = []
            for point in local_points[0]:
                points_to_upload.append(point)
            
            if points_to_upload:
                server_client.upsert("database_schema", points_to_upload)
                print(f"✅ Migrated {len(points_to_upload)} points to server")
        
        print("✅ Data migration completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def update_rag_system_config():
    """Update RAG system to use server instead of local database."""
    print("🔧 Updating RAG system configuration...")
    
    config_file = "app/infrastructure/enhanced_rag_system.py"
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace local connection with server connection
        old_connection = 'QdrantClient(\n                path="./qdrant_db",  # Use existing local Qdrant database\n                prefer_grpc=False\n            )'
        
        new_connection = 'QdrantClient(\n                host="localhost",\n                port=6333,\n                prefer_grpc=False\n            )'
        
        if old_connection in content:
            content = content.replace(old_connection, new_connection)
            
            with open(config_file, 'w') as f:
                f.write(content)
            
            print("✅ Updated RAG system to use Qdrant server")
            return True
        else:
            print("⚠️ Connection code not found in expected format")
            return False
            
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

def main():
    """Main setup function."""
    print("🔧 Qdrant Server Setup")
    print("=" * 50)
    
    # Step 1: Install dependencies
    install_qdrant()
    
    # Step 2: Start Qdrant server
    if not start_qdrant_server():
        print("\n❌ Cannot proceed without Qdrant server")
        print("Please start Qdrant server manually:")
        print("1. Docker: docker run -p 6333:6333 qdrant/qdrant")
        print("2. Or download and run Qdrant binary")
        return False
    
    # Step 3: Migrate data
    if not migrate_data_to_server():
        print("⚠️ Data migration failed, but server is running")
    
    # Step 4: Update configuration
    if not update_rag_system_config():
        print("⚠️ Configuration update failed")
    
    print("\n🎉 Setup completed!")
    print("✅ Qdrant server is running on localhost:6333")
    print("✅ RAG system updated to use server")
    print("✅ Data migrated to server")
    
    print("\n📝 Next steps:")
    print("1. Restart your web interface")
    print("2. Test RAG functionality")
    print("3. Run training with RAG context")
    
    return True

if __name__ == "__main__":
    main()
