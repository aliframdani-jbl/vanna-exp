#!/usr/bin/env python3
"""
Example usage of the Text2SQL API
"""

import requests
import json
import time


class Text2SQLClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def ask_question(self, question, database_config=None):
        """Ask a natural language question"""
        data = {"question": question}
        if database_config:
            data["database_config"] = database_config
        
        response = requests.post(f"{self.base_url}/ask", json=data)
        return response.json()
    
    def generate_sql(self, question, database_config=None):
        """Generate SQL without executing"""
        data = {"question": question}
        if database_config:
            data["database_config"] = database_config
        
        response = requests.post(f"{self.base_url}/sql", json=data)
        return response.json()
    
    def execute_sql(self, sql, database_config=None):
        """Execute SQL directly"""
        data = {"sql": sql}
        if database_config:
            data["database_config"] = database_config
        
        response = requests.post(f"{self.base_url}/execute", json=data)
        return response.json()
    
    def train_model(self, ddl=None, documentation=None, question=None, sql=None):
        """Train the model"""
        data = {}
        if ddl:
            data["ddl"] = ddl
        if documentation:
            data["documentation"] = documentation
        if question:
            data["question"] = question
        if sql:
            data["sql"] = sql
        
        response = requests.post(f"{self.base_url}/train", json=data)
        return response.json()


def example_usage():
    """Example usage of the API"""
    client = Text2SQLClient()
    
    # Check if API is running
    if not client.health_check():
        print("❌ API is not running. Please start it first with: ./start.sh")
        return
    
    print("✅ API is running!")
    print()
    
    # Example 1: Generate SQL only
    print("🔍 Example 1: Generate SQL only")
    question = "Show me all tables in the database"
    result = client.generate_sql(question)
    print(f"Question: {question}")
    print(f"Generated SQL: {result.get('sql', 'Error: ' + str(result))}")
    print()
    
    # Example 2: Ask a question (SQL + execution)
    print("🚀 Example 2: Ask a question and execute")
    question = "How many tables are there in the database?"
    result = client.ask_question(question)
    print(f"Question: {question}")
    print(f"Generated SQL: {result.get('sql', 'N/A')}")
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print(f"Results: {result.get('results', 'N/A')}")
    print()
    
    # Example 3: Train the model with sample data
    print("📚 Example 3: Train the model")
    training_result = client.train_model(
        ddl="CREATE TABLE users (id UInt32, name String, email String, created_at DateTime) ENGINE = MergeTree() ORDER BY id",
        documentation="The users table contains customer registration information including their contact details and registration timestamp",
        question="How many users registered today?",
        sql="SELECT COUNT(*) FROM users WHERE toDate(created_at) = today()"
    )
    print("Training result:")
    print(json.dumps(training_result, indent=2))
    print()
    
    # Example 4: Use custom database config
    print("🔧 Example 4: Use custom database configuration")
    custom_db_config = {
        "host": "localhost",
        "port": 8123,
        "user": "default",
        "password": "",
        "database": "default"
    }
    
    question = "Show me the current date and time"
    result = client.ask_question(question, database_config=custom_db_config)
    print(f"Question: {question}")
    print(f"Generated SQL: {result.get('sql', 'N/A')}")
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print(f"Results: {result.get('results', 'N/A')}")


if __name__ == "__main__":
    print("🤖 Text2SQL API Example Usage")
    print("=" * 50)
    example_usage()
