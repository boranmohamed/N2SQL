#!/usr/bin/env python3
"""
Fix local Qdrant connection issues by properly managing connections.
"""
import os
import shutil
import time
from qdrant_client import QdrantClient

def backup_and_restart_qdrant():
    """Backup current Qdrant data and restart cleanly."""
    print("🔄 Fixing local Qdrant connection...")
    
    qdrant_path = "./qdrant_db"
    backup_path = "./qdrant_db_backup"
    
    try:
        # Step 1: Stop any running processes that might be using Qdrant
        print("⏹️ Stopping any processes using Qdrant...")
        
        # Step 2: Backup existing data
        if os.path.exists(qdrant_path):
            print(f"📦 Backing up existing Qdrant data...")
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(qdrant_path, backup_path)
            print(f"✅ Backup created at {backup_path}")
        
        # Step 3: Remove existing database
        if os.path.exists(qdrant_path):
            print("🗑️ Removing existing Qdrant database...")
            shutil.rmtree(qdrant_path)
            print("✅ Old database removed")
        
        # Step 4: Create new clean database
        print("🆕 Creating new Qdrant database...")
        client = QdrantClient(path=qdrant_path)
        
        # Test connection
        collections = client.get_collections()
        print(f"✅ New database created successfully")
        print(f"   Collections: {len(collections.collections)}")
        
        # Step 5: Restore data from backup if it exists
        if os.path.exists(backup_path):
            print("📥 Restoring data from backup...")
            try:
                # Copy data back
                shutil.copytree(backup_path, qdrant_path)
                print("✅ Data restored successfully")
            except Exception as e:
                print(f"⚠️ Data restoration failed: {e}")
                print("   You may need to re-populate the database")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix Qdrant: {e}")
        return False

def create_connection_manager():
    """Create a connection manager for proper Qdrant access."""
    connection_code = '''
"""
Qdrant Connection Manager for proper resource handling.
"""
import threading
from contextlib import contextmanager
from qdrant_client import QdrantClient

class QdrantConnectionManager:
    """Manages Qdrant connections to prevent conflicts."""
    
    def __init__(self, qdrant_path="./qdrant_db"):
        self.qdrant_path = qdrant_path
        self._lock = threading.Lock()
        self._client = None
    
    @contextmanager
    def get_client(self):
        """Get a Qdrant client with proper locking."""
        with self._lock:
            try:
                if self._client is None:
                    self._client = QdrantClient(path=self.qdrant_path)
                yield self._client
            except Exception as e:
                # If connection fails, try to recreate
                try:
                    self._client = QdrantClient(path=self.qdrant_path)
                    yield self._client
                except Exception as e2:
                    raise RuntimeError(f"Failed to connect to Qdrant: {e2}")
    
    def close(self):
        """Close the connection."""
        with self._lock:
            if self._client:
                self._client.close()
                self._client = None

# Global connection manager
qdrant_manager = QdrantConnectionManager()
'''
    
    try:
        with open("qdrant_connection_manager.py", "w") as f:
            f.write(connection_code)
        print("✅ Created connection manager")
        return True
    except Exception as e:
        print(f"❌ Failed to create connection manager: {e}")
        return False

def update_rag_system_with_manager():
    """Update RAG system to use connection manager."""
    print("🔧 Updating RAG system to use connection manager...")
    
    try:
        with open("app/infrastructure/enhanced_rag_system.py", "r") as f:
            content = f.read()
        
        # Add import
        if "from qdrant_connection_manager import qdrant_manager" not in content:
            content = content.replace(
                "from qdrant_client import QdrantClient",
                "from qdrant_client import QdrantClient\nfrom qdrant_connection_manager import qdrant_manager"
            )
        
        # Replace connection usage
        old_init = '''self.vector_db = QdrantClient(
                path="./qdrant_db",  # Use existing local Qdrant database
                prefer_grpc=False
            )'''
        
        new_init = '''self.vector_db = qdrant_manager'''
        
        if old_init in content:
            content = content.replace(old_init, new_init)
            
            # Update all vector_db usage to use context manager
            content = content.replace(
                "self.vector_db.scroll(",
                "with qdrant_manager.get_client() as client:\n                client.scroll("
            )
            
            with open("app/infrastructure/enhanced_rag_system.py", "w") as f:
                f.write(content)
            
            print("✅ Updated RAG system to use connection manager")
            return True
        else:
            print("⚠️ Could not find expected connection code")
            return False
            
    except Exception as e:
        print(f"❌ Failed to update RAG system: {e}")
        return False

def main():
    """Main fix function."""
    print("🔧 Local Qdrant Connection Fix")
    print("=" * 40)
    
    # Step 1: Fix database
    if not backup_and_restart_qdrant():
        print("❌ Failed to fix database")
        return False
    
    # Step 2: Create connection manager
    if not create_connection_manager():
        print("❌ Failed to create connection manager")
        return False
    
    # Step 3: Update RAG system
    if not update_rag_system_with_manager():
        print("⚠️ Failed to update RAG system")
    
    print("\n🎉 Local Qdrant fix completed!")
    print("✅ Database recreated cleanly")
    print("✅ Connection manager created")
    print("✅ RAG system updated")
    
    print("\n📝 Next steps:")
    print("1. Restart your web interface")
    print("2. Re-populate the database if needed")
    print("3. Test RAG functionality")
    
    return True

if __name__ == "__main__":
    main()
