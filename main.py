from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
from dotenv import load_dotenv

from src.routes.text2sql import get_text2sql_router
from src.service_manager import service_manager

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from models import QueryRequest, QueryResponse, TrainingRequest, DatabaseConfig
from vanna_service import VannaService

# Global VannaService instance
vanna_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global vanna_service
    try:
        print("Initializing vanna service...")
        vanna_service = VannaService()
        print("Vanna service initialized successfully")
        
        # Set the default service in service manager
        service_manager._default_service = vanna_service
        
        # Load tenant configurations
        try:
            from tenant_config import TENANT_CONFIGS
            for tenant_id, db_config in TENANT_CONFIGS.items():
                service_manager.register_tenant(tenant_id, db_config)
            print(f"Loaded {len(TENANT_CONFIGS)} tenant configurations")
        except ImportError:
            print("No tenant_config.py found, skipping tenant configuration loading")
        except Exception as e:
            print(f"Error loading tenant configurations: {e}")
        
        # Include router after service is initialized
        app.include_router(get_text2sql_router(vanna_service))
        print("Text2SQL router included successfully")
    except Exception as e:
        print(f"Failed to initialize Vanna service: {str(e)}")
        vanna_service = None
    
    yield
    
    # Shutdown
    print("Shutting down...")
    # Cleanup all cached services
    service_manager.cleanup_all()


# Initialize FastAPI app
app = FastAPI(
    title="Text2SQL API with Vanna",
    description="A simple API to convert natural language to SQL using Vanna with ClickHouse",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Text2SQL API with Vanna",
        "version": "1.0.0",
        "endpoints": {
            "ask": "POST /ask - Ask a natural language question",
            "sql": "POST /sql - Generate SQL only",
            "execute": "POST /execute - Execute SQL directly",
            "train": "POST /train - Train the model",
            "health": "GET /health - Health check"
        }
    }


@app.get("/health")
async def health_check():
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    # Get service manager stats
    tenant_stats = service_manager.get_stats()
    
    return {
        "status": "healthy",
        "service": "vanna",
        "database": "clickhouse",
        "tenant_management": tenant_stats
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    uvicorn.run(app, host=host, port=port)
