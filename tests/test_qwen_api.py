#!/usr/bin/env python3
"""
Test script to verify Qwen API integration
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_qwen_api():
    """Test Qwen API directly"""
    try:
        import openai
        
        # Configure for Qwen API
        qwen_api_key = os.getenv('QWEN_API_KEY') or os.getenv('DASHSCOPE_API_KEY')
        qwen_base_url = os.getenv('QWEN_BASE_URL', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1')
        qwen_model = os.getenv('QWEN_MODEL', 'qwen-turbo')
        
        if not qwen_api_key:
            print("❌ QWEN_API_KEY or DASHSCOPE_API_KEY not set")
            return False
        
        print(f"🔧 Testing Qwen API:")
        print(f"   Base URL: {qwen_base_url}")
        print(f"   Model: {qwen_model}")
        print(f"   API Key: {qwen_api_key[:10]}...{qwen_api_key[-4:]}")
        
        client = openai.OpenAI(
            api_key=qwen_api_key,
            base_url=qwen_base_url
        )
        
        # Test simple prompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello"}
        ]
        
        print(f"📤 Sending test message: {messages}")
        
        response = client.chat.completions.create(
            model=qwen_model,
            messages=messages,
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f"✅ Qwen API response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Qwen API test failed: {e}")
        return False

def test_sql_generation():
    """Test SQL generation with Qwen"""
    try:
        import openai
        
        qwen_api_key = os.getenv('QWEN_API_KEY') or os.getenv('DASHSCOPE_API_KEY')
        qwen_base_url = os.getenv('QWEN_BASE_URL', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1')
        qwen_model = os.getenv('QWEN_MODEL', 'qwen-turbo')
        
        client = openai.OpenAI(
            api_key=qwen_api_key,
            base_url=qwen_base_url
        )
        
        # Test SQL generation
        sql_prompt = """
        Given a table called 'customers' with columns: id, name, email, country
        Generate a SQL query to find all customers from USA.
        Only return the SQL query, nothing else.
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates SQL queries. Always respond with valid SQL syntax."},
            {"role": "user", "content": sql_prompt}
        ]
        
        print(f"📤 Testing SQL generation...")
        
        response = client.chat.completions.create(
            model=qwen_model,
            messages=messages,
            max_tokens=100,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f"✅ SQL generation result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ SQL generation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Qwen API Integration")
    print("=" * 40)
    
    success = True
    
    print("\n1. Basic API Test:")
    success &= test_qwen_api()
    
    print("\n2. SQL Generation Test:")
    success &= test_sql_generation()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! Qwen API is working correctly.")
    else:
        print("❌ Some tests failed. Check your configuration.")
        print("\nTroubleshooting:")
        print("1. Verify QWEN_API_KEY is set correctly")
        print("2. Check QWEN_BASE_URL is correct")
        print("3. Ensure your API key has access to the specified model")
        print("4. Try different models (qwen-turbo, qwen-plus, qwen-max)")