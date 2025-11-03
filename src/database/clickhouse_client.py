import os
import pandas as pd
import clickhouse_connect
from typing import Dict, Any, Optional


class ClickHouseClient:
    """ClickHouse database client with connection management"""
    
    def __init__(self, database_config: Optional[Dict[str, Any]] = None):
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
        
        self.client = None
        self.connect()
    
    def connect(self):
        """Connect to ClickHouse database"""
        try:
            self.client = clickhouse_connect.get_client(
                host=self.db_config['host'],
                port=self.db_config['port'],
                username=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            
            print(f"Connected to ClickHouse: {self.db_config['host']}:{self.db_config['port']}")
            
            # Test connection
            test_result = self.client.query("SELECT 1 as test")
            print(f"ClickHouse connection test successful")
            
        except Exception as e:
            print(f"Failed to connect to ClickHouse: {str(e)}")
            raise
    
    def run_sql(self, sql: str) -> pd.DataFrame:
        """Execute SQL and return results as DataFrame"""
        try:
            result = self.client.query(sql)
            # Convert to pandas DataFrame
            df = pd.DataFrame(result.result_rows, columns=result.column_names)
            return df
        except Exception as e:
            raise Exception(f"ClickHouse query error: {str(e)}")
    
    def update_config(self, database_config: Dict[str, Any]):
        """Update database configuration and reconnect"""
        self.db_config = database_config
        self.connect()
    
    def get_schema_info(self):
        """Get information schema from ClickHouse"""
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
        
        return self.run_sql(schema_sql)