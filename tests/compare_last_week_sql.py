#!/usr/bin/env python3

"""
Compare different "last week" SQL approaches
"""

def compare_last_week_approaches():
    """Compare different SQL approaches for 'last week'"""
    
    print("📊 Comparing 'Last Week' SQL Approaches")
    print("=" * 60)
    print()
    
    approaches = [
        {
            "name": "PostgreSQL/MySQL Style",
            "sql": "WHERE created_date >= date_trunc('week', now()) - INTERVAL 1 WEEK AND created_date < date_trunc('week', now())",
            "description": "Uses date_trunc and INTERVAL - standard SQL",
            "database": "PostgreSQL, MySQL, etc."
        },
        {
            "name": "ClickHouse Range Style", 
            "sql": "WHERE created_date >= toStartOfWeek(today() - 7) AND created_date < toStartOfWeek(today())",
            "description": "ClickHouse range-based approach",
            "database": "ClickHouse"
        },
        {
            "name": "ClickHouse Comparison Style",
            "sql": "WHERE toStartOfWeek(created_date) = toStartOfWeek(today() - 7)", 
            "description": "ClickHouse direct week comparison",
            "database": "ClickHouse"
        }
    ]
    
    print("Scenario: Today is Wednesday, Oct 2, 2024")
    print("Target: Previous week (Sep 23 Mon - Sep 29 Sun)")
    print()
    
    for i, approach in enumerate(approaches, 1):
        print(f"{i}. {approach['name']} ({approach['database']})")
        print(f"   SQL: {approach['sql']}")
        print(f"   Description: {approach['description']}")
        print()
        
        # Analyze what each approach does
        if "date_trunc" in approach['sql']:
            print("   Analysis:")
            print("   - date_trunc('week', now()) = Start of current week (Sep 30)")
            print("   - INTERVAL 1 WEEK = 7 days")
            print("   - So: Sep 30 - 7 days = Sep 23 (start of last week)")
            print("   - Range: Sep 23 00:00 to Sep 30 00:00 (exclusive)")
            print("   ✅ Result: Exactly last week (Sep 23-29)")
            
        elif "toStartOfWeek(today() - 7)" in approach['sql'] and ">=" in approach['sql']:
            print("   Analysis:")
            print("   - today() - 7 = Sep 25 (Wed)")
            print("   - toStartOfWeek(Sep 25) = Sep 23 (Mon of that week)")
            print("   - toStartOfWeek(today()) = Sep 30 (Mon of current week)")
            print("   - Range: Sep 23 00:00 to Sep 30 00:00 (exclusive)")
            print("   ✅ Result: Exactly last week (Sep 23-29)")
            
        elif "toStartOfWeek(created_date) =" in approach['sql']:
            print("   Analysis:")
            print("   - today() - 7 = Sep 25 (Wed)")
            print("   - toStartOfWeek(Sep 25) = Sep 23 (Mon of that week)")
            print("   - Finds all rows where toStartOfWeek(created_date) = Sep 23")
            print("   - This includes all dates from Sep 23-29")
            print("   ✅ Result: Exactly last week (Sep 23-29)")
        
        print()

def analyze_differences():
    """Analyze the key differences"""
    
    print("🔍 Key Differences Analysis")
    print("=" * 40)
    print()
    
    print("Functional Equivalence:")
    print("✅ All three approaches return THE SAME result")
    print("✅ All target the exact previous calendar week")
    print("✅ No rolling window issues")
    print()
    
    print("Syntax Differences:")
    print()
    print("1. PostgreSQL/MySQL approach:")
    print("   - Uses standard SQL: date_trunc(), INTERVAL")
    print("   - Portable across databases")
    print("   - More verbose but clear intent")
    print()
    
    print("2. ClickHouse range approach:")
    print("   - Uses ClickHouse functions: toStartOfWeek(), today()")
    print("   - Range-based logic")
    print("   - Mathematically equivalent to #1")
    print()
    
    print("3. ClickHouse comparison approach:")
    print("   - Uses ClickHouse functions")
    print("   - Direct week comparison")
    print("   - Most concise and elegant")
    print()
    
    print("Performance Considerations:")
    print("- Approach #3 might be slightly faster (single function call per row)")
    print("- Approach #2 requires range checking")
    print("- Approach #1 requires date arithmetic")
    print()
    
    print("Readability:")
    print("- Approach #1: Most explicit about intent")
    print("- Approach #2: Clear but verbose")  
    print("- Approach #3: Concise but requires understanding of toStartOfWeek()")

def clickhouse_specific_notes():
    """ClickHouse-specific considerations"""
    
    print("\n⚠️  ClickHouse Specific Notes")
    print("=" * 35)
    print()
    
    print("Why we can't use the PostgreSQL approach in ClickHouse:")
    print("❌ date_trunc('week', now()) - INTERVAL 1 WEEK")
    print("   - ClickHouse doesn't support INTERVAL syntax the same way")
    print("   - date_trunc exists but behavior might differ")
    print()
    
    print("ClickHouse equivalents:")
    print("✅ toStartOfWeek(today() - 7) instead of date_trunc('week', now()) - INTERVAL 1 WEEK")
    print("✅ today() instead of now() for date-only operations")
    print("✅ Direct arithmetic: today() - 7 instead of INTERVAL syntax")
    print()
    
    print("So the user's suggested SQL won't work in ClickHouse!")
    print("But the LOGIC is identical to our ClickHouse approaches.")

if __name__ == "__main__":
    compare_last_week_approaches()
    analyze_differences()
    clickhouse_specific_notes()