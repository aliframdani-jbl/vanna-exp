#!/usr/bin/env python3
"""
LLM Switcher for Vanna Text2SQL
Allows easy switching between different LLM providers
"""

import os
import sys
from typing import Dict, Any

class LLMConfig:
    """Configuration for different LLM providers"""
    
    PROVIDERS = {
        'qwen': {
            'class_name': 'CustomQwenLLM',
            'required_vars': ['QWEN_API_KEY'],
            'optional_vars': ['QWEN_BASE_URL', 'QWEN_MODEL'],
            'defaults': {
                'QWEN_BASE_URL': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'QWEN_MODEL': 'qwen-turbo'
            },
            'description': 'Alibaba Qwen via DashScope API'
        },
        'openai': {
            'class_name': 'CustomOpenAILLM',
            'required_vars': ['OPENAI_API_KEY'],
            'optional_vars': ['OPENAI_MODEL'],
            'defaults': {
                'OPENAI_MODEL': 'gpt-3.5-turbo'
            },
            'description': 'OpenAI GPT models'
        },
        'ollama': {
            'class_name': 'CustomOllamaLLM',
            'required_vars': [],
            'optional_vars': ['OLLAMA_BASE_URL', 'OLLAMA_MODEL'],
            'defaults': {
                'OLLAMA_BASE_URL': 'http://localhost:11434/v1',
                'OLLAMA_MODEL': 'qwen:14b'
            },
            'description': 'Local Ollama models'
        }
    }

def generate_llm_class(provider: str) -> str:
    """Generate LLM class code for specified provider"""
    
    if provider == 'qwen':
        return '''class CustomQwenLLM(VannaBase):
    """Custom LLM implementation using Qwen via OpenAI-compatible API"""
    
    def __init__(self, config=None):
        VannaBase.__init__(self, config=config)
        
        try:
            import openai
            
            qwen_api_key = os.getenv('QWEN_API_KEY') or os.getenv('DASHSCOPE_API_KEY')
            qwen_base_url = os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
            
            if not qwen_api_key:
                raise Exception("QWEN_API_KEY or DASHSCOPE_API_KEY environment variable is required")
            
            self.client = openai.OpenAI(
                api_key=qwen_api_key,
                base_url=qwen_base_url
            )
            
            self.default_model = os.getenv('QWEN_MODEL', 'qwen-turbo')
            
        except ImportError:
            raise Exception("OpenAI package not installed. Please install it with: pip install openai")

    def submit_prompt(self, prompt, **kwargs) -> str:
        """Submit prompt to Qwen and return response"""
        try:
            model = kwargs.get('model', self.default_model)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates SQL queries. Always respond with valid SQL syntax."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_tokens', 500),
                temperature=kwargs.get('temperature', 0.1),
                top_p=kwargs.get('top_p', 0.8)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Qwen API error: {str(e)}")
    
    def system_message(self, message: str) -> dict:
        """Format system message for the chat API"""
        return {"role": "system", "content": message}
    
    def user_message(self, message: str) -> dict:
        """Format user message for the chat API"""
        return {"role": "user", "content": message}
    
    def assistant_message(self, message: str) -> dict:
        """Format assistant message for the chat API"""
        return {"role": "assistant", "content": message}'''
    
    elif provider == 'openai':
        return '''class CustomOpenAILLM(VannaBase):
    """Custom LLM implementation using OpenAI"""
    
    def __init__(self, config=None):
        VannaBase.__init__(self, config=config)
        
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            self.default_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        except ImportError:
            raise Exception("OpenAI package not installed. Please install it with: pip install openai")
        
        if not os.getenv('OPENAI_API_KEY'):
            raise Exception("OPENAI_API_KEY environment variable is required")

    def submit_prompt(self, prompt, **kwargs) -> str:
        """Submit prompt to OpenAI and return response"""
        try:
            model = kwargs.get('model', self.default_model)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates SQL queries. Always respond with valid SQL syntax."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_tokens', 500),
                temperature=kwargs.get('temperature', 0.1)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def system_message(self, message: str) -> dict:
        """Format system message for the chat API"""
        return {"role": "system", "content": message}
    
    def user_message(self, message: str) -> dict:
        """Format user message for the chat API"""
        return {"role": "user", "content": message}
    
    def assistant_message(self, message: str) -> dict:
        """Format assistant message for the chat API"""
        return {"role": "assistant", "content": message}'''
    
    elif provider == 'ollama':
        return '''class CustomOllamaLLM(VannaBase):
    """Custom LLM implementation using Ollama"""
    
    def __init__(self, config=None):
        VannaBase.__init__(self, config=config)
        
        try:
            import openai
            ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
            
            self.client = openai.OpenAI(
                api_key='dummy_key',  # Ollama doesn't require real API key
                base_url=ollama_base_url
            )
            
            self.default_model = os.getenv('OLLAMA_MODEL', 'qwen:14b')
            
        except ImportError:
            raise Exception("OpenAI package not installed. Please install it with: pip install openai")

    def submit_prompt(self, prompt, **kwargs) -> str:
        """Submit prompt to Ollama and return response"""
        try:
            model = kwargs.get('model', self.default_model)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates SQL queries. Always respond with valid SQL syntax."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_tokens', 500),
                temperature=kwargs.get('temperature', 0.1)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def system_message(self, message: str) -> dict:
        """Format system message for the chat API"""
        return {"role": "system", "content": message}
    
    def user_message(self, message: str) -> dict:
        """Format user message for the chat API"""
        return {"role": "user", "content": message}
    
    def assistant_message(self, message: str) -> dict:
        """Format assistant message for the chat API"""
        return {"role": "assistant", "content": message}'''
    
    else:
        raise ValueError(f"Unknown provider: {provider}")

