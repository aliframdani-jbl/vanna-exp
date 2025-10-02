#!/usr/bin/env python3
"""
Debug script to test the VannaService generate_sql method directly
"""

import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

def test_generate_sql():
    """Test the generate_sql method directly"""
    try:
        from vanna_service import VannaService
        
        print("🧪 Testing VannaService.generate_sql() directly")
        print("=" * 50)
        
        # Initialize service
        print("1. Initializing VannaService...")
        service = VannaService()
        print("✅ VannaService initialized")
        
        # Test simple question
        question = "How many customers are there?"
        print(f"2. Testing question: '{question}'")
        
        try:
            result = service.generate_sql(question)
            print(f"✅ Result type: {type(result)}")
            print(f"✅ Result value: {result}")
            print(f"✅ Is string? {isinstance(result, str)}")
            
            # Try to convert to JSON to see if it's serializable
            import json
            json_result = json.dumps({"sql": result})
            print(f"✅ JSON serialization successful: {json_result[:100]}...")
            
        except Exception as e:
            print(f"❌ generate_sql failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generate_sql()