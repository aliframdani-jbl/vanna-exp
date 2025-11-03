import re
from typing import List, Set


class SchemaExtractor:
    """Utility class for extracting schema information from DDL training data"""
    
    def __init__(self, vn_client):
        self.vn = vn_client
    
    def get_known_columns_from_ddl(self) -> List[str]:
        """Extract known column names from DDL training data"""
        try:
            # Get DDL data from training
            training_data = self.vn.get_training_data()
            if hasattr(training_data, 'to_dict'):
                training_records = training_data.to_dict('records')
            else:
                training_records = training_data if isinstance(training_data, list) else []
            
            columns = set()
            for record in training_records:
                if record.get('training_data_type') == 'ddl':
                    ddl_content = record.get('content', '')
                    # Extract column names from CREATE TABLE statements (basic regex)
                    # Look for column definitions in CREATE TABLE
                    column_matches = re.findall(
                        r'(\w+)\s+(?:UInt32|UInt64|String|DateTime|Int8|Int32|Int64|Bool|LowCardinality|Array)', 
                        ddl_content
                    )
                    columns.update(column_matches)
            
            return list(columns)
        except Exception as e:
            print(f"Error extracting columns from DDL: {e}")
            return []

    def get_known_tables_from_ddl(self) -> List[str]:
        """Extract known table names from DDL training data"""
        try:
            # Get DDL data from training
            training_data = self.vn.get_training_data()
            if hasattr(training_data, 'to_dict'):
                training_records = training_data.to_dict('records')
            else:
                training_records = training_data if isinstance(training_data, list) else []
            
            tables = set()
            for record in training_records:
                if record.get('training_data_type') == 'ddl':
                    ddl_content = record.get('content', '')
                    # Extract table names from CREATE TABLE statements
                    table_matches = re.findall(r'CREATE TABLE\s+(\S+)\s*\(', ddl_content, re.IGNORECASE)
                    tables.update(table_matches)
            
            return list(tables)
        except Exception as e:
            print(f"Error extracting tables from DDL: {e}")
            return []
    
    def get_known_tables_set(self) -> Set[str]:
        """Get known tables as a set for faster lookups"""
        return set([t.lower() for t in self.get_known_tables_from_ddl()])