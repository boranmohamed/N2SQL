#!/usr/bin/env python3
"""
Demo script for the Vanna AI Web Application.
This script demonstrates how to use the application programmatically.
"""
import asyncio
import json
from typing import Dict, Any

import httpx


class VannaAIDemo:
    """Demo class for showcasing Vanna AI Web Application features."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the demo with the application base URL."""
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def check_health(self) -> Dict[str, Any]:
        """Check the application health."""
        print("🔍 Checking application health...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            health_data = response.json()
            
            print(f"✅ Health Status: {health_data['status']}")
            print(f"📊 Database Connected: {health_data['database_connected']}")
            print(f"🤖 Vanna AI Connected: {health_data['vanna_connected']}")
            print(f"⏱️  Uptime: {health_data['uptime_seconds']:.2f} seconds")
            
            return health_data
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {}
    
    async def process_query(self, question: str, user_id: str = None) -> Dict[str, Any]:
        """Process a natural language query."""
        print(f"\n🤔 Processing query: '{question}'")
        
        try:
            payload = {"question": question}
            if user_id:
                payload["user_id"] = user_id
            
            response = await self.client.post(
                f"{self.base_url}/query",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"🔍 Generated SQL: {result['sql_query']}")
            print(f"📊 Results: {len(result['results'])} rows")
            print(f"⏱️  Execution Time: {result['execution_time_ms']:.2f} ms")
            
            if result['results']:
                print("📋 Sample Results:")
                for i, row in enumerate(result['results'][:3]):  # Show first 3 results
                    print(f"   Row {i+1}: {row}")
            
            if result['error_message']:
                print(f"⚠️  Error: {result['error_message']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Query processing failed: {e}")
            return {}
    
    async def run_demo_queries(self) -> None:
        """Run a series of demo queries."""
        print("\n🚀 Running Demo Queries")
        print("=" * 50)
        
        demo_questions = [
            "How many users are there?",
            "Show me all employees in the Engineering department",
            "What's the average salary?",
            "List recent sales over $100",
            "How many orders are pending?",
            "Show me the top 3 highest paid employees",
            "What products were sold yesterday?",
            "Give me a summary of all departments"
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n--- Demo Query {i} ---")
            await self.process_query(question, f"demo_user_{i}")
            await asyncio.sleep(1)  # Small delay between queries
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def run_full_demo(self) -> None:
        """Run the complete demo."""
        print("🎯 Vanna AI Web Application Demo")
        print("=" * 50)
        
        try:
            # Check health
            await self.check_health()
            
            # Run demo queries
            await self.run_demo_queries()
            
            print("\n🎉 Demo completed successfully!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        finally:
            await self.close()


async def main():
    """Main function to run the demo."""
    demo = VannaAIDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
