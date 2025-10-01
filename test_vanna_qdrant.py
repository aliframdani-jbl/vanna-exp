#!/usr/bin/env python3
"""
Test script for Vanna with Qdrant + ClickHouse implementation
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test hea    print("💡 Tips:")
    print("   - Make sure Qdrant and ClickHouse are running")
    print("   - Verify your Qwen API key is set (QWEN_API_KEY or DASHSCOPE_API_KEY)")
    print("   - Check the API logs for more details")endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_train_schema():
    """Test training from database schema"""
    print("\n🔍 Testing schema training...")
    try:
        response = requests.post(f"{BASE_URL}/train/schema")
        if response.status_code == 200:
            result = response.json()
            print("✅ Schema training successful")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Plan items: {result.get('plan_items', 'Unknown')}")
            return True
        else:
            print(f"❌ Schema training failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Schema training error: {e}")
        return False

def test_train_ddl():
    """Test training with DDL"""
    print("\n🔍 Testing DDL training...")
    
    ddl = """
    CREATE TABLE vanna_demo.customers (
        id UInt32,
        name String,
        email String,
        country String,
        created_date Date
    ) ENGINE = MergeTree()
    ORDER BY id
    """
    
    data = {
        "ddl": ddl
    }
    
    try:
        response = requests.post(f"{BASE_URL}/train", json=data)
        if response.status_code == 200:
            print("✅ DDL training successful")
            result = response.json()
            print(f"   Results: {len(result.get('training_results', []))} items trained")
            return True
        else:
            print(f"❌ DDL training failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ DDL training error: {e}")
        return False

def test_train_documentation():
    """Test training with documentation"""
    print("\n🔍 Testing documentation training...")
    
    data = {
        "documentation": "The customers table contains customer information including their name, email, country, and registration date. The orders table tracks customer purchases with product names, quantities, prices, and order dates."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/train", json=data)
        if response.status_code == 200:
            print("✅ Documentation training successful")
            return True
        else:
            print(f"❌ Documentation training failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Documentation training error: {e}")
        return False

def test_train_sql_pairs():
    """Test training with question-SQL pairs"""
    print("\n🔍 Testing question-SQL pairs training...")
    
    data = {
        "question": [
            "How many customers are there?",
            "What are the total sales?"
        ],
        "sql": [
            "SELECT COUNT(*) FROM vanna_demo.customers",
            "SELECT SUM(price * quantity) FROM vanna_demo.orders"
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/train", json=data)
        if response.status_code == 200:
            print("✅ Question-SQL pairs training successful")
            result = response.json()
            print(f"   Results: {len(result.get('training_results', []))} pairs trained")
            return True
        else:
            print(f"❌ Question-SQL pairs training failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Question-SQL pairs training error: {e}")
        return False

def test_get_training_data():
    """Test getting training data"""
    print("\n🔍 Testing get training data...")
    try:
        response = requests.get(f"{BASE_URL}/training-data")
        if response.status_code == 200:
            result = response.json()
            training_data = result.get('training_data', [])
            print(f"✅ Retrieved {len(training_data)} training records")
            
            # Show sample training data
            if training_data:
                print("   Sample training data:")
                for i, data in enumerate(training_data[:3]):  # Show first 3
                    print(f"     {i+1}. ID: {data.get('id', 'N/A')}, Type: {data.get('training_data_type', 'N/A')}")
            
            return True
        else:
            print(f"❌ Get training data failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get training data error: {e}")
        return False

def test_generate_sql():
    """Test SQL generation"""
    print("\n🔍 Testing SQL generation...")
    
    questions = [
        "How many customers do we have?",
        "What are the total sales by country?",
        "Show me the top 3 customers by order value"
    ]
    
    success_count = 0
    for question in questions:
        print(f"\n   Question: '{question}'")
        try:
            data = {"question": question}
            response = requests.post(f"{BASE_URL}/sql", json=data)
            
            if response.status_code == 200:
                result = response.json()
                sql = result.get('sql', '')
                print(f"   ✅ Generated SQL: {sql[:100]}{'...' if len(sql) > 100 else ''}")
                success_count += 1
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ SQL generation: {success_count}/{len(questions)} successful")
    return success_count > 0

def test_ask_questions():
    """Test asking questions (SQL generation + execution)"""
    print("\n🔍 Testing question answering...")
    
    questions = [
        "How many customers do we have?",
        "What are the total sales?"
    ]
    
    success_count = 0
    for question in questions:
        print(f"\n   Question: '{question}'")
        try:
            data = {"question": question}
            response = requests.post(f"{BASE_URL}/ask", json=data)
            
            if response.status_code == 200:
                result = response.json()
                sql = result.get('sql', '')
                results = result.get('results', {})
                error = result.get('error')
                
                if error:
                    print(f"   ❌ Error in result: {error}")
                else:
                    print(f"   ✅ SQL: {sql}")
                    print(f"   ✅ Results: {results.get('row_count', 0)} rows")
                    if results.get('data'):
                        print(f"   ✅ Sample data: {results['data'][:2]}")  # Show first 2 rows
                    success_count += 1
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Question answering: {success_count}/{len(questions)} successful")
    return success_count > 0

def main():
    """Run all tests"""
    print("🚀 Testing Vanna with Qdrant + ClickHouse")
    print("=" * 50)
    
    # Check if Qwen API key is set
    qwen_key = os.getenv('QWEN_API_KEY') or os.getenv('DASHSCOPE_API_KEY')
    if not qwen_key:
        print("❌ QWEN_API_KEY or DASHSCOPE_API_KEY not set in environment")
        print("   Please set it in your .env file")
        return
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Schema Training", test_train_schema),
        ("DDL Training", test_train_ddl),
        ("Documentation Training", test_train_documentation),
        ("Question-SQL Pairs Training", test_train_sql_pairs),
        ("Get Training Data", test_get_training_data),
        ("SQL Generation", test_generate_sql),
        ("Question Answering", test_ask_questions),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
        
        # Small delay between tests
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Vanna + Qdrant + ClickHouse setup is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    print("\n💡 Tips:")
    print("   - Make sure Qdrant and ClickHouse are running")
    print("   - Verify your OpenAI API key is set")
    print("   - Check the API logs for more details")

if __name__ == "__main__":
    main()