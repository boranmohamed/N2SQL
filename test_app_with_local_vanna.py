#!/usr/bin/env python3
"""
Test script for Vanna AI application with local server integration.
Tests both basic and advanced SQL generation capabilities.
"""
import asyncio
import os
import time
from datetime import datetime
from typing import List, Dict, Any

# Set to use local Vanna server
os.environ["USE_LOCAL_VANNA"] = "true"

from loguru import logger
from app.infrastructure.vanna_factory import get_vanna_client_from_env

# Test queries organized by complexity
TEST_QUERIES = [
    # Basic Queries
    {
        "category": "Basic",
        "question": "Show me all users",
        "expected_keywords": ["SELECT", "users"]
    },
    {
        "category": "Basic", 
        "question": "How many users are there?",
        "expected_keywords": ["COUNT", "users"]
    },
    {
        "category": "Basic",
        "question": "List all employees",
        "expected_keywords": ["SELECT", "employees"]
    },
    
    # Filtering Queries
    {
        "category": "Filtering",
        "question": "Show me users with email containing 'gmail'",
        "expected_keywords": ["WHERE", "LIKE", "gmail"]
    },
    {
        "category": "Filtering",
        "question": "Find employees in the Engineering department",
        "expected_keywords": ["WHERE", "department", "Engineering"]
    },
    {
        "category": "Filtering",
        "question": "Show me active users only",
        "expected_keywords": ["WHERE", "is_active"]
    },
    
    # Aggregation Queries
    {
        "category": "Aggregation",
        "question": "What's the average salary by department?",
        "expected_keywords": ["AVG", "GROUP BY", "department"]
    },
    {
        "category": "Aggregation",
        "question": "Count employees by department",
        "expected_keywords": ["COUNT", "GROUP BY"]
    },
    {
        "category": "Aggregation",
        "question": "What's the total sales amount?",
        "expected_keywords": ["SUM", "amount"]
    },
    
    # Complex Joins
    {
        "category": "Joins",
        "question": "Show users with their order count",
        "expected_keywords": ["JOIN", "COUNT"]
    },
    {
        "category": "Joins",
        "question": "Find users who haven't placed any orders",
        "expected_keywords": ["LEFT JOIN", "IS NULL"]
    },
    {
        "category": "Joins",
        "question": "Show employees with their sales total",
        "expected_keywords": ["JOIN", "SUM"]
    },
    
    # Advanced Queries
    {
        "category": "Advanced",
        "question": "Show the top 5 customers by total order value",
        "expected_keywords": ["ORDER BY", "DESC", "LIMIT"]
    },
    {
        "category": "Advanced",
        "question": "Find orders placed in the last 30 days",
        "expected_keywords": ["WHERE", "date", "BETWEEN"]
    },
    {
        "category": "Advanced",
        "question": "Show monthly sales totals for this year",
        "expected_keywords": ["GROUP BY", "date", "YEAR"]
    },
    {
        "category": "Advanced",
        "question": "Find products with 'laptop' in the name",
        "expected_keywords": ["WHERE", "LIKE", "laptop"]
    }
]

