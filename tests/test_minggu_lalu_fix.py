#!/usr/bin/env python3

"""
Test the specific "minggu lalu" fix with the new approach
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_minggu_lalu_fix():
    """Test the exact minggu lalu query pattern"""
    
    print("🎯 Testing 'Minggu Lalu' Fix")
    print("=" * 40)
    
    question = "Berapa banyak pesanan yang dibuat minggu lalu?"
    
    print(f"Question: {question}")
    print()
    
    # Set ClickHouse context
    try:
        requests.put(f"{BASE_URL}/config/database-type/clickhouse")
        print("✅ ClickHouse context set")
    except:
        print("❌ Failed to set context - is server running?")
        return
    
    try:
        response = requests.post(f"{BASE_URL}/sql", 
            json={"question": question})
        
        if response.status_code == 200:
            sql = response.json()['sql']
            print(f"Generated SQL: {sql}")
            print()
            
            # Check for the correct pattern
            expected_pattern = "toStartOfWeek(created_date) = toStartOfWeek(today() - 7)"
            
            if expected_pattern in sql:
                print("✅ CORRECT: Using exact week comparison")
                print("   This will return ONLY the previous calendar week (Mon-Sun)")
            elif "toStartOfWeek(today() - 7)" in sql and "toStartOfWeek(today())" in sql:
                print("⚠️  PARTIAL: Using range approach")
                print("   This should still work but is more verbose")
            elif "today() - 7" in sql and "toStartOfWeek" not in sql:
                print("❌ WRONG: Using rolling 7 days")
                print("   This is NOT 'minggu lalu', it's '7 hari terakhir'")
            else:
                print("❌ UNKNOWN: Unexpected pattern")
            
            print()
            print("Expected pattern:")
            print("SELECT COUNT(*) FROM internal.realtime_order") 
            print("WHERE toStartOfWeek(created_date) = toStartOfWeek(today() - 7)")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def explain_fix():
    """Explain the fix"""
    
    print("\n📚 The Fix Explained")
    print("=" * 30)
    print()
    print("OLD approach (problematic):")
    print("WHERE created_date >= toStartOfWeek(today() - 7) AND created_date < toStartOfWeek(today())")
    print("→ Range-based, could be confusing")
    print()
    print("NEW approach (clear):")
    print("WHERE toStartOfWeek(created_date) = toStartOfWeek(today() - 7)")
    print("→ Direct comparison: 'created_date is in the same week as 7 days ago'")
    print()
    print("Benefits of new approach:")
    print("✅ More explicit intent")
    print("✅ Cleaner SQL")
    print("✅ Harder to misinterpret")
    print("✅ Directly expresses 'same week as last week'")

if __name__ == "__main__":
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            test_minggu_lalu_fix()
            explain_fix()
        else:
            print("❌ Server not healthy")
    except:
        print("❌ Server not running. Start with: python main.py")