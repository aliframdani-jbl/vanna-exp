import os
import pandas as pd
from typing import Optional, Dict, Any, List
import clickhouse_connect
from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from src.database_prompts import DATABASE_PROMPTS

# Load environment variables
load_dotenv()


class VannaQdrantClickHouse(Qdrant_VectorStore):
    """Custom Vanna implementation using Qdrant for vector storage and ClickHouse for database"""
    
    def __init__(self, config=None):
        # Store database configuration
        self.database_type = config.get('database_type', 'clickhouse') if config else 'clickhouse'
        
        # Initialize Qdrant vector store
        if config and 'qdrant_client' in config:
            qdrant_config = {'client': config['qdrant_client']}
        else:
            # Default Qdrant configuration
            qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
            qdrant_api_key = os.getenv('QDRANT_API_KEY')
            
            if qdrant_api_key:
                qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            else:
                qdrant_client = QdrantClient(url=qdrant_url)
            
            qdrant_config = {'client': qdrant_client}
        
        Qdrant_VectorStore.__init__(self, config=qdrant_config)
        
        # Initialize Qwen client
        self._init_qwen_client()
    
    def _init_qwen_client(self):
        """Initialize Qwen client"""
        try:
            import openai
            
            # Configure for Qwen API
            qwen_api_key = os.getenv('QWEN_API_KEY') or os.getenv('DASHSCOPE_API_KEY')
            qwen_base_url = os.getenv('QWEN_BASE_URL', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1')
            
            if not qwen_api_key:
                raise Exception("QWEN_API_KEY or DASHSCOPE_API_KEY environment variable is required")
            
            self.qwen_client = openai.OpenAI(
                api_key=qwen_api_key,
                base_url=qwen_base_url
            )
            
            # Default Qwen model
            self.qwen_model = os.getenv('QWEN_MODEL', 'qwen-turbo')
            
        except ImportError:
            raise Exception("OpenAI package not installed. Please install it with: pip install openai")

    def submit_prompt(self, prompt, **kwargs) -> str:
        """Submit prompt to Qwen and return response"""
        try:
            model = kwargs.get('model', self.qwen_model)
            
            # Get database-specific system prompt
            db_config = DATABASE_PROMPTS.get(self.database_type, DATABASE_PROMPTS['clickhouse'])
            system_prompt = db_config['system_prompt']
            table_context = db_config.get('table_context', '')
            
            # Build enhanced system prompt with table context
            full_system_prompt = f"{system_prompt}\n\n{table_context}".strip()
            
            # Handle different prompt formats from Vanna
            if isinstance(prompt, list):
                messages = []
                has_system = False
                
                for msg in prompt:
                    if isinstance(msg, dict) and msg.get('role') == 'system':
                        has_system = True
                        # Replace system message with our enhanced one
                        messages.append({"role": "system", "content": full_system_prompt})
                    elif isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                        messages.append({
                            "role": msg['role'],
                            "content": str(msg['content'])
                        })
                    else:
                        messages.append({"role": "user", "content": str(msg)})
                
                if not has_system:
                    messages.insert(0, {"role": "system", "content": full_system_prompt})
                    
            elif isinstance(prompt, str):
                messages = [
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": prompt}
                ]
            else:
                messages = [
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": str(prompt)}
                ]
            
            response = self.qwen_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 500),
                temperature=kwargs.get('temperature', 0.1)
            )
            
            result = response.choices[0].message.content
            return str(result) if result else ""
            
        except Exception as e:
            raise Exception(f"Qwen API error: {str(e)}")
    
    def system_message(self, message: str) -> Dict[str, str]:
        """Format system message for the chat API"""
        return {"role": "system", "content": message}
    
    def user_message(self, message: str) -> Dict[str, str]:
        """Format user message for the chat API"""
        return {"role": "user", "content": message}
    
    def assistant_message(self, message: str) -> Dict[str, str]:
        """Format assistant message for the chat API"""
        return {"role": "assistant", "content": message}


