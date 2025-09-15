#!/usr/bin/env python3
"""
Visual Web Interface for Testing Local Vanna Server
A simple Flask web app for interactive testing of natural language to SQL queries.
"""
import os
import asyncio
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional

# Set to use local Vanna server
os.environ["USE_LOCAL_VANNA"] = "true"

from flask import Flask, render_template, request, jsonify, redirect, url_for
from loguru import logger

from app.infrastructure.vanna_factory import get_vanna_client_from_env

app = Flask(__name__)
app.secret_key = 'vanna_test_interface_2024'

# Global client instance
vanna_client = None
db_path = "vanna_app_clean.db"  # Your database path

class VannaTester:
    """Handles Vanna AI operations for the web interface."""
    
    def __init__(self):
        self.client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the Vanna client."""
        try:
            self.client = get_vanna_client_from_env()
            success = await self.client.initialize()
            if success:
                self.initialized = True
                logger.info("✅ Vanna client initialized for web interface")
            else:
                logger.error("❌ Failed to initialize Vanna client")
        except Exception as e:
            logger.error(f"❌ Vanna client initialization error: {e}")
    
    def generate_sql_sync(self, question: str) -> Dict[str, Any]:
        """Generate SQL from natural language question (synchronous wrapper)."""
        if not self.initialized:
            return {
                "success": False,
                "error": f"Vanna client not initialized. Client exists: {self.client is not None}, Initialized: {self.initialized}"
            }
        
        try:
            start_time = datetime.now()
            
            # Run the async method in a new event loop
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                sql = loop.run_until_complete(self.client.generate_sql(question))
            finally:
                loop.close()
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "question": question,
                "sql": sql,
                "response_time": round(response_time, 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question": question,
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query against the database."""
        try:
            # Connect to database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            
            # Try to fix common SQLite compatibility issues
            fixed_sql = self._fix_sqlite_compatibility(sql)
            
            # Execute query
            df = pd.read_sql_query(fixed_sql, conn)
            conn.close()
            
            # Convert to dict for JSON response
            result_data = {
                "success": True,
                "sql": fixed_sql,
                "original_sql": sql,
                "row_count": len(df),
                "columns": list(df.columns),
                "data": df.to_dict('records'),
                "timestamp": datetime.now().isoformat()
            }
            
            return result_data
            
        except Exception as e:
            # If fixed SQL also fails, try with original
            if fixed_sql != sql:
                try:
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    df = pd.read_sql_query(sql, conn)
                    conn.close()
                    
                    return {
                        "success": True,
                        "sql": sql,
                        "original_sql": sql,
                        "row_count": len(df),
                        "columns": list(df.columns),
                        "data": df.to_dict('records'),
                        "timestamp": datetime.now().isoformat()
                    }
                except:
                    pass
            
            return {
                "success": False,
                "error": str(e),
                "sql": sql,
                "fixed_sql": fixed_sql if fixed_sql != sql else None,
                "timestamp": datetime.now().isoformat()
            }
    
    def _fix_sqlite_compatibility(self, sql: str) -> str:
        """Fix common SQL compatibility issues for SQLite."""
        import re
        
        # Replace EXTRACT(MONTH FROM date) with strftime('%m', date)
        sql = re.sub(r"EXTRACT\(MONTH FROM ([^)]+)\)", r"CAST(strftime('%m', \1) AS INTEGER)", sql, flags=re.IGNORECASE)
        
        # Replace EXTRACT(YEAR FROM date) with strftime('%Y', date)
        sql = re.sub(r"EXTRACT\(YEAR FROM ([^)]+)\)", r"CAST(strftime('%Y', \1) AS INTEGER)", sql, flags=re.IGNORECASE)
        
        # Replace EXTRACT(DAY FROM date) with strftime('%d', date)
        sql = re.sub(r"EXTRACT\(DAY FROM ([^)]+)\)", r"CAST(strftime('%d', \1) AS INTEGER)", sql, flags=re.IGNORECASE)
        
        # Replace CURRENT_DATE with date('now')
        sql = re.sub(r"CURRENT_DATE", r"date('now')", sql, flags=re.IGNORECASE)
        
        # Replace CURRENT_TIMESTAMP with datetime('now')
        sql = re.sub(r"CURRENT_TIMESTAMP", r"datetime('now')", sql, flags=re.IGNORECASE)
        
        # Replace NOW() with datetime('now')
        sql = re.sub(r"NOW\(\)", r"datetime('now')", sql, flags=re.IGNORECASE)
        
        # Replace DATE_FORMAT with strftime
        sql = re.sub(r"DATE_FORMAT\(([^,]+),\s*'([^']+)'\)", r"strftime('\2', \1)", sql, flags=re.IGNORECASE)
        
        # Replace YEAR() function with strftime
        sql = re.sub(r"YEAR\(([^)]+)\)", r"CAST(strftime('%Y', \1) AS INTEGER)", sql, flags=re.IGNORECASE)
        
        # Replace MONTH() function with strftime
        sql = re.sub(r"MONTH\(([^)]+)\)", r"CAST(strftime('%m', \1) AS INTEGER)", sql, flags=re.IGNORECASE)
        
        # Replace DAY() function with strftime
        sql = re.sub(r"DAY\(([^)]+)\)", r"CAST(strftime('%d', \1) AS INTEGER)", sql, flags=re.IGNORECASE)
        
        return sql

