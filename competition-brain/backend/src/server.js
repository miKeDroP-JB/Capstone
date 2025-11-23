const express = require('express');
const cors = require('cors');
const { orchestrateQuery } = require('./orchestrator');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', version: '1.0.0' });
});

// Main query endpoint
app.post('/api/query', async (req, res) => {
  try {
    const { query, config } = req.body;

    if (!query || !config) {
      return res.status(400).json({ error: 'Missing query or config' });
    }

    console.log(`[Query] "${query}" with ${config.models.length} models`);

    const result = await orchestrateQuery(query, config);

    res.json(result);
  } catch (error) {
    console.error('Query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get available models
app.get('/api/models', (req, res) => {
  res.json({
    models: [
      // Free Models
      { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'OpenAI', free: true, power: 75 },
      { id: 'claude-3-5-haiku', name: 'Claude 3.5 Haiku', provider: 'Anthropic', free: true, power: 72 },
      { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', provider: 'Meta', free: true, power: 80 },
      { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'Google', free: true, power: 70 },
      { id: 'mistral-small', name: 'Mistral Small', provider: 'Mistral', free: true, power: 68 },
      { id: 'deepseek-v3', name: 'DeepSeek V3', provider: 'DeepSeek', free: true, power: 82 },
      // Paid Models
      { id: 'o1', name: 'o1 (Reasoning)', provider: 'OpenAI', free: false, power: 99 },
      { id: 'claude-sonnet-4.5', name: 'Claude Sonnet 4.5', provider: 'Anthropic', free: false, power: 98 },
      { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', free: false, power: 95 },
      { id: 'gemini-2.0-flash-thinking', name: 'Gemini 2.0 Flash Thinking', provider: 'Google', free: false, power: 96 },
      { id: 'gemini-exp-1206', name: 'Gemini Exp 1206', provider: 'Google', free: false, power: 97 },
      { id: 'grok-2', name: 'Grok 2', provider: 'xAI', free: false, power: 90 },
      { id: 'claude-3.7-sonnet', name: 'Claude 3.7 Sonnet', provider: 'Anthropic', free: false, power: 93 },
      { id: 'command-r7b', name: 'Command R7B', provider: 'Cohere', free: false, power: 88 },
      { id: 'qwen-2.5-coder', name: 'Qwen 2.5 Coder', provider: 'Alibaba', free: false, power: 85 },
    ],
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Competition Brain Backend running on http://localhost:${PORT}`);
  console.log(`📊 Ready for multi-agent synthesis`);
});
