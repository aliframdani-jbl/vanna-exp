import os
import pandas as pd
from typing import Optional, Dict, Any, List
import clickhouse_connect
from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VannaQdrantClickHouse(Qdrant_VectorStore):
    """Custom Vanna implementation using Qdrant for vector storage and ClickHouse for database"""
    
    def __init__(self, config=None):
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
            
            # Debug logging
            print(f"DEBUG: submit_prompt called with type: {type(prompt)}")
            
            # Handle different prompt formats from Vanna
            if isinstance(prompt, list):
                # Vanna is passing a list of messages directly
                messages = []
                for msg in prompt:
                    if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                        # Ensure content is a string
                        content = msg['content']
                        if not isinstance(content, str):
                            content = str(content)
                        messages.append({
                            "role": msg['role'],
                            "content": content
                        })
                    else:
                        # Fallback for unexpected format
                        messages.append({
                            "role": "user",
                            "content": str(msg)
                        })
            elif isinstance(prompt, str):
                # Simple string prompt
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that generates SQL queries. Always respond with valid SQL syntax."},
                    {"role": "user", "content": prompt}
                ]
            else:
                # Fallback: convert to string
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that generates SQL queries. Always respond with valid SQL syntax."},
                    {"role": "user", "content": str(prompt)}
                ]
            
            print(f"DEBUG: Final messages to API (count: {len(messages)})")
            for i, msg in enumerate(messages):
                print(f"   {i}: {msg['role']} - {msg['content'][:100]}...")
            
            response = self.qwen_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 500),
                temperature=kwargs.get('temperature', 0.1)
            )
            
            # Ensure we get a string response
            result = response.choices[0].message.content
            if not isinstance(result, str):
                result = str(result)
            
            print(f"DEBUG: Qwen API response: {result[:100]}...")
            return result
            
        except Exception as e:
            print(f"DEBUG: Qwen API call failed with error: {e}")
            # Return a more specific error message
            error_msg = str(e)
            if "Error code: 400" in error_msg and "missing_required_parameter" in error_msg:
                print("DEBUG: This appears to be a message format issue with Qwen API")
            raise Exception(f"Qwen API error: {error_msg}")
    
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
        self.vn = VannaQdrantClickHouse()
        
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
            sql = self.vn.generate_sql(question)
            # Ensure the result is always a string
            if not isinstance(sql, str):
                sql = str(sql)
            return sql
        except Exception as e:
            error_msg = str(e)
            print(f"DEBUG: generate_sql failed with error: {error_msg}")
            raise Exception(f"Failed to generate SQL: {error_msg}")
    
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