class VannaAppTester:
    """Test suite for Vanna AI application with local server."""
    
    def __init__(self):
        """Initialize the tester."""
        self.client = None
        self.results = []
        self.start_time = None
        
    async def initialize(self) -> bool:
        """Initialize the Vanna client."""
        try:
            logger.info("🚀 Initializing Vanna AI Application Tester")
            logger.info("=" * 60)
            
            # Create client using factory
            self.client = get_vanna_client_from_env()
            logger.info(f"✅ Client created: {type(self.client).__name__}")
            
            # Initialize the client
            logger.info("🔄 Initializing client...")
            success = await self.client.initialize()
            
            if success:
                logger.info("✅ Client initialized successfully!")
                return True
            else:
                logger.error("❌ Failed to initialize client")
                return False
                
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def test_single_query(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single query and return results."""
        question = query_info["question"]
        category = query_info["category"]
        expected_keywords = query_info["expected_keywords"]
        
        start_time = time.time()
        
        try:
            logger.info(f"🔄 Testing: {category} - {question}")
            
            # Generate SQL
            sql = await self.client.generate_sql(question)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Check if expected keywords are present
            sql_lower = sql.lower()
            keywords_found = [kw.lower() for kw in expected_keywords if kw.lower() in sql_lower]
            keyword_score = (len(keywords_found) / len(expected_keywords)) * 100
            
            result = {
                "question": question,
                "category": category,
                "generated_sql": sql,
                "response_time": round(response_time, 2),
                "expected_keywords": expected_keywords,
                "keywords_found": keywords_found,
                "keyword_score": round(keyword_score, 1),
                "status": "Success",
                "error": None
            }
            
            logger.info(f"✅ Generated SQL in {response_time:.2f}s")
            logger.info(f"📝 SQL: {sql}")
            logger.info(f"🎯 Keyword Score: {keyword_score:.1f}%")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "question": question,
                "category": category,
                "generated_sql": "",
                "response_time": round(response_time, 2),
                "expected_keywords": expected_keywords,
                "keywords_found": [],
                "keyword_score": 0,
                "status": "Failed",
                "error": str(e)
            }
            
            logger.error(f"❌ Query failed: {e}")
            return result
    
    async def run_all_tests(self) -> None:
        """Run all test queries."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return
        
        self.start_time = time.time()
        logger.info("🧪 Starting comprehensive test suite")
        logger.info("=" * 60)
        
        for i, query_info in enumerate(TEST_QUERIES, 1):
            logger.info(f"\n📋 Test {i}/{len(TEST_QUERIES)}")
            result = await self.test_single_query(query_info)
            self.results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        self.end_time = time.time()
        logger.info("\n✅ All tests completed!")
    
    def print_summary(self) -> None:
        """Print test summary."""
        if not self.results:
            logger.error("❌ No test results to summarize")
            return
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["status"] == "Success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100
        
        avg_response_time = sum(r["response_time"] for r in self.results) / total_tests
        avg_keyword_score = sum(r["keyword_score"] for r in self.results) / total_tests
        
        total_duration = self.end_time - self.start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY REPORT")
        logger.info("=" * 60)
        logger.info(f"🎯 Total Tests: {total_tests}")
        logger.info(f"✅ Successful: {successful_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"⏱️  Avg Response Time: {avg_response_time:.2f}s")
        logger.info(f"🎯 Avg Keyword Score: {avg_keyword_score:.1f}%")
        logger.info(f"⏰ Total Duration: {total_duration:.2f}s")
        
        # Category breakdown
        logger.info("\n📋 Category Breakdown:")
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0}
            categories[cat]["total"] += 1
            if result["status"] == "Success":
                categories[cat]["success"] += 1
        
        for category, stats in categories.items():
            rate = (stats["success"] / stats["total"]) * 100
            logger.info(f"  {category}: {stats['success']}/{stats['total']} ({rate:.1f}%)")
        
        # Failed tests
        if failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for result in self.results:
                if result["status"] == "Failed":
                    logger.info(f"  - {result['question']}: {result['error']}")
        
        logger.info("=" * 60)
    
    async def close(self) -> None:
        """Close the client."""
        if self.client and hasattr(self.client, 'close'):
            await self.client.close()
        logger.info("🔒 Test client closed")

async def main():
    """Main test function."""
    tester = VannaAppTester()
    
    try:
        # Initialize
        if not await tester.initialize():
            logger.error("❌ Failed to initialize tester")
            return
        
        # Run tests
        await tester.run_all_tests()
        
        # Print summary
        tester.print_summary()
        
        logger.info("\n🎉 Testing completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
    
    finally:
        await tester.close()

if __name__ == "__main__":
    print("🧪 Vanna AI Application Test Suite")
    print("🏠 Testing with LOCAL Vanna Server")
    print("=" * 60)
    
    # Run the test suite
    asyncio.run(main())
