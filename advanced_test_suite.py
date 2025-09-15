#!/usr/bin/env python3
"""
Advanced Test Suite for Vanna AI Application
Comprehensive testing with Excel reporting and local Vanna server integration.
"""
import asyncio
import os
import time
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

# Set to use local Vanna server
os.environ["USE_LOCAL_VANNA"] = "true"

from loguru import logger
from app.infrastructure.vanna_factory import get_vanna_client_from_env
from app.infrastructure.database import db_manager, SQLiteDatabaseRepository

# Advanced Test Questions organized by complexity and category
ADVANCED_TEST_QUERIES = [
    # Basic Data Retrieval
    {
        "id": 1,
        "category": "Basic Retrieval",
        "complexity": "Beginner",
        "question": "Show me all users in the system",
        "expected_keywords": ["SELECT", "users"],
        "description": "Simple table selection"
    },
    {
        "id": 2,
        "category": "Basic Retrieval", 
        "complexity": "Beginner",
        "question": "How many total users do we have?",
        "expected_keywords": ["COUNT", "users"],
        "description": "Basic counting query"
    },
    {
        "id": 3,
        "category": "Basic Retrieval",
        "complexity": "Beginner", 
        "question": "List all employees with their basic information",
        "expected_keywords": ["SELECT", "employees"],
        "description": "Employee data retrieval"
    },
    
    # Filtering and Conditions
    {
        "id": 4,
        "category": "Filtering",
        "complexity": "Intermediate",
        "question": "Find all users whose email contains 'gmail.com'",
        "expected_keywords": ["WHERE", "LIKE", "gmail"],
        "description": "Pattern matching with LIKE"
    },
    {
        "id": 5,
        "category": "Filtering",
        "complexity": "Intermediate",
        "question": "Show me only active users",
        "expected_keywords": ["WHERE", "is_active", "true"],
        "description": "Boolean filtering"
    },
    {
        "id": 6,
        "category": "Filtering",
        "complexity": "Intermediate",
        "question": "Find employees in the Engineering department with salary above 75000",
        "expected_keywords": ["WHERE", "department", "salary", ">"],
        "description": "Multiple condition filtering"
    },
    {
        "id": 7,
        "category": "Filtering",
        "complexity": "Intermediate",
        "question": "Show users created in the last 30 days",
        "expected_keywords": ["WHERE", "created_at", "BETWEEN", "CURRENT_DATE"],
        "description": "Date range filtering"
    },
    
    # Aggregation and Grouping
    {
        "id": 8,
        "category": "Aggregation",
        "complexity": "Intermediate",
        "question": "What's the average salary by department?",
        "expected_keywords": ["AVG", "GROUP BY", "department"],
        "description": "Grouped aggregation"
    },
    {
        "id": 9,
        "category": "Aggregation",
        "complexity": "Intermediate",
        "question": "Count the number of employees in each department",
        "expected_keywords": ["COUNT", "GROUP BY", "department"],
        "description": "Grouped counting"
    },
    {
        "id": 10,
        "category": "Aggregation",
        "complexity": "Intermediate",
        "question": "Find the highest and lowest salary in each department",
        "expected_keywords": ["MAX", "MIN", "GROUP BY"],
        "description": "Multiple aggregations"
    },
    {
        "id": 11,
        "category": "Aggregation",
        "complexity": "Advanced",
        "question": "Show the total sales amount by month for this year",
        "expected_keywords": ["SUM", "GROUP BY", "MONTH", "YEAR"],
        "description": "Time-based aggregation"
    },
    
    # Joins and Relationships
    {
        "id": 12,
        "category": "Joins",
        "complexity": "Intermediate",
        "question": "Show users with their order count",
        "expected_keywords": ["JOIN", "COUNT", "orders"],
        "description": "Basic join with aggregation"
    },
    {
        "id": 13,
        "category": "Joins",
        "complexity": "Intermediate",
        "question": "Find users who haven't placed any orders",
        "expected_keywords": ["LEFT JOIN", "IS NULL"],
        "description": "Left join to find missing records"
    },
    {
        "id": 14,
        "category": "Joins",
        "complexity": "Advanced",
        "question": "Show employees with their department name and manager information",
        "expected_keywords": ["JOIN", "department", "manager"],
        "description": "Multiple table joins"
    },
    {
        "id": 15,
        "category": "Joins",
        "complexity": "Advanced",
        "question": "Find all products that have never been ordered",
        "expected_keywords": ["LEFT JOIN", "IS NULL", "products", "orders"],
        "description": "Complex join to find unused records"
    },
    
    # Sorting and Limiting
    {
        "id": 16,
        "category": "Sorting",
        "complexity": "Intermediate",
        "question": "Show the top 10 highest paid employees",
        "expected_keywords": ["ORDER BY", "DESC", "LIMIT", "salary"],
        "description": "Top N query with sorting"
    },
    {
        "id": 17,
        "category": "Sorting",
        "complexity": "Intermediate",
        "question": "List users ordered by creation date, newest first",
        "expected_keywords": ["ORDER BY", "DESC", "created_at"],
        "description": "Date-based sorting"
    },
    {
        "id": 18,
        "category": "Sorting",
        "complexity": "Advanced",
        "question": "Show the top 5 customers by total order value",
        "expected_keywords": ["ORDER BY", "DESC", "LIMIT", "SUM"],
        "description": "Complex sorting with aggregation"
    },
    
    # Subqueries and CTEs
    {
        "id": 19,
        "category": "Subqueries",
        "complexity": "Advanced",
        "question": "Find employees whose salary is above the average salary",
        "expected_keywords": ["WHERE", ">", "SELECT", "AVG"],
        "description": "Subquery with comparison"
    },
    {
        "id": 20,
        "category": "Subqueries",
        "complexity": "Advanced",
        "question": "Show departments that have more than 5 employees",
        "expected_keywords": ["HAVING", "COUNT", ">", "5"],
        "description": "Grouped filtering with HAVING"
    },
    {
        "id": 21,
        "category": "Subqueries",
        "complexity": "Expert",
        "question": "Find users who have ordered all available products",
        "expected_keywords": ["NOT EXISTS", "EXISTS", "products"],
        "description": "Complex subquery with EXISTS"
    },
    
    # Date and Time Functions
    {
        "id": 22,
        "category": "Date Functions",
        "complexity": "Intermediate",
        "question": "Show orders placed this month",
        "expected_keywords": ["WHERE", "MONTH", "CURRENT_DATE"],
        "description": "Current month filtering"
    },
    {
        "id": 23,
        "category": "Date Functions",
        "complexity": "Advanced",
        "question": "Find users who registered in the last quarter",
        "expected_keywords": ["WHERE", "QUARTER", "CURRENT_DATE"],
        "description": "Quarter-based filtering"
    },
    {
        "id": 24,
        "category": "Date Functions",
        "complexity": "Advanced",
        "question": "Show monthly sales totals for the past 12 months",
        "expected_keywords": ["GROUP BY", "MONTH", "YEAR", "BETWEEN"],
        "description": "Time series aggregation"
    },
    
    # String Functions
    {
        "id": 25,
        "category": "String Functions",
        "complexity": "Intermediate",
        "question": "Find users whose last name starts with 'S'",
        "expected_keywords": ["WHERE", "LIKE", "last_name", "S%"],
        "description": "Pattern matching with wildcards"
    },
    {
        "id": 26,
        "category": "String Functions",
        "complexity": "Intermediate",
        "question": "Show user names in uppercase",
        "expected_keywords": ["UPPER", "first_name", "last_name"],
        "description": "String transformation"
    },
    {
        "id": 27,
        "category": "String Functions",
        "complexity": "Advanced",
        "question": "Find products with 'laptop' or 'computer' in the name",
        "expected_keywords": ["WHERE", "LIKE", "OR", "laptop", "computer"],
        "description": "Multiple pattern matching"
    },
    
    # Window Functions
    {
        "id": 28,
        "category": "Window Functions",
        "complexity": "Expert",
        "question": "Rank employees by salary within each department",
        "expected_keywords": ["RANK", "OVER", "PARTITION BY", "ORDER BY"],
        "description": "Window function for ranking"
    },
    {
        "id": 29,
        "category": "Window Functions",
        "complexity": "Expert",
        "question": "Show each employee's salary and the average salary of their department",
        "expected_keywords": ["AVG", "OVER", "PARTITION BY"],
        "description": "Window function for comparison"
    },
    {
        "id": 30,
        "category": "Window Functions",
        "complexity": "Expert",
        "question": "Find the running total of sales by month",
        "expected_keywords": ["SUM", "OVER", "ORDER BY", "ROWS"],
        "description": "Running total calculation"
    },
    
    # Complex Business Logic
    {
        "id": 31,
        "category": "Business Logic",
        "complexity": "Expert",
        "question": "Find customers who have made purchases in at least 3 different months",
        "expected_keywords": ["GROUP BY", "HAVING", "COUNT", "DISTINCT", "MONTH"],
        "description": "Complex business rule validation"
    },
    {
        "id": 32,
        "category": "Business Logic",
        "complexity": "Expert",
        "question": "Show the percentage of total sales each product represents",
        "expected_keywords": ["SUM", "OVER", "/", "*", "100"],
        "description": "Percentage calculation with window functions"
    },
    {
        "id": 33,
        "category": "Business Logic",
        "complexity": "Expert",
        "question": "Find the top 3 products by sales in each category",
        "expected_keywords": ["ROW_NUMBER", "OVER", "PARTITION BY", "ORDER BY", "DESC"],
        "description": "Top N per group query"
    },
    
    # Error Handling and Edge Cases
    {
        "id": 34,
        "category": "Edge Cases",
        "complexity": "Intermediate",
        "question": "Show all users including those with NULL email addresses",
        "expected_keywords": ["SELECT", "users", "email"],
        "description": "Handling NULL values"
    },
    {
        "id": 35,
        "category": "Edge Cases",
        "complexity": "Advanced",
        "question": "Find duplicate email addresses in the users table",
        "expected_keywords": ["GROUP BY", "HAVING", "COUNT", ">", "1"],
        "description": "Duplicate detection"
    },
    {
        "id": 36,
        "category": "Edge Cases",
        "complexity": "Advanced",
        "question": "Show products with no sales in the last 6 months",
        "expected_keywords": ["LEFT JOIN", "IS NULL", "WHERE", "BETWEEN"],
        "description": "Complex business logic with time constraints"
    },
    
    # Performance and Optimization
    {
        "id": 37,
        "category": "Performance",
        "complexity": "Advanced",
        "question": "Find the 100 most recent orders with customer information",
        "expected_keywords": ["JOIN", "ORDER BY", "DESC", "LIMIT", "100"],
        "description": "Large dataset query with joins"
    },
    {
        "id": 38,
        "category": "Performance",
        "complexity": "Expert",
        "question": "Calculate the total revenue by year and month for the past 5 years",
        "expected_keywords": ["SUM", "GROUP BY", "YEAR", "MONTH", "BETWEEN"],
        "description": "Large time series aggregation"
    },
    
    # Data Quality and Validation
    {
        "id": 39,
        "category": "Data Quality",
        "complexity": "Intermediate",
        "question": "Find users with invalid email formats",
        "expected_keywords": ["WHERE", "NOT", "LIKE", "@", "."],
        "description": "Data validation query"
    },
    {
        "id": 40,
        "category": "Data Quality",
        "complexity": "Advanced",
        "question": "Show orders with missing or invalid customer references",
        "expected_keywords": ["LEFT JOIN", "IS NULL", "orders", "customers"],
        "description": "Referential integrity check"
    }
]

