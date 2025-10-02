#!/usr/bin/env python3

"""
Test script to demonstrate database type configuration for Vanna
This shows how to switch between different database syntaxes
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_database_type_management():
    """Test database type configuration endpoints"""
    
    print("🚀 Testing Database Type Management")
    print("=" * 50)
    
    # Test 1: Get current database type
    print("\n1. Getting current database type...")
    try:
        response = requests.get(f"{BASE_URL}/config/database-type")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current database type: {data['current_database_type']}")
            print(f"   Available types: {', '.join(data['available_types'])}")
        else:
            print(f"❌ Failed to get database type: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting database type: {e}")
        return
    
    # Test 2: Get all database contexts
    print("\n2. Getting all database contexts...")
    try:
        response = requests.get(f"{BASE_URL}/config/database-contexts")
        if response.status_code == 200:
            data = response.json()
            print("✅ Available database contexts:")
            for db_type, context in data['database_contexts'].items():
                print(f"   📋 {db_type.upper()}:")
                print(f"      System Prompt: {context['system_prompt'][:100]}...")
                print(f"      Constraints: {len(context['constraints'])} rules")
        else:
            print(f"❌ Failed to get database contexts: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting database contexts: {e}")
    
    # Test 3: Test SQL generation with different database types
    print("\n3. Testing SQL generation with different database types...")
    
    test_question = "Show me the top 5 products by sales amount"
    
    database_types = ['clickhouse', 'mysql', 'postgresql', 'sqlite']
    
    for db_type in database_types:
        print(f"\n   🔄 Testing {db_type.upper()} syntax...")
        
        # Switch database type
        try:
            response = requests.put(f"{BASE_URL}/config/database-type/{db_type}")
            if response.status_code == 200:
                print(f"   ✅ Switched to {db_type}")
                
                # Generate SQL
                time.sleep(1)  # Small delay to ensure context is updated
                sql_response = requests.post(f"{BASE_URL}/sql", 
                    json={"question": test_question})
                
                if sql_response.status_code == 200:
                    sql_data = sql_response.json()
                    print(f"   📝 Generated SQL:")
                    print(f"      {sql_data['sql']}")
                else:
                    print(f"   ❌ Failed to generate SQL: {sql_response.status_code}")
                    if sql_response.text:
                        print(f"      Error: {sql_response.text}")
            else:
                print(f"   ❌ Failed to switch to {db_type}: {response.status_code}")
                print(f"      Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error testing {db_type}: {e}")
    
    # Test 4: Switch back to original database type
    print(f"\n4. Switching back to ClickHouse...")
    try:
        response = requests.put(f"{BASE_URL}/config/database-type/clickhouse")
        if response.status_code == 200:
            print("✅ Switched back to ClickHouse")
        else:
            print(f"❌ Failed to switch back: {response.status_code}")
    except Exception as e:
        print(f"❌ Error switching back: {e}")

def test_invalid_database_type():
    """Test error handling for invalid database types"""
    
    print("\n🧪 Testing Invalid Database Type")
    print("=" * 40)
    
    try:
        response = requests.put(f"{BASE_URL}/config/database-type/invalid_db")
        if response.status_code == 400:
            print("✅ Correctly rejected invalid database type")
            print(f"   Error message: {response.json()['detail']}")
        else:
            print(f"❌ Unexpected response for invalid type: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing invalid type: {e}")

def main():
    """Main test function"""
    
    print("🔧 Vanna Database Type Configuration Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not running or not healthy")
            print("   Please start the server with: python main.py")
            return
        print("✅ Server is running and healthy")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Please start the server with: python main.py")
        return
    
    # Run tests
    test_database_type_management()
    test_invalid_database_type()
    
    print("\n" + "=" * 60)
    print("🎉 Database type configuration test completed!")
    print("\nUsage Examples:")
    print("• GET  /config/database-type           - Get current database type")
    print("• PUT  /config/database-type/{type}    - Switch database type")
    print("• GET  /config/database-contexts       - Get all contexts")
    print("\nSupported database types:")
    print("• clickhouse  - ClickHouse syntax (default)")
    print("• mysql       - MySQL syntax")
    print("• postgresql  - PostgreSQL syntax") 
    print("• sqlite      - SQLite syntax")

if __name__ == "__main__":
    main()