# Initialize the tester
tester = VannaTester()

@app.route('/')
def index():
    """Main page with the testing interface."""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_sql():
    """API endpoint to generate SQL from natural language."""
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    # Use the synchronous wrapper method
    result = tester.generate_sql_sync(question)
    return jsonify(result)

@app.route('/api/execute', methods=['POST'])
def execute_sql():
    """API endpoint to execute SQL and return results."""
    data = request.get_json()
    sql = data.get('sql', '').strip()
    
    if not sql:
        return jsonify({"error": "SQL is required"}), 400
    
    result = tester.execute_sql(sql)
    return jsonify(result)

@app.route('/api/status')
def get_status():
    """Get the status of the Vanna client."""
    # Check if local server is accessible
    server_status = "Unknown"
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            server_status = "Running"
        else:
            server_status = "Not responding"
    except:
        server_status = "Not accessible"
    
    return jsonify({
        "initialized": tester.initialized,
        "client_type": type(tester.client).__name__ if tester.client else None,
        "database_path": db_path,
        "server_status": server_status,
        "status": "Connected" if tester.initialized else "Not Connected"
    })

@app.route('/api/sample-queries')
def get_sample_queries():
    """Get sample queries for testing."""
    samples = [
        "Show me all users",
        "How many employees are there?",
        "Find users with email containing 'gmail'",
        "What's the average salary by department?",
        "Show me users with their order count",
        "Find the top 5 customers by total order value",
        "Show employees in the Engineering department",
        "List all pending orders",
        "What's the total sales amount?",
        "Find users who haven't placed any orders"
    ]
    return jsonify({"queries": samples})

@app.route('/api/reinitialize', methods=['POST'])
def reinitialize():
    """Reinitialize the Vanna client."""
    try:
        initialize_tester()
        return jsonify({
            "success": True,
            "message": "Client reinitialized successfully" if tester.initialized else "Client initialization failed"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def initialize_tester():
    """Initialize the tester synchronously."""
    try:
        print("🔄 Initializing Vanna client...")
        # Set environment variable for local Vanna
        os.environ["USE_LOCAL_VANNA"] = "true"
        
        # Create client directly
        tester.client = get_vanna_client_from_env()
        print(f"✅ Client created: {type(tester.client).__name__}")
        
        # Initialize synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(tester.client.initialize())
            if success:
                tester.initialized = True
                print("✅ Vanna client initialized successfully")
            else:
                print("❌ Failed to initialize Vanna client")
        finally:
            loop.close()
            
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🌐 Starting Vanna Visual Tester Web Interface")
    print("=" * 60)
    
    # Initialize the tester
    initialize_tester()
    
    print("🚀 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
