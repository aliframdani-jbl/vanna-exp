import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from src.llm import VannaQdrantClickHouse
from src.database import ClickHouseClient, SchemaExtractor
from src.validation import PreValidator, PostValidator
from src.training import TrainingManager
from src.database_prompts import DATABASE_PROMPTS

# Load environment variables
load_dotenv()


class VannaService:
    """Main service class for text-to-SQL generation with validation and training"""
    
    def __init__(self, database_config: Optional[Dict[str, Any]] = None):
        # Get database type from environment
        self.database_type = os.getenv('DATABASE_TYPE', 'clickhouse').lower()
        
        if self.database_type not in DATABASE_PROMPTS:
            raise ValueError(f"Unsupported database type: {self.database_type}. Supported types: {list(DATABASE_PROMPTS.keys())}")
        
        # Initialize components
        self._init_database(database_config)
        self._init_llm()
        self._init_validators()
        self._init_training_manager()
    
    def _init_database(self, database_config: Optional[Dict[str, Any]] = None):
        """Initialize database client"""
        self.db_client = ClickHouseClient(database_config)
        
        # Set up the run_sql function for Vanna
        def run_sql_wrapper(sql: str):
            return self.db_client.run_sql(sql)
        
        self.run_sql_func = run_sql_wrapper
    
    def _init_llm(self):
        """Initialize LLM client"""
        vanna_config = {'database_type': self.database_type}
        self.vn = VannaQdrantClickHouse(config=vanna_config)
        
        # Set up the run_sql function for Vanna
        self.vn.run_sql = self.run_sql_func
        self.vn.run_sql_is_set = True
    
    def _init_validators(self):
        """Initialize validation components"""
        self.schema_extractor = SchemaExtractor(self.vn)
        self.pre_validator = PreValidator(self.vn)
        self.post_validator = PostValidator(self.schema_extractor)
    
    def _init_training_manager(self):
        """Initialize training manager"""
        self.training_manager = TrainingManager(self.vn, self.db_client)
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL from natural language question with pre and post validation"""
        
        # Pre-validation
        is_valid, message = self.pre_validator.validate_question(question)
        if not is_valid:
            return message
        
        try:
            # Generate SQL using Vanna
            sql = self.vn.generate_sql(question, True)
            
            if not sql:
                return "Sorry, I couldn't generate SQL for your question. Please try rephrasing it."
            
            # Post-validation
            is_sql_valid, sql_message = self.post_validator.validate_sql(sql)
            if not is_sql_valid:
                return sql_message
            
            return str(sql)
            
        except Exception as e:
            raise Exception(f"Failed to generate SQL: {str(e)}")
    
    def run_sql(self, sql: str) -> Dict[str, Any]:
        """Execute SQL and return results"""
        try:
            results_df = self.db_client.run_sql(sql)
            # Convert DataFrame to dict for JSON serialization
            results = {
                'columns': results_df.columns.tolist(),
                'data': results_df.to_dict('records'),
                'row_count': len(results_df)
            }
            return results
        except Exception as e:
            raise Exception(f"Failed to execute SQL: {str(e)}")
    
    def ask(self, question: str) -> Dict[str, Any]:
        """Ask a question and get both SQL and results"""
        try:
            # Generate SQL with validation
            sql = self.generate_sql(question)
            
            # If SQL generation failed (returned error message), return the message
            if not sql or not sql.strip().upper().startswith('SELECT'):
                return {
                    'sql': "",
                    'error': sql if sql else "Failed to generate SQL",
                    'results': {}
                }
            
            # Execute SQL
            results = self.run_sql(sql)
            
            return {
                'sql': sql,
                'results': results
            }
        except Exception as e:
            return {
                'sql': "",
                'error': f"Failed to process question: {str(e)}",
                'results': {}
            }
    
    # Training methods (delegated to TrainingManager)
    def train_ddl(self, ddl: str):
        return self.training_manager.train_ddl(ddl)
    
    def train_documentation(self, documentation: str):
        return self.training_manager.train_documentation(documentation)
    
    def train_sql(self, question: str, sql: str):
        return self.training_manager.train_sql(question, sql)
    
    def train_from_information_schema(self):
        return self.training_manager.train_from_information_schema()
    
    def get_training_data(self):
        return self.training_manager.get_training_data()
    
    def remove_training_data(self, id: str):
        return self.training_manager.remove_training_data(id)
    
    # Configuration methods
    def update_config(self, database_config: Dict[str, Any]):
        """Update database configuration"""
        self.db_client.update_config(database_config)
        return {"status": "success", "message": "Database configuration updated"}
    
    def set_database_type(self, database_type: str):
        """Change the database type and update the context"""
        database_type = database_type.lower()
        
        if database_type not in DATABASE_PROMPTS:
            raise ValueError(f"Unsupported database type: {database_type}. Supported types: {list(DATABASE_PROMPTS.keys())}")
        
        self.database_type = database_type
        self.vn.database_type = database_type
        
        return {
            "status": "success", 
            "message": f"Database type changed to {database_type}",
            "database_type": database_type
        }
    
    def get_database_type(self):
        """Get current database type and available types"""
        return {
            "current_database_type": self.database_type,
            "available_types": list(DATABASE_PROMPTS.keys())
        }
    
    def get_database_contexts(self):
        """Get all available database contexts"""
        return {
            "database_contexts": DATABASE_PROMPTS,
            "current_type": self.database_type
        }
        


