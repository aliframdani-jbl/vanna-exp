#!/usr/bin/env python3

"""
Test script to validate temporal expression fixes
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_temporal_expressions():
    """Test precise temporal expression handling"""
    
    print("🕒 Testing Temporal Expression Precision")
    print("=" * 60)
    
    test_cases = [
        {
            "question": "Berapa banyak pesanan 7 hari terakhir?",
            "description": "Rolling 7 days (past 7×24 hours)",
            "expected_pattern": "WHERE created_date >= today() - 7",
            "should_contain": ["internal.realtime_order", "today() - 7"],
            "should_not_contain": ["toStartOfWeek", "INTERVAL"]
        },
        {
            "question": "Berapa banyak pesanan minggu lalu?", 
            "description": "Calendar week (previous Mon-Sun)",
            "expected_pattern": "WHERE created_date >= toStartOfWeek(today()) - 7 AND created_date < toStartOfWeek(today())",
            "should_contain": ["internal.realtime_order", "toStartOfWeek(today()) - 7", "< toStartOfWeek(today())"],
            "should_not_contain": ["today() - 7", "INTERVAL"]
        },
        {
            "question": "Berapa total pendapatan tahun ini?",
            "description": "Current calendar year",
            "expected_pattern": "WHERE toYear(created_date) = toYear(now())",
            "should_contain": ["internal.realtime_order", "grand_total", "toYear(created_date) = toYear(now())"],
            "should_not_contain": ["toYYYY", "pendapatan", "tanggal"]
        },
        {
            "question": "Pesanan minggu ini",
            "description": "Current week (from Monday)",
            "expected_pattern": "WHERE created_date >= toStartOfWeek(today())",
            "should_contain": ["internal.realtime_order", "toStartOfWeek(today())"],
            "should_not_contain": ["today() - 7", "INTERVAL"]
        },
        {
            "question": "Siapa 5 perusahaan teratas berdasarkan total nilai pesanan?",
            "description": "Top companies query",
            "expected_pattern": "GROUP BY company_name ORDER BY total DESC LIMIT 5",
            "should_contain": ["internal.realtime_order", "company_name", "grand_total", "GROUP BY", "ORDER BY", "LIMIT 5"],
            "should_not_contain": ["orders", "order_value"]
        }
    ]
    
    # Ensure ClickHouse context
    print("🔧 Setting ClickHouse context...")
    try:
        response = requests.put(f"{BASE_URL}/config/database-type/clickhouse")
        if response.status_code == 200:
            print("✅ ClickHouse context set successfully")
        else:
            print(f"❌ Failed to set context: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error setting context: {e}")
        return
    
    print("\n" + "="*60)
    
    passed = 0
    failed = 0
    
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
                
                # Check required elements
                missing = []
                for required in test['should_contain']:
                    if required not in sql:
                        missing.append(required)
                
                # Check forbidden elements
                forbidden_found = []
                for forbidden in test['should_not_contain']:
                    if forbidden in sql:
                        forbidden_found.append(forbidden)
                
                # Evaluate result
                if not missing and not forbidden_found:
                    print(f"   ✅ PASS: Correct temporal pattern")
                    passed += 1
                else:
                    print(f"   ❌ FAIL:")
                    if missing:
                        print(f"      Missing: {missing}")
                    if forbidden_found:
                        print(f"      Found forbidden: {forbidden_found}")
                    failed += 1
            else:
                print(f"   ❌ API Error: {response.status_code} - {response.text}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All temporal expressions are working correctly!")
    else:
        print("⚠️  Some temporal expressions need adjustment")
        print("\nRecommendations:")
        print("1. Check database_prompts.py for correct patterns")
        print("2. Ensure examples match expected output")
        print("3. Validate ClickHouse function usage")

def test_edge_cases():
    """Test edge cases and ambiguous queries"""
    
    print("\n🎯 Testing Edge Cases")
    print("=" * 40)
    
    edge_cases = [
        {
            "question": "orders last 7 days",  # English
            "note": "Should handle English input"
        },
        {
            "question": "pesanan seminggu yang lalu",  # Alternative phrasing
            "note": "Alternative Indonesian phrasing"
        },
        {
            "question": "berapa order bulan lalu",  # Mixed language
            "note": "Should handle mixed Indonesian/English"
        }
    ]
    
    for case in edge_cases:
        print(f"\nTesting: {case['question']} ({case['note']})")
        try:
            response = requests.post(f"{BASE_URL}/sql", 
                json={"question": case['question']})
            if response.status_code == 200:
                sql = response.json()['sql']
                print(f"Generated: {sql}")
                
                # Basic validation
                if "internal.realtime_order" in sql:
                    print("✅ Correct table name")
                else:
                    print("❌ Wrong table name")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            test_temporal_expressions()
            test_edge_cases()
        else:
            print("❌ Server not healthy")
    except:
        print("❌ Server not running. Start with: python main.py")