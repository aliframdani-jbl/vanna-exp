import sqlparse
from sqlparse.tokens import Name, Keyword, Whitespace, Punctuation
from typing import List, Set


class SQLParser:
    """SQL parsing utilities for extracting identifiers and validating SQL structure"""
    
    def __init__(self):
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 'LIMIT', 'AS', 'DESC', 'ASC', 
            'AND', 'OR', 'NOT', 'IN', 'ON', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'FULL', 
            'UNION', 'ALL', 'DISTINCT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'IS', 'NULL', 
            'BETWEEN', 'LIKE', 'HAVING', 'EXISTS', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'NOW', 
            'INTERVAL', 'MONTH', 'DAY', 'YEAR', 'HOUR', 'MINUTE', 'SECOND', 'DATE', 'TIME',
            'CONCAT', 'SUBSTRING', 'UPPER', 'LOWER', 'TRIM', 'LENGTH', 'COALESCE', 'IFNULL',
            'CAST', 'CONVERT', 'ROUND', 'FLOOR', 'CEIL', 'ABS', 'MOD', 'SQRT', 'POWER'
        }
    
    def extract_identifiers(self, sql: str, known_tables: Set[str]) -> List[str]:
        """Extract only column names from SQL, filtering out keywords, functions, table names, and aliases"""
        try:
            column_names = set()
            defined_aliases = set()
            
            # Parse the SQL and get all tokens
            parsed = sqlparse.parse(sql)
            for statement in parsed:
                tokens = list(statement.flatten())
                
                # First pass: collect all defined aliases
                for i, token in enumerate(tokens):
                    if (token.ttype is Name and token.value.strip() and 
                        self._is_alias(tokens, i)):
                        defined_aliases.add(token.value.strip().lower())
                
                # Second pass: extract column names
                for i, token in enumerate(tokens):
                    if token.ttype is Name and token.value.strip():
                        name = token.value.strip()
                        
                        # Skip if it's a SQL keyword or function
                        if name.upper() in self.sql_keywords:
                            continue
                            
                        # Skip if it's a number or too short
                        if name.isdigit() or len(name) <= 1:
                            continue
                        
                        # Check if it's part of schema.table reference
                        if self._is_schema_table_reference(tokens, i):
                            continue
                        
                        # Check if it's a table name (with or without schema)
                        if self._is_table_reference(name, known_tables):
                            continue
                            
                        # Check if it's an alias (preceded by AS or follows a column/expression)
                        if self._is_alias(tokens, i):
                            continue
                            
                        # Check if it's a function name (followed by opening parenthesis)
                        if self._is_function_name(tokens, i):
                            continue
                        
                        # Check if it's a reference to a previously defined alias
                        if name.lower() in defined_aliases:
                            continue
                            
                        # If it passes all filters, it's likely a column name
                        column_names.add(name)
            
            return list(column_names)
            
        except Exception as e:
            print(f"Error extracting identifiers: {e}")
            return []
    
    def _is_schema_table_reference(self, tokens: list, current_index: int) -> bool:
        """Check if the current token is part of a schema.table reference"""
        # Check if next token is a dot (schema.table pattern)
        if current_index + 1 < len(tokens):
            next_token = tokens[current_index + 1]
            if next_token.ttype is Punctuation and next_token.value == '.':
                return True  # This is the schema part
        
        # Check if previous token is a dot (schema.table pattern)
        if current_index > 0:
            prev_token = tokens[current_index - 1]
            if prev_token.ttype is Punctuation and prev_token.value == '.':
                return True  # This is the table part
        
        return False
    
    def _is_function_name(self, tokens: list, current_index: int) -> bool:
        """Check if the current token is a function name (followed by opening parenthesis)"""
        # Look for opening parenthesis after current token (skipping whitespace)
        for i in range(current_index + 1, min(len(tokens), current_index + 3)):
            if tokens[i].ttype is Punctuation and tokens[i].value == '(':
                return True
            elif tokens[i].ttype not in (None, Whitespace):
                break  # Found non-whitespace that's not parenthesis
        
        return False
    
    def _is_table_reference(self, name: str, known_tables: set) -> bool:
        """Check if name is a table reference (with or without schema)"""
        name_lower = name.lower()
        
        # Direct table name match
        if name_lower in known_tables:
            return True
            
        # Check if it's schema.table format
        if '.' in name:
            parts = name.split('.')
            if len(parts) == 2:
                # Check if the second part is a known table
                table_part = parts[1].lower()
                if table_part in known_tables:
                    return True
                # Also check full schema.table format
                if name_lower in known_tables:
                    return True
        
        return False
    
    def _is_alias(self, tokens: list, current_index: int) -> bool:
        """Check if the current token is an alias"""
        # Look for "AS" keyword before current token
        for i in range(max(0, current_index - 3), current_index):
            if (i < len(tokens) and 
                tokens[i].ttype is Keyword and 
                tokens[i].value.upper() == 'AS'):
                return True
        
        # Look for patterns like "column_name alias_name" (without AS)
        # Check if previous token could be a column/expression and this could be an alias
        if current_index > 0:
            prev_token = tokens[current_index - 1]
            # Skip whitespace to find actual previous token
            prev_index = current_index - 1
            while prev_index >= 0 and prev_token.ttype in (None, Whitespace):
                prev_index -= 1
                if prev_index >= 0:
                    prev_token = tokens[prev_index]
            
            # If previous token is a Name (could be column) or closing parenthesis (could be function)
            if (prev_token.ttype is Name or 
                (hasattr(prev_token, 'value') and prev_token.value == ')')):
                # Check if we're in SELECT clause context (this is a simple heuristic)
                # Look backwards for SELECT keyword
                for j in range(prev_index, -1, -1):
                    if (tokens[j].ttype is Keyword and 
                        tokens[j].value.upper() in ['SELECT', 'FROM', 'WHERE', 'GROUP', 'ORDER']):
                        if tokens[j].value.upper() == 'SELECT':
                            return True  # Likely an alias in SELECT clause
                        else:
                            break  # Hit another clause, not in SELECT
        
        return False