def switch_llm_provider(provider: str):
    """Switch to specified LLM provider"""
    
    if provider not in LLMConfig.PROVIDERS:
        print(f"❌ Unknown provider: {provider}")
        print(f"Available providers: {', '.join(LLMConfig.PROVIDERS.keys())}")
        return False
    
    config = LLMConfig.PROVIDERS[provider]
    
    # Check required environment variables
    missing_vars = []
    for var in config['required_vars']:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables for {provider}: {', '.join(missing_vars)}")
        return False
    
    # Read current vanna_service.py
    service_file = 'vanna_service.py'
    if not os.path.exists(service_file):
        print(f"❌ {service_file} not found")
        return False
    
    with open(service_file, 'r') as f:
        content = f.read()
    
    # Generate new LLM class
    new_class = generate_llm_class(provider)
    class_name = config['class_name']
    
    # Find and replace the LLM class
    import re
    
    # Pattern to match any Custom*LLM class
    pattern = r'class Custom\w+LLM\(VannaBase\):.*?(?=class|\Z)'
    
    # Replace the class
    new_content = re.sub(pattern, new_class, content, flags=re.DOTALL)
    
    # Update the VannaQdrantClickHouse class to use the new LLM
    pattern2 = r'class VannaQdrantClickHouse\(Qdrant_VectorStore, Custom\w+LLM\):'
    new_content = re.sub(pattern2, f'class VannaQdrantClickHouse(Qdrant_VectorStore, {class_name}):', new_content)
    
    pattern3 = r'Custom\w+LLM\.__init__\(self, config=config\)'
    new_content = re.sub(pattern3, f'{class_name}.__init__(self, config=config)', new_content)
    
    # Write back the file
    with open(service_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Successfully switched to {provider} ({config['description']})")
    print(f"   Class: {class_name}")
    
    # Show required configuration
    print(f"\n📋 Required configuration:")
    for var in config['required_vars']:
        print(f"   {var}={os.getenv(var, 'NOT_SET')}")
    
    print(f"\n📋 Optional configuration:")
    for var in config['optional_vars']:
        default = config['defaults'].get(var, 'None')
        current = os.getenv(var, default)
        print(f"   {var}={current} (default: {default})")
    
    return True

def show_current_provider():
    """Show currently configured provider"""
    service_file = 'vanna_service.py'
    if not os.path.exists(service_file):
        print(f"❌ {service_file} not found")
        return
    
    with open(service_file, 'r') as f:
        content = f.read()
    
    # Find current LLM class
    import re
    match = re.search(r'class (Custom\w+LLM)', content)
    if match:
        current_class = match.group(1)
        
        # Find which provider this belongs to
        for provider, config in LLMConfig.PROVIDERS.items():
            if config['class_name'] == current_class:
                print(f"🔍 Current LLM Provider: {provider}")
                print(f"   Description: {config['description']}")
                print(f"   Class: {current_class}")
                
                # Show configuration status
                print(f"\n📋 Configuration Status:")
                for var in config['required_vars']:
                    status = "✅" if os.getenv(var) else "❌"
                    print(f"   {status} {var}")
                
                for var in config['optional_vars']:
                    value = os.getenv(var, config['defaults'].get(var, 'Not set'))
                    print(f"   📝 {var}={value}")
                return
        
        print(f"🔍 Current LLM Class: {current_class} (unknown provider)")
    else:
        print("❌ No LLM class found in vanna_service.py")

def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print("🔄 LLM Provider Switcher for Vanna Text2SQL")
        print("=" * 50)
        print(f"Usage: {sys.argv[0]} <command> [provider]")
        print("\nCommands:")
        print("  current              Show current LLM provider")
        print("  switch <provider>    Switch to specified provider")
        print("  list                 List available providers")
        print("\nProviders:")
        for provider, config in LLMConfig.PROVIDERS.items():
            print(f"  {provider:<10} - {config['description']}")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'current':
        show_current_provider()
    
    elif command == 'list':
        print("📋 Available LLM Providers:")
        print("=" * 30)
        for provider, config in LLMConfig.PROVIDERS.items():
            print(f"\n{provider.upper()}:")
            print(f"  Description: {config['description']}")
            print(f"  Required vars: {', '.join(config['required_vars']) or 'None'}")
            print(f"  Optional vars: {', '.join(config['optional_vars']) or 'None'}")
    
    elif command == 'switch':
        if len(sys.argv) < 3:
            print("❌ Please specify a provider to switch to")
            print(f"Available: {', '.join(LLMConfig.PROVIDERS.keys())}")
            return
        
        provider = sys.argv[2].lower()
        if switch_llm_provider(provider):
            print(f"\n💡 Next steps:")
            print(f"   1. Restart your API server: python main.py")
            print(f"   2. Test the new provider: python test_vanna_qdrant.py")
    
    else:
        print(f"❌ Unknown command: {command}")
        print(f"Available commands: current, switch, list")

if __name__ == "__main__":
    main()