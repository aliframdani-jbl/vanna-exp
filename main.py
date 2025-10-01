from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

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
    except Exception as e:
        print(f"Failed to initialize Vanna service: {str(e)}")
        vanna_service = None
    
    yield
    
    # Shutdown
    print("Shutting down...")


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
    
    return {
        "status": "healthy",
        "service": "vanna",
        "database": "clickhouse"
    }


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask a natural language question and get both SQL and results"""
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    try:
        # Update database config if provided
        if request.database_config:
            db_config = {
                'host': request.database_config.host,
                'port': request.database_config.port,
                'user': request.database_config.user,
                'password': request.database_config.password,
                'database': request.database_config.database
            }
            temp_service = VannaService(database_config=db_config)
            result = temp_service.ask(request.question)
        else:
            result = vanna_service.ask(request.question)
        
        return QueryResponse(
            sql=result['sql'],
            results=result['results']
        )
    
    except Exception as e:
        return QueryResponse(
            sql="",
            error=str(e)
        )


@app.post("/sql")
async def generate_sql(request: QueryRequest):
    """Generate SQL from natural language question without executing"""
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    try:
        # Update database config if provided
        if request.database_config:
            db_config = {
                'host': request.database_config.host,
                'port': request.database_config.port,
                'user': request.database_config.user,
                'password': request.database_config.password,
                'database': request.database_config.database
            }
            temp_service = VannaService(database_config=db_config)
            sql = temp_service.generate_sql(request.question)
        else:
            sql = vanna_service.generate_sql(request.question)
        
        return {"sql": sql}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute")
async def execute_sql(sql_request: dict):
    """Execute SQL directly"""
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    sql = sql_request.get('sql')
    if not sql:
        raise HTTPException(status_code=400, detail="SQL query is required")
    
    try:
        # Update database config if provided
        if 'database_config' in sql_request:
            db_config = sql_request['database_config']
            temp_service = VannaService(database_config=db_config)
            results = temp_service.run_sql(sql)
        else:
            results = vanna_service.run_sql(sql)
        
        return {"results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train")
async def train_model(request: TrainingRequest):
    """Train the Vanna model with DDL, documentation, or question-SQL pairs"""
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    try:
        results = []
        
        if request.ddl:
            result = vanna_service.train_ddl(request.ddl)
            results.append({"type": "ddl", "result": result})
        
        if request.documentation:
            result = vanna_service.train_documentation(request.documentation)
            results.append({"type": "documentation", "result": result})
        
        # Loop through question-SQL pairs
        if request.question and request.sql:
            # Ensure both arrays have the same length
            if len(request.question) != len(request.sql):
                raise HTTPException(status_code=400, detail="Question and SQL arrays must have the same length")
            
            # Loop through each pair
            for i, (question, sql) in enumerate(zip(request.question, request.sql)):
                result = vanna_service.train_sql(question, sql)
                results.append({"type": "question_sql", "pair": i+1, "result": result})
        
        if not results:
            raise HTTPException(status_code=400, detail="At least one training data type is required")

        try:
            current_data = vanna_service.get_training_data()
            print(f"DEBUG: After training, we have {len(current_data)} training records")
        except Exception as e:
            print(f"DEBUG: Error checking training data after insert: {e}")
    
        
        return {"training_results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train/schema")
async def train_from_schema():
    """Train the model using database schema information"""
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    try:
        result = vanna_service.train_from_information_schema()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/training-data")
async def get_training_data():
    """Get current training data"""
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    try:
        data = vanna_service.get_training_data()
        print(f"DEBUG: Found {len(data)} training records")
        return {"training_data": data}
    except Exception as e:
        print(f"DEBUG: Error getting training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/training-data/{data_id}")
async def remove_training_data(data_id: str):
    """Remove training data by ID"""
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    try:
        result = vanna_service.remove_training_data(data_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/config/database")
async def update_database_config(config: DatabaseConfig):
    """Update database configuration"""
    if vanna_service is None:
        raise HTTPException(status_code=503, detail="Vanna service not initialized")
    
    try:
        db_config = {
            'host': config.host,
            'port': config.port,
            'user': config.user,
            'password': config.password,
            'database': config.database
        }
        result = vanna_service.update_config(db_config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    uvicorn.run(app, host=host, port=port)
