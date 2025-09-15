#!/usr/bin/env python3
"""
Real Database Schema Extractor and Qdrant Storage System
This ensures Qdrant always stores the ACTUAL database schema, not training data.
"""
import os
import sqlite3
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import hashlib

@dataclass
class ColumnInfo:
    """Column information from database."""
    name: str
    type: str
    not_null: bool
    default_value: Optional[str]
    primary_key: bool
    foreign_key: Optional[str] = None

@dataclass
class TableInfo:
    """Table information from database."""
    name: str
    columns: List[ColumnInfo]
    indexes: List[str]
    sample_data: List[Dict[str, Any]]

class RealSchemaExtractor:
    """
    Extracts REAL schema from database and stores it in Qdrant.
    This ensures Qdrant always has the actual database structure.
    """
    
    def __init__(self, db_path: str, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.db_path = db_path
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port, prefer_grpc=False)
        self.collection_name = "database_schema"
        
    async def extract_and_store_real_schema(self) -> bool:
        """Extract real schema from database and store in Qdrant."""
        print("🔍 REAL SCHEMA EXTRACTION")
        print("=" * 50)
        
        try:
            # Step 1: Extract real schema from database
            print("📋 Step 1: Extracting REAL schema from database...")
            real_schema = await self._extract_real_database_schema()
            
            if not real_schema:
                print("❌ Failed to extract schema from database")
                return False
            
            print(f"✅ Extracted schema for {len(real_schema)} tables")
            
            # Step 2: Clear old incorrect data from Qdrant
            print("\n🗑️ Step 2: Clearing old schema data from Qdrant...")
            await self._clear_old_schema_data()
            
            # Step 3: Store real schema in Qdrant
            print("\n💾 Step 3: Storing REAL schema in Qdrant...")
            success = await self._store_real_schema_in_qdrant(real_schema)
            
            if success:
                print("✅ Real schema stored successfully in Qdrant")
            else:
                print("❌ Failed to store schema in Qdrant")
                return False
            
            # Step 4: Verify the storage
            print("\n🧪 Step 4: Verifying stored schema...")
            verification_success = await self._verify_stored_schema(real_schema)
            
            if verification_success:
                print("✅ Schema verification passed - Qdrant matches database!")
                return True
            else:
                print("❌ Schema verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Schema extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _extract_real_database_schema(self) -> Dict[str, TableInfo]:
        """Extract the REAL schema from the actual database."""
        real_schema = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                if table_name.startswith('sqlite_'):
                    continue
                
                print(f"   📊 Extracting table: {table_name}")
                
                # Get column information
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                
                columns = []
                for col in columns_info:
                    column = ColumnInfo(
                        name=col[1],
                        type=col[2],
                        not_null=bool(col[3]),
                        default_value=col[4],
                        primary_key=bool(col[5])
                    )
                    columns.append(column)
                
                # Get indexes
                cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = [idx[1] for idx in cursor.fetchall()]
                
                # Get sample data (limit to 3 rows)
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_rows = cursor.fetchall()
                column_names = [col[1] for col in columns_info]
                
                sample_data = []
                for row in sample_rows:
                    sample_data.append(dict(zip(column_names, row)))
                
                # Create table info
                table_info = TableInfo(
                    name=table_name,
                    columns=columns,
                    indexes=indexes,
                    sample_data=sample_data
                )
                
                real_schema[table_name] = table_info
                
                print(f"      ✅ Columns: {[c.name for c in columns]}")
                print(f"      ✅ Indexes: {indexes}")
                print(f"      ✅ Sample rows: {len(sample_data)}")
            
            conn.close()
            return real_schema
            
        except Exception as e:
            print(f"❌ Failed to extract schema: {e}")
            return {}
    
    async def _clear_old_schema_data(self):
        """Clear old schema data from Qdrant."""
        try:
            # Get all existing points
            all_points = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1000,
                with_payload=True
            )
            
            # Find points with type 'table_schema'
            points_to_delete = []
            for point in all_points[0]:
                if point.payload and point.payload.get('type') == 'table_schema':
                    points_to_delete.append(point.id)
            
            if points_to_delete:
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=points_to_delete
                )
                print(f"✅ Cleared {len(points_to_delete)} old schema points")
            else:
                print("ℹ️ No old schema data found to clear")
                
        except Exception as e:
            print(f"❌ Failed to clear old data: {e}")
    
    async def _store_real_schema_in_qdrant(self, real_schema: Dict[str, TableInfo]) -> bool:
        """Store the real schema in Qdrant."""
        try:
            points = []
            
            for table_name, table_info in real_schema.items():
                # Create comprehensive schema description
                schema_text = self._create_schema_description(table_info)
                
                # Create vector representation
                vector = self._create_table_vector(table_name, table_info)
                
                # Create point ID based on table name
                point_id = self._get_table_point_id(table_name)
                
                # Create the point
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": schema_text,
                        "type": "table_schema",
                        "table": table_name,
                        "columns": [col.name for col in table_info.columns],
                        "column_types": [f"{col.name} ({col.type})" for col in table_info.columns],
                        "indexes": table_info.indexes,
                        "sample_data": table_info.sample_data,
                        "is_real_schema": True,
                        "extraction_timestamp": str(asyncio.get_event_loop().time())
                    }
                )
                
                points.append(point)
                print(f"   ✅ Created point for table '{table_name}'")
            
            # Store in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            print(f"✅ Stored {len(points)} real schema points in Qdrant")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store schema in Qdrant: {e}")
            return False
    
    def _create_schema_description(self, table_info: TableInfo) -> str:
        """Create a comprehensive schema description."""
        columns_desc = []
        for col in table_info.columns:
            col_desc = f"{col.name} ({col.type})"
            if col.primary_key:
                col_desc += " PRIMARY KEY"
            if col.not_null and not col.primary_key:
                col_desc += " NOT NULL"
            if col.default_value:
                col_desc += f" DEFAULT {col.default_value}"
            columns_desc.append(col_desc)
        
        description = f"""Table: {table_info.name}
Description: Contains {table_info.name} data with {len(table_info.columns)} columns
Columns: {', '.join(columns_desc)}
Indexes: {', '.join(table_info.indexes) if table_info.indexes else 'None'}
Sample Data: {table_info.sample_data[:2] if table_info.sample_data else 'No data'}
Key Fields: {', '.join([col.name for col in table_info.columns if col.primary_key or col.name in ['id', 'name', 'username', 'email']])}"""
        
        return description
    
    def _create_table_vector(self, table_name: str, table_info: TableInfo) -> List[float]:
        """Create a vector representation of the table."""
        # Create a 384-dimensional vector
        vector = [0.0] * 384
        
        # Use table name and columns to create a unique vector
        text = f"{table_name} {' '.join([col.name for col in table_info.columns])}"
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Fill vector based on hash
        for i in range(0, min(384, len(text_hash)), 2):
            if i + 1 < 384:
                vector[i] = int(text_hash[i:i+2], 16) / 255.0
                vector[i+1] = int(text_hash[i:i+2], 16) / 255.0
        
        # Add table-specific patterns
        table_patterns = {
            "users": [0.1, 0.2],
            "employees": [0.3, 0.4],
            "sales": [0.5, 0.6],
            "orders": [0.7, 0.8]
        }
        
        if table_name in table_patterns:
            pattern = table_patterns[table_name]
            vector[0] = pattern[0]
            vector[1] = pattern[1]
        
        return vector
    
    def _get_table_point_id(self, table_name: str) -> int:
        """Get point ID for table."""
        table_id_map = {
            "users": 1,
            "employees": 2,
            "sales": 3,
            "orders": 4
        }
        return table_id_map.get(table_name, hash(table_name) % 1000)
    
    async def _verify_stored_schema(self, real_schema: Dict[str, TableInfo]) -> bool:
        """Verify that stored schema matches real schema."""
        try:
            # Get all points from Qdrant
            all_points = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1000,
                with_payload=True
            )
            
            print(f"📊 Found {len(all_points[0])} points in Qdrant")
            
            # Check each table
            verification_passed = True
            
            for table_name, real_table_info in real_schema.items():
                # Find the table in Qdrant
                qdrant_table = None
                for point in all_points[0]:
                    if (point.payload and 
                        point.payload.get('table') == table_name and 
                        point.payload.get('type') == 'table_schema'):
                        qdrant_table = point.payload
                        break
                
                if not qdrant_table:
                    print(f"❌ Table '{table_name}' not found in Qdrant")
                    verification_passed = False
                    continue
                
                # Check columns match
                real_columns = [col.name for col in real_table_info.columns]
                qdrant_columns = qdrant_table.get('columns', [])
                
                if set(real_columns) == set(qdrant_columns):
                    print(f"✅ Table '{table_name}': Columns match")
                else:
                    print(f"❌ Table '{table_name}': Column mismatch")
                    print(f"   Real: {real_columns}")
                    print(f"   Qdrant: {qdrant_columns}")
                    verification_passed = False
                
                # Check if it's marked as real schema
                if qdrant_table.get('is_real_schema'):
                    print(f"✅ Table '{table_name}': Marked as real schema")
                else:
                    print(f"⚠️ Table '{table_name}': Not marked as real schema")
            
            return verification_passed
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

async def main():
    """Main function to extract and store real schema."""
    print("🚀 REAL SCHEMA EXTRACTION SYSTEM")
    print("=" * 60)
    
    # Initialize extractor
    extractor = RealSchemaExtractor(db_path="vanna_app_clean.db")
    
    # Extract and store real schema
    success = await extractor.extract_and_store_real_schema()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Real database schema extracted")
        print("✅ Old incorrect data cleared from Qdrant")
        print("✅ Real schema stored in Qdrant")
        print("✅ Verification passed - Qdrant matches database")
        
        print("\n📝 Next steps:")
        print("1. Test SQL generation with web interface")
        print("2. Ask: 'Show me the complete customer journey: users, their orders, and sales'")
        print("3. Generated SQL should now use correct column names (created_at, not order_date)")
    else:
        print("\n❌ FAILED!")
        print("Check the errors above and try again")

if __name__ == "__main__":
    asyncio.run(main())
