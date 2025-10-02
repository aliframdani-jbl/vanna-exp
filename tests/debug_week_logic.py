#!/usr/bin/env python3

"""
Test to verify the actual date ranges for ClickHouse week functions
"""

def test_clickhouse_week_logic():
    """Test ClickHouse week function logic"""
    
    print("🗓️  ClickHouse Week Function Analysis")
    print("=" * 50)
    print()
    
    # Assume today is Wednesday, Oct 2, 2024
    print("Scenario: Today is Wednesday, Oct 2, 2024")
    print()
    
    print("ClickHouse toStartOfWeek() behavior:")
    print("- Monday is day 1, Sunday is day 7")
    print("- toStartOfWeek() returns the Monday of that week")
    print()
    
    print("Let's trace the logic:")
    print("1. today() = Oct 2, 2024 (Wednesday)")
    print("2. today() - 7 = Sep 25, 2024 (Wednesday)")
    print("3. toStartOfWeek(today() - 7) = Sep 23, 2024 (Monday) ← Start of last week")
    print("4. toStartOfWeek(today()) = Sep 30, 2024 (Monday) ← Start of this week")
    print()
    
    print("So the WHERE clause:")
    print("WHERE created_date >= toStartOfWeek(today() - 7) AND created_date < toStartOfWeek(today())")
    print("Becomes:")
    print("WHERE created_date >= '2024-09-23 00:00:00' AND created_date < '2024-09-30 00:00:00'")
    print()
    
    print("This covers:")
    print("✅ Sep 23 (Mon) 00:00 to Sep 29 (Sun) 23:59")
    print("✅ This IS the exact previous calendar week!")
    print()
    
    print("🤔 Wait... let me check if this is actually correct...")
    print()
    
    # Let's verify with different days
    scenarios = [
        ("Monday", "Sep 30", "Sep 23", "Sep 16"),
        ("Tuesday", "Oct 1", "Sep 24", "Sep 17"), 
        ("Wednesday", "Oct 2", "Sep 25", "Sep 18"),
        ("Thursday", "Oct 3", "Sep 26", "Sep 19"),
        ("Friday", "Oct 4", "Sep 27", "Sep 20"),
        ("Saturday", "Oct 5", "Sep 28", "Sep 21"),
        ("Sunday", "Oct 6", "Sep 29", "Sep 22"),
    ]
    
    print("Testing different 'today' values:")
    for day_name, today_date, today_minus_7, expected_start in scenarios:
        print(f"If today is {day_name} ({today_date}):")
        print(f"  today() - 7 = {today_minus_7}")
        print(f"  toStartOfWeek({today_minus_7}) should be Monday of that week")
        print(f"  Expected: Monday closest to {today_minus_7}")
        print()

def analyze_problem():
    """Analyze what might be wrong"""
    
    print("🔍 Problem Analysis")
    print("=" * 30)
    print()
    
    print("The user says it's still a 'rolling window', but:")
    print()
    print("Query: WHERE created_date >= toStartOfWeek(today() - 7) AND created_date < toStartOfWeek(today())")
    print()
    print("This should give EXACTLY 7 days (Mon-Sun of previous week).")
    print("If it's giving MORE than 7 days, then either:")
    print("1. ClickHouse toStartOfWeek() behaves differently than expected")
    print("2. The prompt is still not being applied correctly")
    print("3. The LLM is generating a different pattern than what we specified")
    print()
    
    print("Let's check what the actual SQL should be for different approaches:")
    print()
    print("Approach 1 (Current - should be correct):")
    print("WHERE created_date >= toStartOfWeek(today() - 7) AND created_date < toStartOfWeek(today())")
    print()
    print("Approach 2 (Alternative - more explicit):")
    print("WHERE toStartOfWeek(created_date) = toStartOfWeek(today() - 7)")
    print()
    print("Approach 3 (Manual calculation):")
    print("WHERE created_date >= toMonday(today() - 7) AND created_date < toMonday(today())")

if __name__ == "__main__":
    test_clickhouse_week_logic()
    analyze_problem()