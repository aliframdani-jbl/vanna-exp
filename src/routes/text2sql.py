
import os
from fastapi import APIRouter, HTTPException
import sys

from src.models import DatabaseConfig, QueryRequest, QueryResponse, TrainingRequest
from src.service_manager import service_manager

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

router = APIRouter(
    tags=["text2sql"]
)

def get_text2sql_router(vanna_service):
    @router.post("/ask", response_model=QueryResponse)
    async def ask_question(request: QueryRequest):
        """Ask a natural language question and get both SQL and results"""
        if vanna_service is None:
            raise HTTPException(status_code=503, detail="Vanna service not initialized")
        
        try:
            # Use tenant-based service selection
            if request.tenant_id:
                service = service_manager.get_service(request.tenant_id)
                result = service.ask(request.question)
            else:
                result = vanna_service.ask(request.question)
                
            print("DEBUG: Ask question result:")   
            print(result)
            
            # Handle error case
            if 'error' in result:
                return QueryResponse(
                    sql=result.get('sql', ''),
                    error=result['error'],
                    results=None
                )
            
            # Handle success case
            results_data = result.get('results')
            if results_data and 'data' in results_data:
                # Convert the results format to list of dictionaries
                results_list = results_data['data']
            else:
                results_list = None
                
            return QueryResponse(
                sql=result.get('sql', ''),
                results=results_list
            )
        
        except Exception as e:
            return QueryResponse(
                sql="",
                error=str(e),
                results=None
            )


    @router.post("/sql")
    async def generate_sql(request: QueryRequest):
        """Generate SQL from natural language question without executing"""
        if vanna_service is None:
            raise HTTPException(status_code=503, detail="Vanna service not initialized")
        
        try:
            # Use tenant-based service selection
            if request.tenant_id:
                service = service_manager.get_service(request.tenant_id)
                sql = service.generate_sql(request.question)
            else:
                sql = vanna_service.generate_sql(request.question)
            
            return {"sql": sql}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/execute")
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
                temp_service = service_manager.get_service(db_config)
                results = temp_service.run_sql(sql)
            else:
                results = vanna_service.run_sql(sql)
            
            return {"results": results}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/train")
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


    @router.post("/train/schema")
    async def train_from_schema():
        """Train the model using database schema information"""
        if vanna_service is None:
            raise HTTPException(status_code=503, detail="Vanna service not initialized")
        
        try:
            result = vanna_service.train_from_information_schema()
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/training-data")
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


    @router.delete("/training-data/{data_id}")
    async def remove_training_data(data_id: str):
        """Remove training data by ID"""
        if vanna_service is None:
            raise HTTPException(status_code=503, detail="Vanna service not initialized")
        
        try:
            result = vanna_service.remove_training_data(data_id)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @router.post("/knowledges")
    async def knowledge(documentation: str):
        """Add documentation for training data"""
        if vanna_service is None:
            raise HTTPException(status_code=503, detail="Vanna service not initialized")
        
        try:
            result = vanna_service.add_documentation(documentation)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/config/database")
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

    @router.post("/tenants/{tenant_id}/register")
    async def register_tenant(tenant_id: str, config: DatabaseConfig):
        """Register a new tenant with their database configuration"""
        try:
            db_config = {
                'host': config.host,
                'port': config.port,
                'user': config.user,
                'password': config.password,
                'database': config.database
            }
            service_manager.register_tenant(tenant_id, db_config)
            return {"message": f"Tenant {tenant_id} registered successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/tenants/{tenant_id}")
    async def remove_tenant(tenant_id: str):
        """Remove a tenant and cleanup their service"""
        try:
            service_manager.remove_tenant(tenant_id)
            return {"message": f"Tenant {tenant_id} removed successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/tenants")
    async def list_tenants():
        """List all registered tenants"""
        try:
            stats = service_manager.get_stats()
            return {
                "tenants": stats["tenant_list"],
                "stats": stats
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    return router
    