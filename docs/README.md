# Text2SQL API with Vanna + Qdrant + ClickHouse

A powerful REST API that converts natural language questions to SQL using Vanna AI with **Qdrant vector database** for training data storage and **ClickHouse** as the target database.

## Architecture

This implementation uses:
- **Vanna AI**: Text-to-SQL conversion with RAG (Retrieval-Augmented Generation)
- **Qdrant**: Vector database for storing and retrieving training data
- **ClickHouse**: Target SQL database for query execution
- **Qwen**: Alibaba's large language model for SQL generation

## Features

- Convert natural language questions to SQL queries
- Execute queries on ClickHouse database
- Vector-based training data storage with Qdrant
- Custom Qwen LLM integration
- Automated schema-based training
- Simple REST API interface
- Configurable database connections

## Quick Setup

### 1. Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Qwen API key (from Alibaba Cloud DashScope)

### 2. Automated Setup
```bash
# Run the automated setup script
./setup_qdrant_clickhouse.sh
```

This script will:
- Start Qdrant and ClickHouse using Docker
- Install Python dependencies
- Create sample database and tables
- Set up environment configuration

### 3. Manual Setup

**Start Services:**
```bash
# Start Qdrant and ClickHouse
docker-compose up -d
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Configure Environment:**
```bash
# Copy and edit environment variables
cp .env.example .env
# Edit .env with your Qwen API key
```

**Start API:**
```bash
python main.py
```

## Environment Configuration

Edit `.env` file with your settings:

```bash
# Qwen Configuration (required)
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo

# ClickHouse Configuration
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=vanna_demo

# Qdrant Configuration (optional - defaults to local)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## API Endpoints

### Main Endpoints

- **GET** `/` - API information and available endpoints
- **GET** `/health` - Health check
- **POST** `/ask` - Ask a natural language question (returns SQL + results)
- **POST** `/sql` - Generate SQL only (no execution)
- **POST** `/execute` - Execute SQL directly

### Training Endpoints

- **POST** `/train` - Train with DDL, documentation, or Q&A pairs
- **POST** `/train/schema` - **NEW**: Auto-train from database schema
- **GET** `/training-data` - Get current training data
- **DELETE** `/training-data/{id}` - Remove training data

### Configuration

- **POST** `/config/database` - Update database configuration

## Usage Examples

### 1. Train from Database Schema (Recommended First Step)
```bash
curl -X POST "http://localhost:8000/train/schema"
```

### 2. Ask Natural Language Questions
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many customers do we have?"
  }'
```

### 3. Train with Custom Data
```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "ddl": "CREATE TABLE customers (id UInt32, name String, country String) ENGINE = MergeTree() ORDER BY id",
    "documentation": "The customers table contains customer information including their country of residence"
  }'
```

### 4. Train with Question-SQL Pairs
```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "question": ["How many customers are there?", "What are the total sales?"],
    "sql": ["SELECT COUNT(*) FROM customers", "SELECT SUM(price * quantity) FROM orders"]
  }'
```

## Testing

Run comprehensive tests:
```bash
python test_vanna_qdrant.py
```

This will test:
- Health checks
- Schema training
- DDL training  
- Documentation training
- Question-SQL pair training
- SQL generation
- Question answering

## Sample Questions (after training)

Once you've trained the model with schema data, try these questions:

- "How many customers do we have?"
- "What are the total sales by country?"
- "Show me the top 5 customers by order value"
- "What products were ordered in the last month?"
- "Which country has the most customers?"

## Architecture Details

### Custom LLM Implementation
```python
class CustomQwenLLM(VannaBase):
    def submit_prompt(self, prompt, **kwargs) -> str:
        # Custom Qwen integration
        # Uses qwen-turbo by default
