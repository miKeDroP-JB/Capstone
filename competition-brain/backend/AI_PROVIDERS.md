# AI Provider Integration Guide

Competition Brain now supports **15+ AI models** across **9 providers**. This guide explains how to get API keys and enable each provider.

---

## Supported Providers

| Provider | Models | Power | Cost | API Keys |
|----------|--------|-------|------|----------|
| **OpenAI** | o1, GPT-4o, GPT-4o Mini | 75-99 | Paid/Free tier | ✅ Required |
| **Anthropic** | Claude Sonnet 4.5, Claude 3.7, Haiku | 72-98 | Paid | ✅ Required |
| **Google** | Gemini Exp 1206, Gemini 2.0 Flash Thinking, 1.5 Flash | 70-97 | Free/Paid | ✅ Required |
| **Mistral** | Mistral Small | 68 | Free tier | Optional |
| **Cohere** | Command R7B | 88 | Free tier | Optional |
| **Groq** | Llama 3.3 70B | 80 | Free tier | Optional |
| **DeepSeek** | DeepSeek V3 | 82 | Paid | Optional |
| **xAI** | Grok 2 | 90 | Paid | Optional |
| **Perplexity** | Sonar (web-grounded) | 94 | Paid | Optional |

**Note**: Models without API keys will use mock responses for testing. The system gracefully falls back to mocks when keys are missing.

---

## Getting API Keys

### 1. OpenAI (Required for o1, GPT-4o, GPT-4o Mini)

**Sign Up**: https://platform.openai.com/signup

**Get Key**:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

**Add to .env**:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

**Models Enabled**:
- `o1` (99% power) - Advanced reasoning model
- `gpt-4o` (95% power) - GPT-4 Omni
- `gpt-4o-mini` (75% power) - Fast, cost-effective

**Cost**:
- o1: $15/1M input, $60/1M output
- GPT-4o: $2.50/1M input, $10/1M output
- GPT-4o Mini: $0.15/1M input, $0.60/1M output

---

### 2. Anthropic (Required for Claude models)

**Sign Up**: https://console.anthropic.com/

**Get Key**:
1. Go to https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Copy the key (starts with `sk-ant-`)

**Add to .env**:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Models Enabled**:
- `claude-sonnet-4.5` (98% power) - Latest flagship
- `claude-3.7-sonnet` (93% power) - Enhanced reasoning
- `claude-3-5-haiku` (72% power) - Fast responses

**Cost**:
- Sonnet 4.5: $3/1M input, $15/1M output
- Haiku: $0.25/1M input, $1.25/1M output

---

### 3. Google Gemini (Required for Gemini models)

**Sign Up**: https://ai.google.dev/

**Get Key**:
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

**Add to .env**:
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

**Models Enabled**:
- `gemini-exp-1206` (97% power) - Experimental flagship
- `gemini-2.0-flash-thinking` (96% power) - Fast reasoning
- `gemini-1.5-flash` (70% power) - Free tier

**Cost**:
- 1.5 Flash: **FREE** up to 15 RPM, then $0.075/1M input
- Exp models: Pricing varies

**Free Tier**: 15 requests/minute, 1500/day

---

### 4. Mistral (Optional)

**Sign Up**: https://console.mistral.ai/

**Get Key**:
1. Go to https://console.mistral.ai/api-keys/
2. Create new key
3. Copy the key

**Add to .env**:
```bash
MISTRAL_API_KEY=your-mistral-api-key-here
```

**Models Enabled**:
- `mistral-small` (68% power) - Cost-effective

**Cost**: $0.20/1M tokens (input/output combined)

**Free Tier**: Limited free credits for testing

---

### 5. Cohere (Optional)

**Sign Up**: https://dashboard.cohere.com/

**Get Key**:
1. Go to https://dashboard.cohere.com/api-keys
2. Create new API key
3. Copy the key

**Add to .env**:
```bash
COHERE_API_KEY=your-cohere-api-key-here
```

**Models Enabled**:
- `command-r7b` (88% power) - Strong generalist

