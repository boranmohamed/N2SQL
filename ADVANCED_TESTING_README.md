# Advanced Vanna AI Test Suite

A comprehensive testing framework for the Vanna AI application that generates advanced SQL test questions, runs them through the local Vanna server, and produces detailed Excel reports.

## 🎯 Features

- **40 Advanced Test Questions** covering various SQL scenarios and complexity levels
- **Automated Test Execution** with local Vanna server integration
- **Comprehensive Excel Reporting** with multiple analysis sheets
- **Real-time Performance Monitoring** and quality scoring
- **RAG-Enhanced Context** for better SQL generation
- **Detailed Error Tracking** and execution results

## 📊 Test Categories

### Basic Retrieval (3 tests)
- Simple table selections
- Basic counting queries
- Employee data retrieval

### Filtering (4 tests)
- Pattern matching with LIKE
- Boolean filtering
- Multiple condition filtering
- Date range filtering

### Aggregation (4 tests)
- Grouped aggregation
- Grouped counting
- Multiple aggregations
- Time-based aggregation

### Joins (4 tests)
- Basic join with aggregation
- Left join to find missing records
- Multiple table joins
- Complex join to find unused records

### Sorting (3 tests)
- Top N queries with sorting
- Date-based sorting
- Complex sorting with aggregation

### Subqueries (3 tests)
- Subquery with comparison
- Grouped filtering with HAVING
- Complex subquery with EXISTS

### Date Functions (3 tests)
- Current month filtering
- Quarter-based filtering
- Time series aggregation

### String Functions (3 tests)
- Pattern matching with wildcards
- String transformation
- Multiple pattern matching

### Window Functions (3 tests)
- Window function for ranking
- Window function for comparison
- Running total calculation

### Business Logic (3 tests)
- Complex business rule validation
- Percentage calculation with window functions
- Top N per group query

### Edge Cases (3 tests)
- Handling NULL values
- Duplicate detection
- Complex business logic with time constraints

### Performance (2 tests)
- Large dataset query with joins
- Large time series aggregation

### Data Quality (2 tests)
- Data validation query
- Referential integrity check

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Local Vanna server running
- Required dependencies installed

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure local Vanna server is running
# (Follow your local Vanna setup instructions)
```

### Running Tests

#### Option 1: Direct execution
```bash
python advanced_test_suite.py
```

#### Option 2: Using the runner script
```bash
python run_advanced_tests.py
```

### Expected Output
- Console logs showing test progress
- Detailed summary report
- Excel file with comprehensive results

## 📈 Test Results

The test suite generates an Excel file with the following sheets:

### 1. Test Results
- Complete test data for all 40 questions
- Generated SQL queries
- Execution results and performance metrics
- Quality scores and error details

### 2. Summary
- Overall statistics
- Success rates
- Performance metrics
- Test duration

### 3. Category Analysis
- Performance breakdown by test category
- Success rates per category
- Average quality scores

### 4. Complexity Analysis
- Performance breakdown by complexity level
- Success rates per complexity
- Quality score analysis

### 5. Performance
- SQL generation time metrics
- Execution time metrics
- Total time analysis

### 6. Failed Tests (if any)
- Details of any failed tests
- Error messages and debugging information

### 7. Metadata
- Test suite version
- Test execution details
- System information

## 🎯 Quality Scoring

The test suite uses a sophisticated quality scoring system:

- **Keyword Matching (40%)**: How well the generated SQL matches expected keywords
- **Execution Success (30%)**: Whether the SQL executes successfully
- **Performance Bonus**: Faster execution gets higher scores
- **Time Penalties**: Slow queries get penalized

## 📊 Sample Results

Based on the latest test run:

- **Total Tests**: 40
- **Success Rate**: 80.0%
- **Overall Success Rate**: 100.0% (including partial success)
- **Average Quality Score**: 53.6/100
- **Average SQL Generation Time**: 3.592s
- **Average Execution Time**: 0.010s
- **Total Duration**: 152.85s

## 🔧 Configuration

### Environment Variables
- `USE_LOCAL_VANNA=true`: Enables local Vanna server mode
- Database connection settings (configured in your app)

### Test Customization
You can modify the test questions in `advanced_test_suite.py`:
- Add new test categories
- Modify existing questions
- Adjust expected keywords
- Change complexity levels

## 🐛 Troubleshooting

### Common Issues

1. **Local Vanna Server Not Running**
   - Ensure the local Vanna server is started
   - Check server health endpoint

2. **Database Connection Issues**
   - Verify database file exists
   - Check database permissions

3. **RAG System Issues**
   - Ensure Qdrant is running
   - Check vector database initialization

4. **Excel Generation Errors**
   - Install openpyxl: `pip install openpyxl`
   - Check file permissions

### Debug Mode
Enable detailed logging by modifying the log level in the test suite.

## 📝 Adding New Tests

To add new test questions:

1. Open `advanced_test_suite.py`
2. Add new entries to `ADVANCED_TEST_QUERIES`
3. Include required fields:
   - `id`: Unique identifier
   - `category`: Test category
   - `complexity`: Beginner/Intermediate/Advanced/Expert
   - `question`: Natural language question
   - `expected_keywords`: List of expected SQL keywords
   - `description`: Test description

## 🎉 Success Metrics

A successful test run should show:
- High success rate (>80%)
- Good quality scores (>50%)
- Fast execution times
- Comprehensive Excel report generation

## 📞 Support

For issues or questions:
1. Check the console logs for detailed error messages
2. Review the Excel report for specific test failures
3. Ensure all dependencies are properly installed
4. Verify the local Vanna server is running correctly

---

**Happy Testing! 🚀**