class VannaService:
    def __init__(self, database_config: Optional[Dict[str, Any]] = None):
        # Get database type from environment
        self.database_type = os.getenv('DATABASE_TYPE', 'clickhouse').lower()
        
        if self.database_type not in DATABASE_PROMPTS:
            raise ValueError(f"Unsupported database type: {self.database_type}. Supported types: {list(DATABASE_PROMPTS.keys())}")
        
        # Database configuration
        if database_config:
            self.db_config = database_config
        else:
            self.db_config = {
                'host': os.getenv('CLICKHOUSE_HOST', 'localhost'),
                'port': int(os.getenv('CLICKHOUSE_PORT', 8123)),
                'user': os.getenv('CLICKHOUSE_USER', 'default'),
                'password': os.getenv('CLICKHOUSE_PASSWORD', ''),
                'database': os.getenv('CLICKHOUSE_DATABASE', 'default')
            }
        
        # Initialize Vanna with Qdrant and custom LLM
        vanna_config = {'database_type': self.database_type}
        self.vn = VannaQdrantClickHouse(config=vanna_config)
        
        # Connect to ClickHouse
        self._connect_to_clickhouse()
    
    def _connect_to_clickhouse(self):
        """Connect to ClickHouse database"""
        try:
            self.clickhouse_client = clickhouse_connect.get_client(
                host=self.db_config['host'],
                port=self.db_config['port'],
                username=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            
            # Set up the run_sql function for Vanna
            def run_sql(sql: str) -> pd.DataFrame:
                try:
                    result = self.clickhouse_client.query(sql)
                    # Convert to pandas DataFrame
                    df = pd.DataFrame(result.result_rows, columns=result.column_names)
                    return df
                except Exception as e:
                    raise Exception(f"ClickHouse query error: {str(e)}")
            
            self.vn.run_sql = run_sql
            self.vn.run_sql_is_set = True
            
            print(f"Connected to ClickHouse: {self.db_config['host']}:{self.db_config['port']}")
            
            # Test connection
            test_df = run_sql("SELECT 1 as test")
            print(f"ClickHouse connection test successful: {test_df}")
            
        except Exception as e:
            print(f"Failed to connect to ClickHouse: {str(e)}")
            raise
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL from natural language question"""
        try:
            sql = self.vn.generate_sql(question, True)
            return str(sql) if sql else ""
        except Exception as e:
            raise Exception(f"Failed to generate SQL: {str(e)}")
    
    def run_sql(self, sql: str) -> Dict[str, Any]:
        """Execute SQL and return results"""
        try:
            results_df = self.vn.run_sql(sql)
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
            # Use Vanna's ask method which handles both SQL generation and execution
            sql = self.generate_sql(question)
            results = self.run_sql(sql)
            
            return {
                'sql': sql,
                'results': results
            }
        except Exception as e:
            raise Exception(f"Failed to process question: {str(e)}")
    
    def train_ddl(self, ddl: str):
        """Train the model with DDL statements"""
        try:
            self.vn.train(ddl=ddl)
            return {"status": "success", "message": "DDL trained successfully"}
        except Exception as e:
            raise Exception(f"Failed to train DDL: {str(e)}")
    
    def train_documentation(self, documentation: str):
        """Train the model with documentation"""
        try:
            self.vn.train(documentation=documentation)
            return {"status": "success", "message": "Documentation trained successfully"}
        except Exception as e:
            raise Exception(f"Failed to train documentation: {str(e)}")
    
    def train_sql(self, question: str, sql: str):
        """Train the model with question-SQL pairs"""
        try:
            self.vn.train(question=question, sql=sql)
            return {"status": "success", "message": "Question-SQL pair trained successfully"}
        except Exception as e:
            raise Exception(f"Failed to train SQL: {str(e)}")
    
    def train_from_information_schema(self):
        """Train the model using database schema information"""
        try:
            # Get information schema from ClickHouse
            schema_sql = """
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default,
                column_comment
            FROM information_schema.columns 
            WHERE table_schema = '{}'
            ORDER BY table_name, ordinal_position
            """.format(self.db_config['database'])
            
            df_information_schema = self.vn.run_sql(schema_sql)
            
            # Generate training plan
            plan = self.vn.get_training_plan_generic(df_information_schema)
            
            # Execute training
            self.vn.train(plan=plan)
            
            return {
                "status": "success", 
                "message": f"Schema training completed. Processed {len(df_information_schema)} columns.",
                "plan_items": len(plan) if plan else 0
            }
        except Exception as e:
            raise Exception(f"Failed to train from schema: {str(e)}")
    
    def get_training_data(self):
        """Get current training data"""
        try:
            raw_data = self.vn.get_training_data()
            
            # Check if raw_data is a pandas DataFrame
            if hasattr(raw_data, 'to_dict'):
                # It's a pandas DataFrame, convert to proper JSON format
                try:
                    # Convert DataFrame to list of dictionaries (records format)
                    training_records = raw_data.to_dict('records')
                    return training_records
                except Exception as df_error:
                    print(f"DEBUG: DataFrame conversion error: {df_error}")
                    # Fallback: convert to dictionary format
                    try:
                        return {
                            'columns': raw_data.columns.tolist(),
                            'data': raw_data.values.tolist(),
                            'index': raw_data.index.tolist()
                        }
                    except:
                        # Final fallback: convert to string but in a structured way
                        return {
                            'training_data_summary': f"Found {len(raw_data)} training records",
                            'columns': list(raw_data.columns) if hasattr(raw_data, 'columns') else [],
                            'row_count': len(raw_data) if hasattr(raw_data, '__len__') else 0,
                            'data_preview': str(raw_data.head() if hasattr(raw_data, 'head') else raw_data)
                        }
            
            # If it's a list, process each item
            elif isinstance(raw_data, list):
                serializable_data = []
                for item in raw_data:
                    if hasattr(item, '__dict__'):
                        # Convert object to dictionary
                        item_dict = {}
                        for key, value in vars(item).items():
                            try:
                                if isinstance(value, (str, int, float, bool, type(None))):
                                    item_dict[key] = value
                                elif isinstance(value, (list, dict)):
                                    item_dict[key] = value
                                else:
                                    item_dict[key] = str(value)
                            except:
                                item_dict[key] = str(value)
                        serializable_data.append(item_dict)
                    elif isinstance(item, dict):
                        # Already a dictionary, ensure values are serializable
                        clean_dict = {}
                        for key, value in item.items():
                            try:
                                if isinstance(value, (str, int, float, bool, type(None))):
                                    clean_dict[key] = value
                                elif isinstance(value, (list, dict)):
                                    clean_dict[key] = value
                                else:
                                    clean_dict[key] = str(value)
                            except:
                                clean_dict[key] = str(value)
                        serializable_data.append(clean_dict)
                    else:
                        serializable_data.append(str(item))
                return serializable_data
            
            # If it's a dictionary
            elif isinstance(raw_data, dict):
                clean_dict = {}
                for key, value in raw_data.items():
                    try:
                        if isinstance(value, (str, int, float, bool, type(None))):
                            clean_dict[key] = value
                        elif isinstance(value, (list, dict)):
                            clean_dict[key] = value
                        else:
                            clean_dict[key] = str(value)
                    except:
                        clean_dict[key] = str(value)
                return clean_dict
            
            # Fallback for other types
            else:
                return {
                    'training_data_type': str(type(raw_data)),
                    'training_data_summary': str(raw_data)[:500] + '...' if len(str(raw_data)) > 500 else str(raw_data)
                }
            
        except Exception as e:
            print(f"DEBUG: Error in get_training_data: {e}")
            raise Exception(f"Failed to get training data: {str(e)}")
    
    def remove_training_data(self, id: str):
        """Remove training data by ID"""
        try:
            self.vn.remove_training_data(id)
            return {"status": "success", "message": f"Training data {id} removed successfully"}
        except Exception as e:
            raise Exception(f"Failed to remove training data: {str(e)}")
    
    def update_config(self, database_config: Dict[str, Any]):
        """Update database configuration"""
        self.db_config = database_config
        self._connect_to_clickhouse()
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
