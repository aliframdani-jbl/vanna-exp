# Getting Qwen API Access

This guide explains how to get access to Qwen (Tongyi Qianwen) API for use with the Vanna Text2SQL system.

## Method 1: Alibaba Cloud DashScope (Recommended)

### Step 1: Create Alibaba Cloud Account
1. Go to [Alibaba Cloud](https://www.alibabacloud.com/)
2. Sign up for a new account or log in to existing account
3. Complete account verification (may require phone/email verification)

### Step 2: Access DashScope
1. Navigate to [DashScope Console](https://dashscope.console.aliyun.com/)
2. Enable the DashScope service if not already enabled
3. You may need to add payment method (some free quota available)

### Step 3: Create API Key
1. In DashScope console, go to "API Key Management"
2. Click "Create API Key"
3. Copy the generated API key
4. Set it in your `.env` file as `QWEN_API_KEY=your_api_key_here`

### Step 4: Available Models
Popular Qwen models available:
- `qwen-turbo` - Fast and efficient (recommended for text2sql)
- `qwen-plus` - More capable, higher cost
- `qwen-max` - Most capable model
- `qwen-max-longcontext` - For long context tasks

## Method 2: Self-Hosted Qwen

### Option A: Ollama (Local)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Qwen model
ollama pull qwen:14b

# Start Ollama server
ollama serve
```

Then update your `.env`:
```bash
QWEN_BASE_URL=http://localhost:11434/v1
QWEN_API_KEY=dummy_key  # Ollama doesn't require real API key
QWEN_MODEL=qwen:14b
```

### Option B: vLLM (Self-hosted)
```bash
# Install vLLM
pip install vllm

# Start vLLM server with Qwen
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen-14B-Chat \
    --host 0.0.0.0 \
    --port 8000
```

Then update your `.env`:
```bash
QWEN_BASE_URL=http://localhost:8000/v1
QWEN_API_KEY=dummy_key
QWEN_MODEL=Qwen/Qwen-14B-Chat
```

## Method 3: Third-Party Providers

Some cloud providers offer Qwen models through OpenAI-compatible APIs:

### Together AI
```bash
QWEN_BASE_URL=https://api.together.xyz/v1
QWEN_API_KEY=your_together_api_key
QWEN_MODEL=Qwen/Qwen1.5-72B-Chat
```

### Replicate
```bash
QWEN_BASE_URL=https://api.replicate.com/v1
QWEN_API_KEY=your_replicate_token
QWEN_MODEL=qwen-chat
```

## Environment Configuration

After getting your API access, update your `.env` file:

```bash
# For DashScope (Alibaba Cloud)
QWEN_API_KEY=your_dashscope_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo

# Alternative environment variable name
DASHSCOPE_API_KEY=your_dashscope_api_key
```

## Testing Your Setup

1. Set your API key in `.env`
2. Start the services: `./setup_qdrant_clickhouse.sh`
3. Run the test: `python test_vanna_qdrant.py`

## Pricing Information

### DashScope Pricing (as of 2024)
- **qwen-turbo**: ~$0.002 per 1K tokens
- **qwen-plus**: ~$0.02 per 1K tokens
- **qwen-max**: ~$0.06 per 1K tokens

Free tier typically includes:
- 1M tokens per month for qwen-turbo
- Limited tokens for other models

### Cost Optimization Tips

1. **Use qwen-turbo** for most text2sql tasks (sufficient quality, lower cost)
2. **Set reasonable max_tokens** in the LLM configuration
3. **Cache training data** to avoid re-processing
4. **Monitor usage** through DashScope console

## Alternative: Fallback to OpenAI

If you prefer to use OpenAI instead, you can modify the code:

1. Change the class name from `CustomQwenLLM` to `CustomOpenAILLM`
2. Update the configuration to use OpenAI endpoints
3. Set `OPENAI_API_KEY` in your `.env` file

## Troubleshooting

### Common Issues

1. **Authentication Error**: Double-check your API key
2. **Model Not Found**: Verify the model name is correct
3. **Rate Limiting**: Check your quota and billing status
4. **Network Issues**: Ensure the base URL is accessible

### Debug Commands

```bash
# Test API connection
curl -X POST "${QWEN_BASE_URL}/chat/completions" \
  -H "Authorization: Bearer ${QWEN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-turbo",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

### Support

- **DashScope**: [Documentation](https://dashscope.aliyun.com/), [Support](https://workorder.console.aliyun.com/)
- **Qwen GitHub**: [Repository](https://github.com/QwenLM/Qwen)
- **Community**: [ModelScope](https://modelscope.cn/), [HuggingFace](https://huggingface.co/Qwen)

The Qwen integration provides excellent performance for Chinese and English text-to-SQL tasks with competitive pricing and good availability.