```

### Qdrant Vector Storage
- Stores training data as vectors
- Enables semantic similarity search
- Retrieves relevant context for SQL generation

### ClickHouse Integration
- Direct connection using clickhouse-connect
- Pandas DataFrame results
- Support for complex queries

## Services

The system runs these services:

- **Qdrant**: http://localhost:6333 (Vector database)
- **ClickHouse**: http://localhost:8123 (SQL database)
- **API Server**: http://localhost:8000 (REST API)

## Troubleshooting

### Common Issues

1. **Qwen API Error**: Ensure `QWEN_API_KEY` is set in `.env`
2. **Qdrant Connection**: Check if Qdrant is running on port 6333
3. **ClickHouse Connection**: Verify ClickHouse is running on port 8123
4. **Training Issues**: Start with schema training first

### Check Service Status
```bash
# Check if services are running
curl http://localhost:6333/health  # Qdrant
curl http://localhost:8123/ping    # ClickHouse
curl http://localhost:8000/health  # API
```

### View Logs
```bash
# View service logs
docker-compose logs qdrant
docker-compose logs clickhouse
```

## Production Considerations

1. **Security**: Configure proper authentication for Qdrant and ClickHouse
2. **Scaling**: Use Qdrant Cloud and ClickHouse Cloud for production
3. **Monitoring**: Add health checks and monitoring
4. **Rate Limiting**: Implement rate limiting for the API
5. **CORS**: Configure appropriate CORS settings

## Getting Started Workflow

1. Run `./setup_qdrant_clickhouse.sh`
2. Set your Qwen API key in `.env`
3. Start the API: `python main.py`
4. Train from schema: `curl -X POST http://localhost:8000/train/schema`
5. Ask questions: `curl -X POST http://localhost:8000/ask -d '{"question": "How many customers?"}'`
6. Run tests: `python test_vanna_qdrant.py`

This implementation provides a production-ready foundation for text-to-SQL conversion with modern vector database technology.

## Features

- Convert natural language questions to SQL queries
- Execute queries on ClickHouse database
- Changeable database configuration per request
- Train the model with your own data (DDL, documentation, Q&A pairs)
- Simple REST API interface

## Setup

1. **Clone and navigate to the project:**
```bash
cd /Users/alramdein/Jubelio/Experiment/text2sql/vanna
```

2. **Configure environment variables:**
Edit the `.env` file with your settings:
```bash
# ClickHouse Configuration
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=default

# Vanna Configuration
VANNA_API_KEY=your_vanna_api_key_here
VANNA_MODEL=chinook

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

3. **Start the server:**
```bash
chmod +x start.sh
./start.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## API Endpoints

### Main Endpoints

- **GET** `/` - API information and available endpoints
- **GET** `/health` - Health check
- **POST** `/ask` - Ask a natural language question (returns SQL + results)
- **POST** `/sql` - Generate SQL only (no execution)
- **POST** `/execute` - Execute SQL directly

### Training Endpoints

- **POST** `/train` - Train the model with DDL, documentation, or Q&A pairs
- **GET** `/training-data` - Get current training data
- **DELETE** `/training-data/{id}` - Remove training data

### Configuration

- **POST** `/config/database` - Update database configuration

## Usage Examples

### 1. Ask a Question
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me all users from the last 30 days"
  }'
```

### 2. Generate SQL Only
```bash
curl -X POST "http://localhost:8000/sql" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the top 10 products by sales?"
  }'
```

### 3. Use Different Database
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me total revenue",
    "database_config": {
      "host": "your-clickhouse-host",
      "port": 8123,
      "user": "your-user",
      "password": "your-password",
      "database": "your-database"
    }
  }'
```

### 4. Train the Model
```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "ddl": "CREATE TABLE users (id UInt32, name String, created_at DateTime) ENGINE = MergeTree() ORDER BY id",
    "documentation": "The users table contains customer information",
    "question": "How many users do we have?",
    "sql": "SELECT COUNT(*) FROM users"
  }'
```

## API Response Format

### Successful Query Response
```json
{
  "sql": "SELECT COUNT(*) FROM users WHERE created_at >= now() - INTERVAL 30 DAY",
  "results": [
    {"count": 150}
  ]
}
```

### Error Response
```json
{
  "sql": "",
  "error": "Table 'users' doesn't exist"
}
```

## Requirements

- Python 3.8+
- ClickHouse database
- Vanna API key (get from https://vanna.ai)

## Environment Variables

- `CLICKHOUSE_HOST`: ClickHouse server host
- `CLICKHOUSE_PORT`: ClickHouse server port (default: 8123)
- `CLICKHOUSE_USER`: ClickHouse username
- `CLICKHOUSE_PASSWORD`: ClickHouse password
- `CLICKHOUSE_DATABASE`: Default database name
- `VANNA_API_KEY`: Your Vanna AI API key
- `VANNA_MODEL`: Vanna model name (default: chinook)
- `API_HOST`: API server host (default: 0.0.0.0)
- `API_PORT`: API server port (default: 8000)

## Notes

- The API supports changing database configuration per request
- You can train the model with your own data for better results
- The service automatically connects to ClickHouse on startup
- CORS is enabled for all origins (modify in production)

## Getting Started with Vanna

1. Sign up at https://vanna.ai to get your API key
2. Replace `your_vanna_api_key_here` in `.env` with your actual API key
3. Optionally create a new model or use an existing one
4. Train your model with your database schema and sample queries for better results
