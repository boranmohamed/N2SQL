# Vanna AI Web Application

A production-ready Python web application that integrates with Vanna.AI to convert natural language queries into SQL queries. Built with Clean Architecture principles, FastAPI, and comprehensive testing.

## 🏗️ Architecture

This application follows **Clean Architecture** principles with clear separation of concerns:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and business orchestration
- **Infrastructure Layer**: External integrations (Vanna AI, Database)
- **Interface Layer**: REST API with FastAPI

## ✨ Features

### Core Functionality
- **Natural Language to SQL**: Convert human questions to SQL queries using Vanna.AI
- **Query Execution**: Execute generated SQL against PostgreSQL/SQLite databases
- **Context-Aware Generation**: RAG system provides schema-aware SQL generation
- **Visual Web Interface**: Interactive testing with real-time results

### Architecture & Performance
- **Local Vanna AI**: Self-hosted Vanna AI for better privacy and cost control
- **RAG Integration**: Enhanced context retrieval using Qdrant vector database
- **Dual Mode Support**: Switch between local and remote Vanna AI services
- **Clean Architecture**: Domain-driven design with clear separation of concerns

### Development & Operations
- **Health Monitoring**: Comprehensive health checks for all components
- **RESTful API**: Clean, documented API endpoints
- **Error Handling**: Robust error handling and logging
- **Testing**: Comprehensive unit tests with pytest
- **Docker Support**: Containerized deployment with docker-compose
- **Production Ready**: Logging, monitoring, and configuration management

### Advanced Features
- **SQL Compatibility**: Automatic PostgreSQL/MySQL → SQLite conversion
- **Vector Search**: Intelligent schema context retrieval
- **Training Pipeline**: Easy model training with DDL and examples
- **Real-time Execution**: Live SQL execution with results visualization

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key (for local Vanna AI)
- Vanna.AI API key (optional, for remote Vanna AI)

### Local Vanna AI Setup (Recommended)

This application supports both **local Vanna AI** (recommended) and **remote Vanna AI** services. The local setup provides better performance, privacy, and cost control.

#### **Step 1: Clone and Setup Local Vanna AI**

```bash
# Clone Vanna AI from GitHub
cd D:\
git clone https://github.com/vanna-ai/vanna.git
cd vanna

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows

# Install Vanna AI in development mode
pip install -e .
```

#### **Step 2: Start Docker Qdrant (Vector Database)**

```bash
# Start Qdrant with Docker
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

# Verify Qdrant is running
curl http://localhost:6333/health
```

#### **Step 3: Configure Local Vanna Server**

```bash
# Create .env file in D:\vanna\
cd D:\vanna
echo OPENAI_API_KEY=your_openai_api_key_here > .env
echo OPENAI_MODEL=gpt-4 >> .env
echo OPENAI_TEMPERATURE=0.1 >> .env

# Start local Vanna server
python local_vanna_server.py
```

#### **Step 4: Setup Application with Local Vanna**

```bash
# In your application directory
cd D:\PycharmProjects\Vanna-AI

# Create .env file
echo USE_LOCAL_VANNA=true > .env
echo LOCAL_VANNA_SERVER_URL=http://localhost:8001 >> .env
echo DATABASE_URL=sqlite:///vanna_app_clean.db >> .env

# Install dependencies
pip install -e .

# Start the web interface
python start_visual_tester.py
```

#### **Step 5: Migrate Schema Data to Qdrant**

```bash
# Run the migration script to populate Qdrant with schema data
python migrate_to_docker_qdrant.py

# Train local Vanna with RAG context
python train_with_rag_context.py
```

### Remote Vanna AI Setup (Alternative)

If you prefer to use the hosted Vanna AI service:

```bash
# Configure for remote Vanna AI
echo USE_LOCAL_VANNA=false > .env
echo VANNA_API_KEY=your_vanna_api_key_here >> .env
echo VANNA_EMAIL=your_email@example.com >> .env
echo VANNA_ORG_ID=your_org_id_here >> .env
```

