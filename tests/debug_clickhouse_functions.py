#!/usr/bin/env python3

"""
Test script to debug ClickHouse function generation issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_clickhouse_functions():
    """Test ClickHouse-specific function generation"""
    
    print("🔍 Testing ClickHouse Function Generation")
    print("=" * 50)
    
    # Test questions that should use specific ClickHouse functions
    test_cases = [
        {
            "question": "Berapa total pendapatan tahun ini?",
            "expected_functions": ["toYear(", "now()"],
            "avoid_functions": ["toYYYY", "year(", "YEAR("]
        },
        {
            "question": "Show sales by month this year",
            "expected_functions": ["toMonth(", "toYear("],
            "avoid_functions": ["toMM", "month(", "MONTH("]
        },
        {
            "question": "Count unique customers",
            "expected_functions": ["uniq("],
            "avoid_functions": ["COUNT DISTINCT", "count distinct"]
        },
        {
            "question": "Convert date to string format",
            "expected_functions": ["toString("],
            "avoid_functions": ["CAST(", "str("]
        }
    ]
    
    # First, ensure we're using ClickHouse context
    print("1. Setting database type to ClickHouse...")
    try:
        response = requests.put(f"{BASE_URL}/config/database-type/clickhouse")
        if response.status_code == 200:
            print("✅ ClickHouse context set successfully")
            context_data = response.json()
            print(f"   Context: {context_data['context']['system_prompt'][:100]}...")
        else:
            print(f"❌ Failed to set ClickHouse context: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error setting context: {e}")
        return
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['question']}")
        
        try:
            # Generate SQL
            sql_response = requests.post(f"{BASE_URL}/sql", 
                json={"question": test_case['question']})
            
            if sql_response.status_code == 200:
                sql_data = sql_response.json()
                generated_sql = sql_data['sql']
                print(f"   📝 Generated SQL: {generated_sql}")
                
                # Check for expected functions
                found_expected = []
                for func in test_case['expected_functions']:
                    if func in generated_sql:
                        found_expected.append(func)
                        print(f"   ✅ Found expected function: {func}")
                    else:
                        print(f"   ❌ Missing expected function: {func}")
                
                # Check for functions to avoid
                found_avoided = []
                for func in test_case['avoid_functions']:
                    if func in generated_sql:
                        found_avoided.append(func)
                        print(f"   ❌ Found unwanted function: {func}")
                    else:
                        print(f"   ✅ Correctly avoided: {func}")
                
                # Overall assessment
                if len(found_expected) == len(test_case['expected_functions']) and len(found_avoided) == 0:
                    print(f"   🎉 PASS: Correct ClickHouse syntax!")
                else:
                    print(f"   ⚠️  FAIL: Incorrect function usage")
                    
            else:
                print(f"   ❌ Failed to generate SQL: {sql_response.status_code}")
                if sql_response.text:
                    print(f"      Error: {sql_response.text}")
                    
        except Exception as e:
            print(f"   ❌ Error testing case: {e}")

def test_database_context_debugging():
    """Test and debug the current database context"""
    
    print("\n🔧 Database Context Debugging")
    print("=" * 40)
    
    try:
        # Get current context
        response = requests.get(f"{BASE_URL}/config/database-type")
        if response.status_code == 200:
            data = response.json()
            print(f"Current database type: {data['current_database_type']}")
            
            if 'current_context' in data:
                context = data['current_context']
                print(f"\nSystem prompt preview:")
                print(f"{context.get('system_prompt', 'No system prompt')[:300]}...")
                
                print(f"\nConstraints:")
                for constraint in context.get('constraints', []):
                    print(f"  - {constraint}")
            else:
                print("No context information available")
        else:
            print(f"Failed to get context: {response.status_code}")
    except Exception as e:
        print(f"Error getting context: {e}")

def main():
    """Main test function"""
    
    print("🧪 ClickHouse Function Generation Debug Test")
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
    test_database_context_debugging()
    test_clickhouse_functions()
    
    print("\n" + "=" * 60)
    print("🎯 Debugging Summary:")
    print("If tests fail, check:")
    print("1. System prompt is being applied correctly")
    print("2. Database type is set to 'clickhouse'")
    print("3. LLM is following the specific function constraints")
    print("4. Debug logs show the full system message")

if __name__ == "__main__":
    main()