**Cost**: $0.15/1M input, $0.60/1M output

**Free Tier**: Trial API with rate limits

---

### 6. Groq (Optional - Fast Llama Inference)

**Sign Up**: https://console.groq.com/

**Get Key**:
1. Go to https://console.groq.com/keys
2. Create new API key
3. Copy the key

**Add to .env**:
```bash
GROQ_API_KEY=your-groq-api-key-here
```

**Models Enabled**:
- `llama-3.3-70b` (80% power) - Fast open-source

**Cost**: **FREE** during beta (with rate limits)

**Speed**: Up to 750 tokens/second (fastest inference)

**Free Tier**: 14,400 requests/day

---

### 7. DeepSeek (Optional)

**Sign Up**: https://platform.deepseek.com/

**Get Key**:
1. Go to https://platform.deepseek.com/api_keys
2. Create new API key
3. Copy the key

**Add to .env**:
```bash
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

**Models Enabled**:
- `deepseek-v3` (82% power) - Strong Chinese model with English support

**Cost**: $0.27/1M input, $1.10/1M output

**Strengths**: Math, coding, reasoning at low cost

---

### 8. xAI (Optional - Grok)

**Sign Up**: https://console.x.ai/

**Get Key**:
1. Go to https://console.x.ai/
2. Navigate to API Keys
3. Create and copy key

**Add to .env**:
```bash
XAI_API_KEY=your-xai-api-key-here
```

**Models Enabled**:
- `grok-2` (90% power) - Real-time web access

**Cost**: Pricing TBD (beta access)

**Strengths**: Real-time information, humor, X/Twitter integration

---

### 9. Perplexity (Optional - Web-Grounded)

**Sign Up**: https://www.perplexity.ai/settings/api

**Get Key**:
1. Subscribe to Perplexity Pro
2. Go to https://www.perplexity.ai/settings/api
3. Generate API key

**Add to .env**:
```bash
PERPLEXITY_API_KEY=your-perplexity-api-key-here
```

**Models Enabled**:
- `perplexity` (94% power) - Web-grounded responses with citations

**Cost**: Included with Pro subscription ($20/month)

**Strengths**: Live web search, citations, up-to-date info

---

## Configuration Examples

### Minimal Setup (Free/Low Cost)

```bash
# .env
OPENAI_API_KEY=sk-your-key  # GPT-4o Mini ($0.15/1M)
GOOGLE_API_KEY=your-key      # Gemini 1.5 Flash (FREE)
GROQ_API_KEY=your-key        # Llama 3.3 (FREE beta)
```

**Total Cost**: ~$0-5/month for moderate use

---

### Competition Setup (Maximum Power)

```bash
# .env
OPENAI_API_KEY=sk-your-key         # o1 reasoning
ANTHROPIC_API_KEY=sk-ant-your-key  # Claude Sonnet 4.5
GOOGLE_API_KEY=your-key            # Gemini Exp 1206
DEEPSEEK_API_KEY=your-key          # DeepSeek V3
PERPLEXITY_API_KEY=your-key        # Web-grounded
```

**Total Cost**: $50-200/month depending on volume

**Use Case**: High-stakes competitions with large prizes

---

### Balanced Setup

```bash
# .env
OPENAI_API_KEY=sk-your-key         # GPT-4o
ANTHROPIC_API_KEY=sk-ant-your-key  # Claude Haiku (fast)
GOOGLE_API_KEY=your-key            # Gemini Flash (free)
GROQ_API_KEY=your-key              # Llama (free)
MISTRAL_API_KEY=your-key           # Mistral Small
```

**Total Cost**: $10-30/month

**Use Case**: Daily use, testing, development

---

## Testing Your Setup

After adding API keys to `.env`, test each provider:

```bash
cd backend
npm start
```

Then make a test query:

```bash
curl -X POST http://localhost:3001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 2+2?",
    "config": {
      "models": ["gpt-4o-mini", "claude-3-5-haiku", "gemini-1.5-flash"],
      "timeLimit": 30,
      "powerLevel": 80
    }
  }'
