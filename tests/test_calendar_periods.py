#!/usr/bin/env python3

"""
Test the specific "minggu lalu" (last week) fix
"""

import requests

BASE_URL = "http://localhost:8000"

def test_calendar_vs_rolling():
    """Test calendar periods vs rolling periods"""
    
    print("🗓️  Testing Calendar vs Rolling Periods")
    print("=" * 50)
    
    test_cases = [
        {
            "question": "Berapa banyak pesanan yang dibuat minggu lalu?",
            "description": "Last week (calendar week)",
            "expected_pattern": "toStartOfWeek(today() - 7)",
            "should_contain": ["toStartOfWeek(today() - 7)", "< toStartOfWeek(today())"],
            "should_not_contain": ["toStartOfWeek(today()) - 7", "today() - 7"]
        },
        {
            "question": "Berapa banyak pesanan 7 hari terakhir?",
            "description": "Rolling 7 days",
            "expected_pattern": "today() - 7",
            "should_contain": ["today() - 7"],
            "should_not_contain": ["toStartOfWeek"]
        },
        {
            "question": "Pesanan bulan lalu",
            "description": "Last month (calendar month)",
            "expected_pattern": "toMonth(created_date) = toMonth(today()) - 1",
            "should_contain": ["toMonth(created_date) = toMonth(today()) - 1"],
            "should_not_contain": ["today() - 30"]
        }
    ]
    
    # Set ClickHouse context
    try:
        requests.put(f"{BASE_URL}/config/database-type/clickhouse")
        print("✅ ClickHouse context set")
    except:
        print("❌ Failed to set context")
        return
    
    print("\n" + "="*60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Question: {test['question']}")
        print(f"   Expected: {test['expected_pattern']}")
        
        try:
            response = requests.post(f"{BASE_URL}/sql", 
                json={"question": test['question']})
            
            if response.status_code == 200:
                sql = response.json()['sql']
                print(f"   Generated: {sql}")
                
                # Check required patterns
                missing = []
                for required in test['should_contain']:
                    if required not in sql:
                        missing.append(required)
                
                # Check forbidden patterns
                forbidden_found = []
                for forbidden in test['should_not_contain']:
                    if forbidden in sql:
                        forbidden_found.append(forbidden)
                
                if not missing and not forbidden_found:
                    print(f"   ✅ CORRECT: Proper {test['description'].lower()}")
                else:
                    print(f"   ❌ WRONG:")
                    if missing:
                        print(f"      Missing: {missing}")
                    if forbidden_found:
                        print(f"      Found wrong pattern: {forbidden_found}")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def explain_difference():
    """Explain the difference between calendar and rolling periods"""
    
    print("\n📚 Calendar vs Rolling Period Examples")
    print("=" * 50)
    print()
    print("Scenario: Today is Wednesday, Oct 2, 2024")
    print()
    print("❌ WRONG (Rolling 7 days):")
    print("   'minggu lalu' → Sep 25 to Oct 2")
    print("   SQL: WHERE created_date >= today() - 7")
    print("   Problem: This is NOT last week, it's past 7 days")
    print()
    print("✅ CORRECT (Calendar week):")
    print("   'minggu lalu' → Sep 23 (Mon) to Sep 29 (Sun)")  
    print("   SQL: WHERE created_date >= toStartOfWeek(today() - 7) AND created_date < toStartOfWeek(today())")
    print("   Result: Exact previous Monday-Sunday week")
    print()
    print("🎯 Key insight:")
    print("   toStartOfWeek(today() - 7) = Start of last week (Mon)")
    print("   toStartOfWeek(today())     = Start of this week (Mon)")
    print("   So we get: last Monday to this Monday (exclusive)")

if __name__ == "__main__":
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            test_calendar_vs_rolling()
            explain_difference()
        else:
            print("❌ Server not healthy")
    except:
        print("❌ Server not running. Start with: python main.py")