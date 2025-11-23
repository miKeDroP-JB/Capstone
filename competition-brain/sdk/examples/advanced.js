/**
 * Advanced Usage Example - JavaScript
 *
 * This example demonstrates advanced features:
 * - Custom model selection
 * - Caching strategies
 * - Batch queries
 * - Error handling
 */

const { CompetitionBrain } = require('../dist/index');

async function main() {
  const client = new CompetitionBrain({
    baseUrl: 'http://localhost:3001',
  });

  console.log('🚀 Advanced Competition Brain Usage\n');

  // 1. Custom model selection based on task type
  console.log('1️⃣ Custom Model Selection\n');

  const models = await client.getModels();

  // Select models based on criteria
  const codingModels = models
    .filter(m => ['gpt-4o', 'claude-sonnet-4.5', 'deepseek-v3', 'qwen-2.5-coder'].includes(m.id))
    .map(m => m.id);

  console.log(`Selected coding-specialized models: ${codingModels.join(', ')}\n`);

  const codingQuery = 'Write a function to detect palindromes in O(n) time';

  const codingResult = await client.query(codingQuery, {
    models: codingModels,
    powerLevel: 90,
    timeLimit: 60,
  });

  console.log(`Coding Query Result: ${codingResult.synthesized.slice(0, 100)}...\n`);

  // 2. Caching demonstration
  console.log('2️⃣ Caching Strategy\n');

  const testQuery = 'What is 2+2?';

  console.log('First query (will be cached)...');
  const firstResult = await client.query(testQuery, {
    models: ['gpt-4o-mini'],
    powerLevel: 50,
    useCache: true,
  });
  console.log(`Time: ${firstResult.totalTime.toFixed(2)}s, Cached: ${firstResult.cached || false}`);

  console.log('Second query (should be instant from cache)...');
  const cachedResult = await client.query(testQuery, {
    models: ['gpt-4o-mini'],
    powerLevel: 50,
    useCache: true,
  });
  console.log(
    `Time: ${cachedResult.totalTime.toFixed(2)}s, Cached: ${cachedResult.cached}, Age: ${(
      cachedResult.cacheAge! / 1000
    ).toFixed(1)}s\n`
  );

  // 3. Batch queries with different configurations
  console.log('3️⃣ Batch Queries\n');

  const queries = [
    { q: 'What is machine learning?', preset: 'fast' },
    { q: 'Explain quantum computing', preset: 'balanced' },
    { q: 'Best practices for API design', preset: 'free' },
  ];

  const batchResults = await Promise.all(
    queries.map(async ({ q, preset }) => {
      console.log(`Running ${preset} query: "${q.slice(0, 30)}..."`);

      switch (preset) {
        case 'fast':
          return client.fastQuery(q);
        case 'free':
          return client.freeQuery(q);
        default:
          return client.query(q, {
            models: ['gpt-4o', 'claude-3-5-haiku'],
            powerLevel: 70,
            timeLimit: 60,
          });
      }
    })
  );

  console.log('\nBatch Results:');
  batchResults.forEach((result, i) => {
    const stats = client.getStats(result);
    console.log(
      `  ${i + 1}. ${queries[i].preset.padEnd(10)} - ${stats.totalTime.toFixed(2)}s, ${stats.successfulModels} models, ${(stats.avgConfidence * 100).toFixed(1)}% conf`
    );
  });

  // 4. Error handling and retries
  console.log('\n4️⃣ Error Handling\n');

  try {
    // Intentionally bad request
    await client.query('test', {
      models: ['invalid-model-xyz'],
      powerLevel: 50,
    });
  } catch (error) {
    console.log('❌ Caught expected error for invalid model');
    console.log(`   Error: ${error.message}\n`);
  }

  // Retry with fallback
  console.log('Retrying with fallback to free models...');
  const fallbackResult = await client.freeQuery('test query');
  console.log(`✅ Fallback successful: ${fallbackResult.individual.length} models responded\n`);

  // 5. A/B Testing different configurations
  console.log('5️⃣ A/B Testing Configurations\n');

  const testPrompt = 'Explain neural networks briefly';

  const configA = await client.query(testPrompt, {
    models: ['gpt-4o-mini', 'gemini-1.5-flash'],
    powerLevel: 50,
    timeLimit: 20,
  });

  const configB = await client.query(testPrompt, {
    models: ['claude-sonnet-4.5', 'o1'],
    powerLevel: 95,
    timeLimit: 60,
  });

  const statsA = client.getStats(configA);
  const statsB = client.getStats(configB);

  console.log('Config A (Fast & Cheap):');
  console.log(
    `  Time: ${statsA.totalTime.toFixed(2)}s, Confidence: ${(statsA.avgConfidence * 100).toFixed(1)}%`
  );

  console.log('Config B (Slow & High Quality):');
  console.log(
    `  Time: ${statsB.totalTime.toFixed(2)}s, Confidence: ${(statsB.avgConfidence * 100).toFixed(1)}%`
  );

  const speedup = statsB.totalTime / statsA.totalTime;
  const qualityDiff = (statsB.avgConfidence - statsA.avgConfidence) * 100;

  console.log(`\nConfig A is ${speedup.toFixed(1)}x faster`);
  console.log(`Config B is ${qualityDiff.toFixed(1)}% more confident`);

  console.log('\n✅ Advanced examples complete!');
}

main().catch(console.error);