```

Check the backend console logs to see which providers succeeded and which fell back to mocks.

---

## Provider Selection Strategy

### For Speed (< 5 seconds)
- Groq (Llama 3.3) - 750 tok/s
- Gemini 1.5 Flash - Fast and free
- Claude Haiku - Fast paid option

### For Quality (Competition Submissions)
1. **o1** (99%) - Best reasoning
2. **Claude Sonnet 4.5** (98%) - Best writing
3. **Gemini Exp 1206** (97%) - Strong generalist
4. **DeepSeek V3** (92%) - Budget powerhouse

### For Cost Efficiency
1. **Gemini 1.5 Flash** (70%) - FREE
2. **Groq Llama** (80%) - FREE beta
3. **GPT-4o Mini** (75%) - $0.15/1M
4. **Mistral Small** (68%) - $0.20/1M

### For Specific Use Cases
- **Research/Facts**: Perplexity (web-grounded)
- **Coding**: DeepSeek V3, GPT-4o
- **Writing**: Claude Sonnet 4.5
- **Reasoning**: o1
- **Real-time Info**: Grok 2, Perplexity

---

## Troubleshooting

### "No API key" warnings

If you see warnings like `[Gemini gemini-1.5-flash] No API key, using mock`:
1. Check `.env` file exists in `/backend` directory
2. Verify key format (no quotes, no extra spaces)
3. Restart the backend server after adding keys

### Rate Limits

Free tiers have rate limits:
- **Gemini**: 15 requests/minute
- **Groq**: 30 requests/minute
- **OpenAI Free**: 3 requests/minute

**Solution**: Spread queries over time or upgrade to paid tier

### Invalid API Key Errors

1. Verify key is copied correctly (no truncation)
2. Check key is active in provider dashboard
3. Ensure billing is enabled (for paid providers)
4. Try regenerating the key

### Model Not Found Errors

Some model names changed:
- Use `o1` instead of `o1-preview` (auto-mapped)
- Use `claude-sonnet-4.5` instead of API name (auto-mapped)
- Check `agents/index.js` for model mappings

---

## Cost Optimization Tips

1. **Use Caching**: Identical queries return cached results (no API cost)
2. **Start with Free Models**: Test with Gemini/Groq before paid models
3. **Power Level**: Lower power = fewer tokens = lower cost
4. **Time Limits**: Shorter timeouts prevent runaway costs
5. **Model Selection**: Don't query all models unless needed

**Example**: Testing a feature
- Use 3 free models (Gemini, Groq, GPT-4o Mini)
- Power: 50%
- Time: 30s
- Cost: ~$0.01 per query

**Example**: Competition submission
- Use top 5 models (o1, Claude 4.5, Gemini Exp, DeepSeek, GPT-4o)
- Power: 95%
- Time: 180s
- Cost: ~$0.50-2.00 per query

---

## Adding New Providers

To add a new provider:

1. **Install SDK**:
```bash
npm install new-provider-sdk
```

2. **Add to `agents/index.js`**:
```javascript
const newProvider = require('new-provider-sdk');

async function queryNewProvider(modelId, query, powerLevel) {
  const response = await newProvider.query({
    model: modelId,
    prompt: query,
    temperature: 1 - (powerLevel / 200),
  });

  return {
    text: response.output,
    confidence: 0.85,
  };
}
```

3. **Add routing**:
```javascript
else if (modelId.startsWith('new-')) {
  responsePromise = queryNewProvider(modelId, query, powerLevel);
}
```

4. **Add to UI** (`frontend/src/components/ControlPanel.tsx`):
```javascript
{ id: 'new-model', name: 'New Model', provider: 'NewProvider', free: false, power: 85 }
```

---

## Support

**Issues**: https://github.com/miKeDroP-JB/Capstone/issues

**Questions**: Check provider docs first, then open an issue

**API Costs**: Always test with free tiers before scaling up

---

**Last Updated**: November 2025