### Option 1: Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd vanna-ai-webapp
   
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -e ".[dev]"
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Run the application**:
   ```bash
   python -m app.main
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Docker Deployment

1. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Check services**:
   ```bash
   docker-compose ps
   docker-compose logs app
   ```

3. **Access the application**:
   - API: http://localhost:8000
   - PostgreSQL: localhost:5432

## 📚 API Endpoints

### Health Check
```http
GET /health
```
Returns the health status of all application components.

### Process Query
```http
POST /query
Content-Type: application/json

{
  "question": "How many users are there?",
  "user_id": "optional_user_id"
}
```
Converts natural language to SQL and executes it, returning both the SQL and results.

### Root
```http
GET /
```
Returns API information and available endpoints.

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | "Vanna AI Web App" |
| `DEBUG` | Debug mode | false |
| `HOST` | Server host | "0.0.0.0" |
| `PORT` | Server port | 8000 |
| `DATABASE_URL` | Database connection string | SQLite local file |
| `VANNA_API_KEY` | Vanna.AI API key | None (uses mock) |
| `VANNA_MODEL` | AI model to use | "gpt-4" |
| `LOG_LEVEL` | Logging level | "INFO" |

### Database Configuration

The application supports both PostgreSQL and SQLite:

- **PostgreSQL** (recommended for production):
  ```bash
  DATABASE_URL=postgresql://user:password@host:port/database
  ```

- **SQLite** (development/testing):
  ```bash
  DATABASE_URL=sqlite:///./vanna_app.db
  ```

## 🐳 Docker

### Building the Image
```bash
docker build -t vanna-ai-webapp .
```

### Running with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Production Deployment
For production, consider:
- Using environment-specific docker-compose files
- Setting up proper secrets management
- Configuring reverse proxy (nginx)
- Setting up monitoring and alerting

## 🔄 End-to-End Process Flow

This section explains the complete pipeline from user input to database execution, showing exactly how each component works together.

### 📊 System Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask Web      │    │   Local Vanna   │    │   Docker        │
│   (HTML/JS)     │───▶│   Interface      │───▶│   Server        │───▶│   Qdrant        │
│                 │    │   (Python)       │    │   (FastAPI)     │    │   (Vector DB)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       ▼                       ▼                       │
         │              ┌──────────────────┐    ┌─────────────────┐              │
         │              │   RAG System     │◀───│   Enhanced RAG  │◀─────────────┘
         │              │   (Context)      │    │   System        │
         │              └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SQLite        │    │   OpenAI API     │    │   Generated     │
│   Database      │◀───│   (LLM)          │    │   SQL Query     │
│   (Execution)   │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🚀 Step-by-Step Process Flow

#### **Step 1: User Input (Frontend)**
- **Location**: `templates/index.html` - JavaScript function `generateSQL()`
- **Process**: 
  1. User types question: `"Calculate customer lifetime value"`
  2. Clicks "Generate SQL" button
  3. JavaScript captures the question
  4. Makes HTTP POST request to `/api/generate`

#### **Step 2: Flask Web Interface (Backend Router)**
- **Location**: `vanna_visual_tester.py` - Flask route `/api/generate`
- **Process**:
  1. Flask receives POST request with question
  2. Calls `tester.generate_sql_sync(question)`
  3. Returns JSON response with generated SQL

#### **Step 3: VannaTester Client (Synchronous Wrapper)**
- **Location**: `vanna_visual_tester.py` - `VannaTester.generate_sql_sync()`
- **Process**:
  1. Creates new asyncio event loop (Flask is synchronous)
  2. Calls `self.client.generate_sql(question)` asynchronously
  3. Returns structured response with SQL and timing

#### **Step 4: Local Vanna Client (Repository Layer)**
- **Location**: `app/infrastructure/local_vanna_client.py` - `generate_sql()`
- **Process**:
  1. **RAG Context Retrieval**: Calls `_rag_system.retrieve_relevant_context(question)`
  2. **Enhanced Question**: Combines original question + RAG context
  3. **HTTP Request**: Sends to local Vanna server at `http://localhost:8001/generate_sql`
  4. **Response Processing**: Returns generated SQL

