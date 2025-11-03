import os
from typing import Dict, Any
from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient
from src.database_prompts import DATABASE_PROMPTS


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