class AdvancedVannaTester:
    """Advanced test suite for Vanna AI application with comprehensive reporting."""
    
    def __init__(self):
        """Initialize the advanced tester."""
        self.client = None
        self.db_repo = None
        self.results = []
        self.start_time = None
        self.end_time = None
        self.test_metadata = {
            "test_suite_version": "2.0.0",
            "total_questions": len(ADVANCED_TEST_QUERIES),
            "categories": list(set(q["category"] for q in ADVANCED_TEST_QUERIES)),
            "complexity_levels": list(set(q["complexity"] for q in ADVANCED_TEST_QUERIES))
        }
        
    async def initialize(self) -> bool:
        """Initialize the Vanna client and database connection."""
        try:
            logger.info("🚀 Initializing Advanced Vanna AI Test Suite")
            logger.info("=" * 80)
            
            # Create Vanna client
            self.client = get_vanna_client_from_env()
            logger.info(f"✅ Vanna client created: {type(self.client).__name__}")
            
            # Initialize Vanna client
            logger.info("🔄 Initializing Vanna client...")
            vanna_success = await self.client.initialize()
            
            if not vanna_success:
                logger.error("❌ Failed to initialize Vanna client")
                return False
                
            logger.info("✅ Vanna client initialized successfully!")
            
            # Initialize database repository
            logger.info("🔄 Initializing database connection...")
            self.db_repo = SQLiteDatabaseRepository(db_manager)
            await self.db_repo.check_connection()
            logger.info("✅ Database connection established!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def test_single_query(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single query and return comprehensive results."""
        question = query_info["question"]
        category = query_info["category"]
        complexity = query_info["complexity"]
        expected_keywords = query_info["expected_keywords"]
        description = query_info["description"]
        query_id = query_info["id"]
        
        start_time = time.time()
        sql_generation_time = 0
        execution_time = 0
        execution_success = False
        execution_error = None
        result_count = 0
        execution_results = None
        
        try:
            logger.info(f"🔄 Testing Query {query_id}: {category} - {complexity}")
            logger.info(f"   Question: {question}")
            
            # Generate SQL
            sql_start = time.time()
            sql = await self.client.generate_sql(question)
            sql_end = time.time()
            sql_generation_time = sql_end - sql_start
            
            logger.info(f"✅ SQL generated in {sql_generation_time:.2f}s")
            logger.info(f"📝 Generated SQL: {sql}")
            
            # Try to execute the SQL
            try:
                exec_start = time.time()
                execution_results = await self.db_repo.execute_query(sql)
                exec_end = time.time()
                execution_time = exec_end - exec_start
                execution_success = True
                result_count = len(execution_results) if execution_results else 0
                logger.info(f"✅ SQL executed successfully in {execution_time:.2f}s")
                logger.info(f"📊 Returned {result_count} rows")
            except Exception as exec_e:
                execution_error = str(exec_e)
                logger.warning(f"⚠️ SQL execution failed: {execution_error}")
            
            # Analyze SQL quality
            sql_lower = sql.lower()
            keywords_found = [kw.lower() for kw in expected_keywords if kw.lower() in sql_lower]
            keyword_score = (len(keywords_found) / len(expected_keywords)) * 100 if expected_keywords else 100
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(
                keyword_score, execution_success, sql_generation_time, execution_time
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            result = {
                "query_id": query_id,
                "question": question,
                "category": category,
                "complexity": complexity,
                "description": description,
                "generated_sql": sql,
                "expected_keywords": expected_keywords,
                "keywords_found": keywords_found,
                "keyword_score": round(keyword_score, 1),
                "sql_generation_time": round(sql_generation_time, 3),
                "execution_time": round(execution_time, 3),
                "total_time": round(total_time, 3),
                "execution_success": execution_success,
                "execution_error": execution_error,
                "result_count": result_count,
                "execution_results": execution_results[:5] if execution_results else None,  # First 5 rows
                "quality_score": round(quality_score, 1),
                "status": "Success" if execution_success else "Partial Success",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"🎯 Quality Score: {quality_score:.1f}/100")
            logger.info(f"📈 Keyword Score: {keyword_score:.1f}%")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            total_time = end_time - start_time
            
            result = {
                "query_id": query_id,
                "question": question,
                "category": category,
                "complexity": complexity,
                "description": description,
                "generated_sql": "",
                "expected_keywords": expected_keywords,
                "keywords_found": [],
                "keyword_score": 0,
                "sql_generation_time": 0,
                "execution_time": 0,
                "total_time": round(total_time, 3),
                "execution_success": False,
                "execution_error": str(e),
                "result_count": 0,
                "execution_results": None,
                "quality_score": 0,
                "status": "Failed",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.error(f"❌ Query {query_id} failed: {e}")
            return result
    
    def _calculate_quality_score(self, keyword_score: float, execution_success: bool, 
                                sql_time: float, exec_time: float) -> float:
        """Calculate overall quality score for a query result."""
        # Base score from keyword matching
        base_score = keyword_score * 0.4
        
        # Execution success bonus
        execution_bonus = 30 if execution_success else 0
        
        # Performance bonus (faster is better)
        time_penalty = 0
        if sql_time > 5:  # SQL generation taking too long
            time_penalty += 10
        if exec_time > 10:  # Execution taking too long
            time_penalty += 10
        
        # Cap the score at 100
        total_score = min(100, base_score + execution_bonus - time_penalty)
        return max(0, total_score)
    
    async def run_all_tests(self) -> None:
        """Run all test queries with progress tracking."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return
        
        self.start_time = time.time()
        logger.info("🧪 Starting Advanced Test Suite")
        logger.info(f"📊 Total Questions: {len(ADVANCED_TEST_QUERIES)}")
        logger.info("=" * 80)
        
        for i, query_info in enumerate(ADVANCED_TEST_QUERIES, 1):
            logger.info(f"\n📋 Test {i}/{len(ADVANCED_TEST_QUERIES)}")
            result = await self.test_single_query(query_info)
            self.results.append(result)
            
            # Progress update every 10 tests
            if i % 10 == 0:
                completed = len([r for r in self.results if r["status"] in ["Success", "Partial Success"]])
                logger.info(f"📈 Progress: {i}/{len(ADVANCED_TEST_QUERIES)} completed, {completed} successful")
            
            # Small delay between tests to avoid overwhelming the system
            await asyncio.sleep(0.2)
        
        self.end_time = time.time()
        logger.info("\n✅ All tests completed!")
    
    def generate_excel_report(self, filename: str = None) -> str:
        """Generate comprehensive Excel report with all test results."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vanna_advanced_test_results_{timestamp}.xlsx"
        
        try:
            logger.info(f"📊 Generating Excel report: {filename}")
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main Results Sheet
                df_results = pd.DataFrame(self.results)
                df_results.to_excel(writer, sheet_name='Test Results', index=False)
                
                # Summary Statistics
                summary_data = self._generate_summary_data()
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                
                # Category Analysis
                category_data = self._generate_category_analysis()
                df_category = pd.DataFrame(category_data)
                df_category.to_excel(writer, sheet_name='Category Analysis', index=False)
                
                # Complexity Analysis
                complexity_data = self._generate_complexity_analysis()
                df_complexity = pd.DataFrame(complexity_data)
                df_complexity.to_excel(writer, sheet_name='Complexity Analysis', index=False)
                
                # Performance Metrics
                performance_data = self._generate_performance_metrics()
                df_performance = pd.DataFrame(performance_data)
                df_performance.to_excel(writer, sheet_name='Performance', index=False)
                
                # Failed Tests Details
                failed_tests = [r for r in self.results if r["status"] == "Failed"]
                if failed_tests:
                    df_failed = pd.DataFrame(failed_tests)
                    df_failed.to_excel(writer, sheet_name='Failed Tests', index=False)
                
                # Test Metadata
                metadata = {
                    'Metric': ['Test Suite Version', 'Total Questions', 'Test Date', 'Duration (seconds)'],
                    'Value': [
                        self.test_metadata['test_suite_version'],
                        self.test_metadata['total_questions'],
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        round(self.end_time - self.start_time, 2) if self.end_time else 0
                    ]
                }
                df_metadata = pd.DataFrame(metadata)
                df_metadata.to_excel(writer, sheet_name='Metadata', index=False)
            
            logger.info(f"✅ Excel report generated successfully: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Failed to generate Excel report: {e}")
            raise
    
    def _generate_summary_data(self) -> List[Dict[str, Any]]:
        """Generate summary statistics."""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["status"] == "Success"])
        partial_success = len([r for r in self.results if r["status"] == "Partial Success"])
        failed_tests = len([r for r in self.results if r["status"] == "Failed"])
        
        avg_quality_score = sum(r["quality_score"] for r in self.results) / total_tests if total_tests > 0 else 0
        avg_sql_time = sum(r["sql_generation_time"] for r in self.results) / total_tests if total_tests > 0 else 0
        avg_exec_time = sum(r["execution_time"] for r in self.results) / total_tests if total_tests > 0 else 0
        
        return [
            {"Metric": "Total Tests", "Value": total_tests},
            {"Metric": "Successful Tests", "Value": successful_tests},
            {"Metric": "Partial Success", "Value": partial_success},
            {"Metric": "Failed Tests", "Value": failed_tests},
            {"Metric": "Success Rate (%)", "Value": round((successful_tests / total_tests) * 100, 1) if total_tests > 0 else 0},
            {"Metric": "Overall Success Rate (%)", "Value": round(((successful_tests + partial_success) / total_tests) * 100, 1) if total_tests > 0 else 0},
            {"Metric": "Average Quality Score", "Value": round(avg_quality_score, 1)},
            {"Metric": "Average SQL Generation Time (s)", "Value": round(avg_sql_time, 3)},
            {"Metric": "Average Execution Time (s)", "Value": round(avg_exec_time, 3)},
            {"Metric": "Total Duration (s)", "Value": round(self.end_time - self.start_time, 2) if self.end_time else 0}
        ]
    
    def _generate_category_analysis(self) -> List[Dict[str, Any]]:
        """Generate category-wise analysis."""
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0, "partial": 0, "failed": 0, "avg_quality": 0, "quality_scores": []}
            
            categories[cat]["total"] += 1
            categories[cat]["quality_scores"].append(result["quality_score"])
            
            if result["status"] == "Success":
                categories[cat]["success"] += 1
            elif result["status"] == "Partial Success":
                categories[cat]["partial"] += 1
            else:
                categories[cat]["failed"] += 1
        
        # Calculate averages
        for cat_data in categories.values():
            cat_data["avg_quality"] = sum(cat_data["quality_scores"]) / len(cat_data["quality_scores"])
            cat_data["success_rate"] = (cat_data["success"] / cat_data["total"]) * 100
            cat_data["overall_success_rate"] = ((cat_data["success"] + cat_data["partial"]) / cat_data["total"]) * 100
        
        return [
            {
                "Category": cat,
                "Total Tests": data["total"],
                "Successful": data["success"],
                "Partial Success": data["partial"],
                "Failed": data["failed"],
                "Success Rate (%)": round(data["success_rate"], 1),
                "Overall Success Rate (%)": round(data["overall_success_rate"], 1),
                "Average Quality Score": round(data["avg_quality"], 1)
            }
            for cat, data in categories.items()
        ]
    
    def _generate_complexity_analysis(self) -> List[Dict[str, Any]]:
        """Generate complexity-wise analysis."""
        complexities = {}
        for result in self.results:
            comp = result["complexity"]
            if comp not in complexities:
                complexities[comp] = {"total": 0, "success": 0, "partial": 0, "failed": 0, "avg_quality": 0, "quality_scores": []}
            
            complexities[comp]["total"] += 1
            complexities[comp]["quality_scores"].append(result["quality_score"])
            
            if result["status"] == "Success":
                complexities[comp]["success"] += 1
            elif result["status"] == "Partial Success":
                complexities[comp]["partial"] += 1
            else:
                complexities[comp]["failed"] += 1
        
        # Calculate averages
        for comp_data in complexities.values():
            comp_data["avg_quality"] = sum(comp_data["quality_scores"]) / len(comp_data["quality_scores"])
            comp_data["success_rate"] = (comp_data["success"] / comp_data["total"]) * 100
            comp_data["overall_success_rate"] = ((comp_data["success"] + comp_data["partial"]) / comp_data["total"]) * 100
        
        return [
            {
                "Complexity": comp,
                "Total Tests": data["total"],
                "Successful": data["success"],
                "Partial Success": data["partial"],
                "Failed": data["failed"],
                "Success Rate (%)": round(data["success_rate"], 1),
                "Overall Success Rate (%)": round(data["overall_success_rate"], 1),
                "Average Quality Score": round(data["avg_quality"], 1)
            }
            for comp, data in complexities.items()
        ]
    
    def _generate_performance_metrics(self) -> List[Dict[str, Any]]:
        """Generate performance metrics."""
        sql_times = [r["sql_generation_time"] for r in self.results]
        exec_times = [r["execution_time"] for r in self.results]
        total_times = [r["total_time"] for r in self.results]
        
        return [
            {"Metric": "SQL Generation - Min Time (s)", "Value": round(min(sql_times), 3)},
            {"Metric": "SQL Generation - Max Time (s)", "Value": round(max(sql_times), 3)},
            {"Metric": "SQL Generation - Average Time (s)", "Value": round(sum(sql_times) / len(sql_times), 3)},
            {"Metric": "Execution - Min Time (s)", "Value": round(min(exec_times), 3)},
            {"Metric": "Execution - Max Time (s)", "Value": round(max(exec_times), 3)},
            {"Metric": "Execution - Average Time (s)", "Value": round(sum(exec_times) / len(exec_times), 3)},
            {"Metric": "Total - Min Time (s)", "Value": round(min(total_times), 3)},
            {"Metric": "Total - Max Time (s)", "Value": round(max(total_times), 3)},
            {"Metric": "Total - Average Time (s)", "Value": round(sum(total_times) / len(total_times), 3)},
        ]
    
    def print_summary(self) -> None:
        """Print comprehensive test summary."""
        if not self.results:
            logger.error("❌ No test results to summarize")
            return
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["status"] == "Success"])
        partial_success = len([r for r in self.results if r["status"] == "Partial Success"])
        failed_tests = len([r for r in self.results if r["status"] == "Failed"])
        
        success_rate = (successful_tests / total_tests) * 100
        overall_success_rate = ((successful_tests + partial_success) / total_tests) * 100
        
        avg_quality_score = sum(r["quality_score"] for r in self.results) / total_tests
        avg_sql_time = sum(r["sql_generation_time"] for r in self.results) / total_tests
        avg_exec_time = sum(r["execution_time"] for r in self.results) / total_tests
        
        total_duration = self.end_time - self.start_time if self.end_time else 0
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 ADVANCED TEST SUITE SUMMARY REPORT")
        logger.info("=" * 80)
        logger.info(f"🎯 Total Tests: {total_tests}")
        logger.info(f"✅ Successful: {successful_tests}")
        logger.info(f"⚠️  Partial Success: {partial_success}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"📈 Overall Success Rate: {overall_success_rate:.1f}%")
        logger.info(f"🎯 Average Quality Score: {avg_quality_score:.1f}/100")
        logger.info(f"⏱️  Average SQL Generation Time: {avg_sql_time:.3f}s")
        logger.info(f"⏱️  Average Execution Time: {avg_exec_time:.3f}s")
        logger.info(f"⏰ Total Duration: {total_duration:.2f}s")
        
        # Category breakdown
        logger.info("\n📋 Category Breakdown:")
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0, "partial": 0}
            categories[cat]["total"] += 1
            if result["status"] == "Success":
                categories[cat]["success"] += 1
            elif result["status"] == "Partial Success":
                categories[cat]["partial"] += 1
        
        for category, stats in categories.items():
            rate = ((stats["success"] + stats["partial"]) / stats["total"]) * 100
            logger.info(f"  {category}: {stats['success'] + stats['partial']}/{stats['total']} ({rate:.1f}%)")
        
        # Complexity breakdown
        logger.info("\n🎚️ Complexity Breakdown:")
        complexities = {}
        for result in self.results:
            comp = result["complexity"]
            if comp not in complexities:
                complexities[comp] = {"total": 0, "success": 0, "partial": 0}
            complexities[comp]["total"] += 1
            if result["status"] == "Success":
                complexities[comp]["success"] += 1
            elif result["status"] == "Partial Success":
                complexities[comp]["partial"] += 1
        
        for complexity, stats in complexities.items():
            rate = ((stats["success"] + stats["partial"]) / stats["total"]) * 100
            logger.info(f"  {complexity}: {stats['success'] + stats['partial']}/{stats['total']} ({rate:.1f}%)")
        
        logger.info("=" * 80)
    
    async def close(self) -> None:
        """Close the client and cleanup."""
        if self.client and hasattr(self.client, 'close'):
            await self.client.close()
        logger.info("🔒 Test client closed")

async def main():
    """Main test function."""
    tester = AdvancedVannaTester()
    
    try:
        # Initialize
        if not await tester.initialize():
            logger.error("❌ Failed to initialize tester")
            return
        
        # Run tests
        await tester.run_all_tests()
        
        # Print summary
        tester.print_summary()
        
        # Generate Excel report
        excel_file = tester.generate_excel_report()
        logger.info(f"📊 Excel report saved: {excel_file}")
        
        logger.info("\n🎉 Advanced testing completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
    
    finally:
        await tester.close()

if __name__ == "__main__":
    print("🧪 Advanced Vanna AI Test Suite v2.0")
    print("🏠 Testing with LOCAL Vanna Server")
    print("📊 Comprehensive Excel Reporting")
    print("=" * 80)
    
    # Run the advanced test suite
    asyncio.run(main())