#### **Step 5: Enhanced RAG System (Context Provider)**
- **Location**: `app/infrastructure/enhanced_rag_system.py` - `retrieve_relevant_context()`
- **Process**:
  1. **Vector Search**: Creates vector from question text
  2. **Qdrant Query**: Searches Docker Qdrant for similar schema contexts
  3. **Context Extraction**: Returns relevant table schemas and descriptions
  4. **Fallback**: If vector search fails, uses simple text matching

#### **Step 6: Local Vanna Server (FastAPI)**
- **Location**: `D:\vanna\local_vanna_server.py` - `/generate_sql` endpoint
- **Process**:
  1. **Receives Request**: Gets enhanced question with RAG context
  2. **Vanna AI Call**: Calls `vanna.generate_sql(request.question)`
  3. **LLM Processing**: Uses OpenAI API to generate SQL
  4. **Response**: Returns structured JSON with generated SQL

#### **Step 7: Vanna AI Core (OpenAI Integration)**
- **Location**: `D:\vanna\local_vanna_server.py` - Vanna initialization
- **Process**:
  1. **OpenAI API Call**: Sends enhanced question to GPT-4
  2. **Context Processing**: LLM uses RAG context + training examples
  3. **SQL Generation**: Returns generated SQL query
  4. **Response**: Structured JSON back through the chain

#### **Step 8: SQL Execution (Database Layer)**
- **Location**: `vanna_visual_tester.py` - `execute_sql()`
- **Process**:
  1. **SQLite Connection**: Connects to `vanna_app_clean.db`
  2. **SQL Compatibility**: Fixes PostgreSQL/MySQL → SQLite syntax
  3. **Query Execution**: Runs SQL with pandas
  4. **Result Processing**: Converts to JSON format

#### **Step 9: Response Back to Frontend**
- **Location**: `templates/index.html` - JavaScript result display
- **Process**:
  1. **Result Display**: Shows generated SQL in code block
  2. **Execution Button**: Enables "Execute SQL" button
  3. **User Clicks Execute**: Triggers SQL execution
  4. **Results Display**: Shows query results in table format

### 🔄 Complete Flow Summary

Here's the **exact sequence** that happens when you ask "Calculate customer lifetime value":

#### **🔄 Request Flow (Frontend → Backend)**
```
User Input: "Calculate customer lifetime value"
    ↓
Frontend (HTML/JS) → POST /api/generate
    ↓
Flask Router → VannaTester.generate_sql_sync()
    ↓
Local Vanna Client → HTTP POST localhost:8001/generate_sql
    ↓
Enhanced RAG System → Docker Qdrant Query
    ↓
Local Vanna Server → OpenAI GPT-4 API Call
    ↓
Response: "SELECT customer_id, SUM(amount) as lifetime_value FROM sales GROUP BY customer_id"
```

#### **🔄 Response Flow (Backend → Frontend)**
```
Generated SQL: "SELECT customer_id, SUM(amount) as lifetime_value FROM sales GROUP BY customer_id"
    ↓
Local Vanna Server → JSON Response
    ↓
Local Vanna Client → Return SQL String
    ↓
Flask Router → JSON Response
    ↓
Frontend → Display SQL + Enable Execute Button
    ↓
User Clicks Execute → POST /api/execute
    ↓
SQLite Database → Execute Query
    ↓
Results → Display in Table
```

### 🔍 Key Components & Their Roles

| Component | Role | Technology |
|-----------|------|------------|
| **Frontend** | User interface, question input, result display | HTML/JavaScript |
| **Flask Web** | API routing, sync/async coordination | Python Flask |
| **Local Vanna Client** | Repository layer, RAG integration | Python httpx |
| **Enhanced RAG** | Context retrieval, schema knowledge | Qdrant + Vector Search |
| **Docker Qdrant** | Vector database, schema storage | Docker + Qdrant |
| **Local Vanna Server** | SQL generation, LLM coordination | FastAPI + Vanna AI |
| **OpenAI API** | Natural language → SQL conversion | GPT-4 |
| **SQLite Database** | Query execution, data storage | SQLite + Pandas |

### ⚡ Performance Characteristics

