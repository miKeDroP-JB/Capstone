# Competition Brain Client SDK

Official client library for [Competition Brain](../README.md) - Multi-Agent AI Orchestration Platform

[![npm version](https://img.shields.io/npm/v/@orb/competition-brain-client)](https://www.npmjs.com/package/@orb/competition-brain-client)
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](../LICENSE)

---

## Features

- 🎯 **Type-Safe** - Full TypeScript support with comprehensive type definitions
- 🚀 **Easy to Use** - Simple API with sensible defaults
- 🎨 **Presets** - Built-in configurations for common use cases
- 📊 **Analytics** - Rich statistics and export capabilities
- 🔄 **Caching** - Automatic response caching for cost optimization
- 🌐 **Cross-Platform** - Works in Node.js and browsers (with bundler)
- 📦 **Lightweight** - Minimal dependencies (just axios)

---

## Installation

### NPM
```bash
npm install @orb/competition-brain-client
```

### Yarn
```bash
yarn add @orb/competition-brain-client
```

### PNPM
```bash
pnpm add @orb/competition-brain-client
```

---

## Quick Start

### JavaScript
```javascript
const { CompetitionBrain } = require('@orb/competition-brain-client');

const client = new CompetitionBrain({
  baseUrl: 'http://localhost:3001'
});

const result = await client.query('What is 2+2?', {
  models: ['gpt-4o-mini', 'claude-3-5-haiku'],
  powerLevel: 70
});

console.log(result.synthesized);
```

### TypeScript
```typescript
import CompetitionBrain, { QueryResult } from '@orb/competition-brain-client';

const client = new CompetitionBrain({
  baseUrl: 'http://localhost:3001'
});

const result: QueryResult = await client.query('What is 2+2?', {
  models: ['gpt-4o-mini', 'claude-3-5-haiku'],
  powerLevel: 70
});

console.log(result.synthesized);
```

---

## Usage

### 1. Initialize Client

```typescript
const client = new CompetitionBrain({
  baseUrl: 'http://localhost:3001',  // API endpoint
  timeout: 300000,                   // 5 minutes (in ms)
});
```

### 2. Basic Query

```typescript
const result = await client.query('Explain quantum computing', {
  models: ['gpt-4o', 'claude-sonnet-4.5'],
  powerLevel: 80,        // 0-100 (higher = better quality)
  timeLimit: 60,         // seconds
  useCache: true,        // enable caching
});

console.log(result.synthesized);
```

### 3. Get Available Models

```typescript
const models = await client.getModels();

models.forEach(model => {
  console.log(`${model.name} - Power: ${model.power}% ${model.free ? '[FREE]' : ''}`);
});

// Filter free models
const freeModels = models.filter(m => m.free);
```

### 4. Health Check

```typescript
const health = await client.health();
console.log(health.status); // 'ok' or 'error'
```

---

## Presets

### Competition Mode (Max Quality)
```typescript
// Uses top 5 models, 95% power, 180s timeout
const result = await client.competitionQuery('Your hard question here');
```

**Best for**: High-stakes competitions, critical decisions, complex problems

**Cost**: ~$0.50-2.00 per query

---

### Fast Mode (Quick Answers)
```typescript
// Uses 3 models, 50% power, 30s timeout
const result = await client.fastQuery('Quick question?');
```

**Best for**: Development, testing, simple queries

**Cost**: ~$0.01-0.05 per query

---

### Free Mode (No Cost)
```typescript
// Uses only free models, 70% power
const result = await client.freeQuery('Budget-friendly query');
```

**Best for**: High-volume use cases, prototyping, learning

**Cost**: FREE (with rate limits)

---

## Advanced Features

### Statistics

```typescript
const result = await client.query(...);

const stats = client.getStats(result);

console.log(stats);
// {
//   totalModels: 5,
//   successfulModels: 5,
//   failedModels: 0,
//   avgConfidence: 0.94,
//   avgTime: 2.3,
//   totalTime: 5.1,
//   cached: false
// }
```

### Export to Markdown

```typescript
const result = await client.query(...);

const markdown = client.exportMarkdown(result);
fs.writeFileSync('result.md', markdown);
```

**Output**:
```markdown
# Competition Brain Result

**Query**: Explain quantum computing

**Timestamp**: 2025-11-23T05:30:00.000Z

**Total Time**: 12.34s

## Synthesized Response

[Combined response from all models...]

## Statistics

- Models Queried: 5
- Successful: 5
- Average Confidence: 94.2%
...
```

### Export to JSON

```typescript
const result = await client.query(...);

const json = client.exportJSON(result);
fs.writeFileSync('result.json', json);
```

### Custom Model Selection

```typescript
const models = await client.getModels();

// Select coding-focused models
const codingModels = models
  .filter(m => ['gpt-4o', 'deepseek-v3', 'qwen-2.5-coder'].includes(m.id))
  .map(m => m.id);

const result = await client.query('Write a sorting algorithm', {
  models: codingModels,
  powerLevel: 90
});
```

### Batch Queries

```typescript
const queries = [
  'What is AI?',
  'Explain machine learning',
  'What is neural network?'
];

const results = await Promise.all(
  queries.map(q => client.fastQuery(q))
);

results.forEach((result, i) => {
  console.log(`${i+1}. ${result.synthesized.slice(0, 100)}...`);
});
```

### Caching Control

```typescript
// First query - will hit API
const result1 = await client.query('What is 2+2?', {
  models: ['gpt-4o-mini'],
  useCache: true  // default
});
console.log(`Time: ${result1.totalTime}s, Cached: ${result1.cached}`);
// Output: Time: 2.5s, Cached: false

// Second identical query - instant from cache
const result2 = await client.query('What is 2+2?', {
  models: ['gpt-4o-mini'],
  useCache: true
});
console.log(`Time: ${result2.totalTime}s, Cached: ${result2.cached}`);
// Output: Time: 0.05s, Cached: true

// Force bypass cache
const result3 = await client.query('What is 2+2?', {
  models: ['gpt-4o-mini'],
  useCache: false  // bypass cache
});
```

---

## API Reference

### CompetitionBrain

#### Constructor

```typescript
new CompetitionBrain(options?: CompetitionBrainOptions)
```

**Options**:
- `baseUrl?: string` - API endpoint (default: `http://localhost:3001`)
- `timeout?: number` - Request timeout in ms (default: `300000`)
- `axiosConfig?: AxiosRequestConfig` - Custom axios configuration

#### Methods

##### query()
```typescript
async query(query: string, config: QueryConfig): Promise<QueryResult>
```

**Parameters**:
- `query: string` - The question or prompt
- `config: QueryConfig`:
  - `models: string[]` - Array of model IDs
  - `freeOnly?: boolean` - Only use free models
  - `timeLimit?: number` - Time limit in seconds (5-300)
  - `powerLevel?: number` - Power level (0-100)
  - `useCache?: boolean` - Enable caching (default: true)

**Returns**: `Promise<QueryResult>`

---

##### getModels()
```typescript
async getModels(): Promise<Model[]>
```

Returns list of available AI models.

---

##### health()
```typescript
async health(): Promise<HealthResponse>
```

Check API health status.

---

##### competitionQuery()
```typescript
async competitionQuery(query: string): Promise<QueryResult>
```

Query with competition preset (top 5 models, max power).

---

##### fastQuery()
```typescript
async fastQuery(query: string): Promise<QueryResult>
```

Query with fast preset (3 models, 30s).

---

##### freeQuery()
```typescript
async freeQuery(query: string): Promise<QueryResult>
```

Query with free models only.

---

##### getStats()
```typescript
getStats(result: QueryResult): Stats
```

Calculate statistics from a query result.

**Returns**:
```typescript
{
  totalModels: number;
  successfulModels: number;
  failedModels: number;
  avgConfidence: number;
  avgTime: number;
  totalTime: number;
  cached: boolean;
  cacheAge?: number;
}
```

---

##### exportJSON()
```typescript
exportJSON(result: QueryResult): string
```

Export result to JSON string.

---

##### exportMarkdown()
```typescript
exportMarkdown(result: QueryResult): string
```

Export result to Markdown format.

---

### Types

#### QueryResult
```typescript
interface QueryResult {
  id: string;
  query: string;
  synthesized: string;
  individual: AgentResponse[];
  totalTime: number;
  timestamp: Date;
  cached?: boolean;
  cacheAge?: number;
}
```

#### AgentResponse
```typescript
interface AgentResponse {
  model: string;
  response: string;
  confidence: number;
  time: number;
  success: boolean;
}
```

#### Model
```typescript
interface Model {
  id: string;
  name: string;
  provider: string;
  free: boolean;
  power: number;
}
```

---

## Examples

See the [examples](./examples) directory:

- [`basic.js`](./examples/basic.js) - Basic usage in JavaScript
- [`competition.ts`](./examples/competition.ts) - Competition mode in TypeScript
- [`advanced.js`](./examples/advanced.js) - Advanced features (caching, batch, A/B testing)
- [`python_client.py`](./examples/python_client.py) - Python wrapper implementation

### Running Examples

```bash
# Install dependencies
npm install

# Build SDK
npm run build

# Run JavaScript example
node examples/basic.js

# Run TypeScript example (compile first)
npx ts-node examples/competition.ts
```

---

## Python Client

A lightweight Python wrapper is available in [`examples/python_client.py`](./examples/python_client.py):

```python
from python_client import CompetitionBrain

client = CompetitionBrain(base_url="http://localhost:3001")

result = client.query(
    "What is AI?",
    models=["gpt-4o-mini", "claude-3-5-haiku"],
    power_level=70
)

print(result["synthesized"])
```

**Requirements**: `pip install requests`

---

## Error Handling

```typescript
try {
  const result = await client.query('test', {
    models: ['invalid-model'],
    powerLevel: 50
  });
} catch (error) {
  if (error.response) {
    // API responded with error
    console.error('API Error:', error.response.data);
  } else if (error.request) {
    // No response received
    console.error('Network Error:', error.message);
  } else {
    // Other error
    console.error('Error:', error.message);
  }
}
```

### Common Errors

**400 Bad Request** - Invalid query or config
```typescript
// Missing required fields
const result = await client.query('', { models: [] }); // Error!
```

**500 Internal Server Error** - All models failed
```typescript
// Check individual responses
if (result.individual.every(r => !r.success)) {
  console.log('All models failed!');
}
```

**Timeout** - Request took too long
```typescript
// Increase timeout or reduce timeLimit
const client = new CompetitionBrain({ timeout: 600000 }); // 10 minutes
```

---

## Best Practices

### 1. Use Caching for Development

```typescript
// Enable caching to save costs during development
const result = await client.query(query, {
  models: ['gpt-4o-mini'],
  useCache: true  // default
});
```

### 2. Start with Free Models

```typescript
// Test with free models first
const freeResult = await client.freeQuery('test');

// Then scale up to paid models
const paidResult = await client.competitionQuery('final submission');
```

### 3. Handle Errors Gracefully

```typescript
let result;

try {
  result = await client.query(...);
} catch (error) {
  // Fallback to fast query
  result = await client.fastQuery(...);
}
```

### 4. Monitor Statistics

```typescript
const result = await client.query(...);
const stats = client.getStats(result);

// Quality check
if (stats.avgConfidence < 0.8) {
  console.warn('Low confidence - consider re-running');
}

// Performance check
if (stats.totalTime > 60) {
  console.warn('Slow query - consider reducing timeLimit or models');
}
```

### 5. Export for Analysis

```typescript
// Export every competition query
const result = await client.competitionQuery(...);

fs.writeFileSync(
  `submissions/${Date.now()}.json`,
  client.exportJSON(result)
);
```

---

## Performance Tips

1. **Parallel Queries**: Use `Promise.all()` for multiple independent queries
2. **Caching**: Enable for repeated/similar queries
3. **Model Selection**: Use fewer, higher-quality models instead of many low-quality ones
4. **Power Level**: Balance quality vs speed (70-80% is usually optimal)
5. **Time Limit**: Set realistic limits based on task complexity

---

## Cost Optimization

### Budget Tiers

**Free Tier** ($0/month):
```typescript
await client.freeQuery(query); // Gemini, Groq, GPT-4o Mini
```

**Light Use** ($5-20/month):
```typescript
await client.query(query, {
  models: ['gpt-4o-mini', 'claude-3-5-haiku'],
  powerLevel: 70
});
```

**Professional** ($50-200/month):
```typescript
await client.competitionQuery(query); // Top 5 models
```

---

## Troubleshooting

### "Connection refused"

**Problem**: Backend not running

**Solution**:
```bash
cd backend
npm start
```

### "Invalid API key" warnings

**Problem**: Missing provider API keys

**Solution**: Add keys to `backend/.env` (see [AI_PROVIDERS.md](../backend/AI_PROVIDERS.md))

### "All models failed"

**Problem**: Network issues or invalid config

**Solution**:
```typescript
const health = await client.health();
const models = await client.getModels();
```

---

## Development

### Build from Source

```bash
git clone https://github.com/miKeDroP-JB/Capstone
cd competition-brain/sdk
npm install
npm run build
```

### Run Tests

```bash
npm test
```

### Generate Docs

```bash
npm run docs
```

---

## License

MIT - See [LICENSE](../LICENSE) file

---

## Support

- **Issues**: https://github.com/miKeDroP-JB/Capstone/issues
- **Backend Docs**: [AI_PROVIDERS.md](../backend/AI_PROVIDERS.md)
- **Main README**: [../README.md](../README.md)

---

**Built with ❤️ for the AI competition community**
