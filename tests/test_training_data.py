#!/usr/bin/env python3
"""
Test script to debug get_training_data method
"""

import os
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv

load_dotenv()

def test_get_training_data():
    """Test get_training_data method"""
    try:
        from vanna_service import VannaService
        
        print("🔧 Testing get_training_data method...")
        
        # Initialize service
        service = VannaService()
        
        print("✅ VannaService initialized")
        
        # Test get_training_data
        training_data = service.get_training_data()
        
        print(f"✅ Training data retrieved successfully")
        print(f"   Type: {type(training_data)}")
        print(f"   Length: {len(training_data) if isinstance(training_data, (list, dict)) else 'N/A'}")
        
        if isinstance(training_data, list) and len(training_data) > 0:
            print(f"   First item type: {type(training_data[0])}")
            print(f"   First item: {training_data[0]}")
        
        # Test JSON serialization
        import json
        json_str = json.dumps(training_data)
        print(f"✅ JSON serialization successful")
        print(f"   JSON length: {len(json_str)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing get_training_data method")
    print("=" * 40)
    
    success = test_get_training_data()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 get_training_data test passed!")
    else:
        print("❌ get_training_data test failed!")