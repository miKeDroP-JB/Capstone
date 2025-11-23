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
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI', free: true, power: 60 },
      { id: 'claude-instant', name: 'Claude Instant', provider: 'Anthropic', free: true, power: 65 },
      { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', provider: 'OpenAI', free: false, power: 95 },
      { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'Anthropic', free: false, power: 98 },
      { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'Anthropic', free: false, power: 90 },
      { id: 'gemini-ultra', name: 'Gemini Ultra', provider: 'Google', free: false, power: 93 },
    ],
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Competition Brain Backend running on http://localhost:${PORT}`);
  console.log(`📊 Ready for multi-agent synthesis`);
});
