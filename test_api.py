#!/usr/bin/env python3
"""
Simple test script for the Text2SQL API
"""

import requests
import json


def test_api(base_url="http://localhost:8000"):
    print(f"Testing Text2SQL API at {base_url}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Root endpoint failed: {e}")
    
    # Test SQL generation
    try:
        query_data = {
            "question": "Show me all tables in the database"
        }
        response = requests.post(f"{base_url}/sql", json=query_data)
        print(f"SQL generation: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"SQL generation failed: {e}")
    
    # Test ask endpoint
    try:
        query_data = {
            "question": "How many rows are in each table?"
        }
        response = requests.post(f"{base_url}/ask", json=query_data)
        print(f"Ask endpoint: {response.status_code}")
        result = response.json()
        print(f"SQL: {result.get('sql', 'N/A')}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        else:
            print(f"Results: {result.get('results', 'N/A')}")
    except Exception as e:
        print(f"Ask endpoint failed: {e}")


if __name__ == "__main__":
    test_api()