- **Total Response Time**: ~3-8 seconds
- **RAG Context Retrieval**: ~100-200ms
- **Vanna AI Processing**: ~2-5 seconds (OpenAI API)
- **SQL Execution**: ~50-100ms
- **Frontend Rendering**: ~50ms

This architecture provides **context-aware SQL generation** by combining your database schema (via RAG) with natural language processing (via Vanna AI) for accurate, schema-compliant SQL queries!

## 📊 Sample Queries

Try these natural language questions:

1. **"How many users are there?"**
2. **"Show me all employees in the Engineering department"**
3. **"What's the average salary?"**
4. **"List recent sales over $100"**
5. **"How many orders are pending?"**
6. **"Calculate customer lifetime value"**
7. **"Show employees with high salary"**
8. **"What is the total sales amount?"**
9. **"Find pending orders"**
10. **"Show me sales performance by employee"**

## 🔍 Development

### Project Structure
```
vanna-ai-webapp/
├── app/
│   ├── domain/           # Business entities and interfaces
│   ├── application/      # Use cases and business logic
│   ├── infrastructure/   # External integrations
│   ├── interface/        # API endpoints and DTOs
│   └── main.py          # Application entry point
├── tests/                # Test suite
├── logs/                 # Application logs
├── docker-compose.yml    # Docker services
├── Dockerfile           # Application container
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

### Adding New Features

1. **Domain Layer**: Define entities and repository interfaces
2. **Application Layer**: Implement use cases
3. **Infrastructure Layer**: Create concrete implementations
4. **Interface Layer**: Add API endpoints and DTOs
5. **Tests**: Write comprehensive tests

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/

# Run all quality checks
pre-commit run --all-files
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check `DATABASE_URL` in `.env`
   - Ensure database service is running
   - Verify network connectivity

2. **Vanna AI Errors**:
   - Check `VANNA_API_KEY` configuration
   - Verify API key validity
   - Check network connectivity to Vanna.AI

3. **Port Already in Use**:
   - Change `PORT` in `.env`
   - Kill existing processes on port 8000

4. **Docker Issues**:
   - Ensure Docker is running
   - Check `docker-compose ps` for service status
   - View logs with `docker-compose logs`

### Local Vanna AI & Qdrant Issues

5. **Qdrant Connection Failed**:
   ```bash
   # Check if Qdrant is running
   docker ps | grep qdrant
   
   # Restart Qdrant if needed
   docker restart qdrant
   
   # Check Qdrant health
   curl http://localhost:6333/health
   ```

6. **Local Vanna Server Not Responding**:
   ```bash
   # Check if local Vanna server is running
   curl http://localhost:8001/health
   
   # Check OpenAI API key
   echo $OPENAI_API_KEY
   
   # Restart local Vanna server
   cd D:\vanna
   python local_vanna_server.py
   ```

7. **RAG Context Not Retrieved**:
   ```bash
   # Check Qdrant data
   python fix_qdrant_migration.py
   
   # Verify schema data exists
   python -c "
   from qdrant_client import QdrantClient
   client = QdrantClient(host='localhost', port=6333)
   points = client.scroll('database_schema', limit=10)
   print(f'Points in Qdrant: {len(points[0])}')
   "
   ```

8. **Event Loop Closed Error**:
   - This happens when Flask tries to use async code
   - Solution: Use the `generate_sql_sync()` wrapper method
   - The application handles this automatically

9. **SQL Generation Timeout**:
   ```bash
   # Increase timeout in local_vanna_client.py
   # Update LOCAL_VANNA_TIMEOUT in .env
   echo LOCAL_VANNA_TIMEOUT=120 >> .env
   ```

10. **Schema Context Empty**:
    ```bash
    # Re-populate Qdrant with schema data
    python migrate_to_docker_qdrant.py
    
    # Train Vanna with fresh data
    python train_with_rag_context.py
    ```

### Logs

Application logs are available:
- **Console**: During development
- **File**: `logs/app.log` (production)
- **Docker**: `docker-compose logs app`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Vanna.AI](https://vanna.ai/) for natural language to SQL conversion
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) principles by Robert C. Martin

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation at `/docs` endpoint
- Review the logs for error details
