/**
 * Basic Usage Example - JavaScript
 *
 * This example shows how to use the Competition Brain client
 * for a simple query with default settings.
 */

const { CompetitionBrain } = require('../dist/index');

async function main() {
  // Initialize client
  const client = new CompetitionBrain({
    baseUrl: 'http://localhost:3001',
    timeout: 60000, // 60 seconds
  });

  try {
    // Check health
    console.log('🔍 Checking API health...');
    const health = await client.health();
    console.log(`✅ API Status: ${health.status} (v${health.version})\n`);

    // Get available models
    console.log('📋 Fetching available models...');
    const models = await client.getModels();
    console.log(`Found ${models.length} models:\n`);

    models.slice(0, 5).forEach(model => {
      console.log(
        `  ${model.name} (${model.provider}) - Power: ${model.power}% ${
          model.free ? '[FREE]' : ''
        }`
      );
    });

    // Make a query
    console.log('\n💭 Querying: "What is the capital of France?"\n');

    const result = await client.query('What is the capital of France?', {
      models: ['gpt-4o-mini', 'claude-3-5-haiku', 'gemini-1.5-flash'],
      powerLevel: 70,
      timeLimit: 30,
    });

    // Display results
    console.log('📊 Results:\n');
    console.log(`Synthesized Answer: ${result.synthesized}\n`);

    const stats = client.getStats(result);
    console.log(`Total Time: ${stats.totalTime.toFixed(2)}s`);
    console.log(`Successful Models: ${stats.successfulModels}/${stats.totalModels}`);
    console.log(`Average Confidence: ${(stats.avgConfidence * 100).toFixed(1)}%`);
    console.log(`Cached: ${stats.cached ? 'Yes' : 'No'}\n`);

    // Show individual responses
    console.log('Individual Agent Responses:');
    result.individual.forEach((resp, i) => {
      console.log(
        `\n  ${i + 1}. ${resp.model} (${(resp.confidence * 100).toFixed(1)}% confidence, ${resp.time.toFixed(2)}s)`
      );
      console.log(`     ${resp.response.slice(0, 100)}...`);
    });
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.response) {
      console.error('Server responded with:', error.response.data);
    }
  }
}

main();
