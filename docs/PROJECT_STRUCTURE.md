# Vanna Text2SQL Project

Clean and organized folder structure for the Vanna Text2SQL implementation.

## 📁 Project Structure

```
vanna/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (local)
├── .env.example          # Environment variables template
├── docker-compose.yml    # Docker services configuration
├── Dockerfile           # Container configuration
│
├── src/                 # Source code
│   ├── vanna_service.py # Core Vanna service implementation
│   ├── database_prompts.py # Database-specific prompts
│   └── models.py        # Pydantic models for API
│
├── tests/               # Test files
│   ├── test_simple_fix.py
│   ├── test_database_types.py
│   ├── test_training_data.py
│   ├── test_vanna_qdrant.py
│   ├── test_qwen_api.py
│   └── debug_*.py       # Debug scripts
│
├── scripts/            # Utility scripts
│   ├── setup_qdrant_clickhouse.sh
│   ├── install.sh
│   ├── start.sh
│   ├── example.py
│   └── llm_switcher.py
│
└── docs/              # Documentation
    ├── README.md
    └── TEMPORAL_MAPPING.md
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start services:**
   ```bash
   docker-compose up -d  # Start Qdrant & ClickHouse
   python main.py        # Start API server
   ```

4. **Test the API:**
   ```bash
   python tests/test_simple_fix.py
   ```

## 🎯 Key Features

- ✅ **Clean folder structure** - organized by purpose
- ✅ **Separated concerns** - prompts, models, services
- ✅ **Proper imports** - src/ directory structure  
- ✅ **Test organization** - all tests in tests/
- ✅ **Script management** - utilities in scripts/
- ✅ **Documentation** - guides in docs/

## 📊 API Endpoints

- `POST /sql` - Generate SQL from natural language
- `POST /ask` - Generate SQL and execute query
- `POST /train` - Train the model with examples
- `GET /training-data` - View training data
- `GET /config/database-type` - Get current database type
- `PUT /config/database-type/{type}` - Change database type

Clean, simple, and focused! 🎯