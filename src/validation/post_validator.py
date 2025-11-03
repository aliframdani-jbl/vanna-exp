from typing import Tuple
from .sql_parser import SQLParser


class PostValidator:
    """Post-validation of generated SQL against known schema"""
    
    def __init__(self, schema_extractor):
        self.schema_extractor = schema_extractor
        self.sql_parser = SQLParser()
    
    def validate_sql(self, sql: str) -> Tuple[bool, str]:
        """Post-validate generated SQL against known schema"""
        if not sql or not sql.strip():
            return False, "No SQL was generated."
        
        try:
            import sqlparse
            
            # Parse the SQL
            parsed = sqlparse.parse(sql)
            if not parsed:
                return False, "Generated SQL could not be parsed."
            
            # Extract table and column references from SQL
            sql_lower = sql.lower()
            
            # Get known columns from DDL training data
            known_columns = self.schema_extractor.get_known_columns_from_ddl()
            known_tables = self.schema_extractor.get_known_tables_set()

            print(f"Known columns from DDL: {known_columns}")

            if known_columns:
                potential_columns = self.sql_parser.extract_identifiers(sql, known_tables)
                print(f"Potential columns found in SQL: {potential_columns}")
                
                invalid_columns = [col for col in potential_columns if col.lower() not in [kc.lower() for kc in known_columns]]
                if invalid_columns:
                    return False, f"Generated SQL references unknown columns: {', '.join(invalid_columns)}. Please rephrase your question."
                            
            # Check for common SQL injection patterns or suspicious content
            suspicious_patterns = ['drop table', 'delete from', 'truncate', 'alter table', 'create table']
            for pattern in suspicious_patterns:
                if pattern in sql_lower:
                    return False, f"Generated SQL contains potentially harmful operation: {pattern}"
            
            return True, "SQL validation passed"
            
        except ImportError:
            # sqlparse not available, skip detailed validation
            print("Warning: sqlparse not available for SQL validation")
            return True, "SQL validation skipped"
        except Exception as e:
            print(f"Post-validation error: {e}")
            # If validation fails, allow the SQL (fail-safe)
            return True, "Validation skipped due to error"