const { queryAgent } = require('../agents');
const { synthesizeResponses } = require('../formatters/synthesizer');
const { getCache } = require('../cache');

/**
 * Orchestrate multi-agent query
 * @param {string} query - User query
 * @param {object} config - Configuration (models, timeLimit, powerLevel, freeOnly, useCache)
 * @returns {Promise<object>} Synthesized result with individual responses
 */
async function orchestrateQuery(query, config) {
  const startTime = Date.now();

  // Check cache first
  const cache = getCache({
    enabled: config.useCache !== false,
    ttl: 3600000, // 1 hour
    persist: true,
  });

  const cached = cache.get(query, config);
  if (cached) {
    console.log(`[Orchestrator] Returning cached result (saved ${cached.totalTime.toFixed(1)}s)`);
    return {
      ...cached,
      cached: true,
      cacheAge: Date.now() - new Date(cached.timestamp).getTime(),
    };
  }

  console.log(`[Orchestrator] Starting with ${config.models.length} agents`);

  // Execute all agents in parallel
  const agentPromises = config.models.map(async (modelId) => {
    const agentStart = Date.now();

    try {
      const response = await queryAgent(modelId, query, {
        timeout: config.timeLimit * 1000,
        powerLevel: config.powerLevel,
      });

      const agentTime = (Date.now() - agentStart) / 1000;

      return {
        model: modelId,
        response: response.text,
        confidence: response.confidence || 0.8,
        time: agentTime,
        success: true,
      };
    } catch (error) {
      console.error(`[Agent ${modelId}] Failed:`, error.message);

      return {
        model: modelId,
        response: error.message,
        confidence: 0,
        time: (Date.now() - agentStart) / 1000,
        success: false,
      };
    }
  });

  // Wait for all agents (with timeout)
  const agentResults = await Promise.allSettled(agentPromises);

  // Extract successful responses
  const individual = agentResults
    .filter((result) => result.status === 'fulfilled')
    .map((result) => result.value)
    .filter((result) => result.success);

  console.log(`[Orchestrator] ${individual.length}/${config.models.length} agents succeeded`);

  // Synthesize responses
  const synthesized = await synthesizeResponses(query, individual, config);

  const totalTime = (Date.now() - startTime) / 1000;

  const result = {
    id: Date.now().toString(),
    query,
    synthesized,
    individual,
    totalTime,
    timestamp: new Date(),
    cached: false,
  };

  // Cache the result
  cache.set(query, config, result);

  return result;
}

module.exports = { orchestrateQuery };
