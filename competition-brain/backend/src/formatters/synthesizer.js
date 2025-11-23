/**
 * Synthesize multiple agent responses into one coherent answer
 * @param {string} query - Original query
 * @param {Array} responses - Individual agent responses
 * @param {object} config - Configuration
 * @returns {Promise<string>} Synthesized response
 */
async function synthesizeResponses(query, responses, config) {
  if (responses.length === 0) {
    return 'No responses available. Please try again with different models.';
  }

  if (responses.length === 1) {
    return responses[0].response;
  }

  console.log(`[Synthesizer] Combining ${responses.length} responses`);

  // Weight responses by confidence
  const weightedResponses = responses.map((r) => ({
    ...r,
    weight: r.confidence * (r.success ? 1 : 0.5),
  }));

  // Sort by weight
  const sorted = weightedResponses.sort((a, b) => b.weight - a.weight);

  // Approach 1: Use highest-confidence response as base
  const baseResponse = sorted[0];

  // Approach 2: Extract key points from all responses
  const keyPoints = extractKeyPoints(sorted);

  // Approach 3: Combine insights
  const synthesized = combineInsights(query, sorted, keyPoints, config);

  return synthesized;
}

/**
 * Extract key points from all responses
 */
function extractKeyPoints(responses) {
  const points = new Set();

  responses.forEach((response) => {
    // Simple sentence extraction (in production, use NLP)
    const sentences = response.response
      .split(/[.!?]+/)
      .map((s) => s.trim())
      .filter((s) => s.length > 20 && s.length < 200);

    sentences.slice(0, 3).forEach((s) => points.add(s));
  });

  return Array.from(points);
}

/**
 * Combine insights into coherent response
 */
function combineInsights(query, responses, keyPoints, config) {
  const topResponses = responses.slice(0, 3);

  // Build synthesized response
  let synthesized = '';

  // Strategy based on config.powerLevel
  if (config.powerLevel > 80) {
    // High power: Comprehensive synthesis
    synthesized += `# Comprehensive Analysis\n\n`;
    synthesized += `Based on analysis from ${responses.length} AI models:\n\n`;

    // Include top 3 perspectives
    topResponses.forEach((r, idx) => {
      synthesized += `**Perspective ${idx + 1}** (Confidence: ${(r.confidence * 100).toFixed(0)}%)\n`;
      synthesized += `${r.response.slice(0, 300)}...\n\n`;
    });

    synthesized += `**Synthesized Conclusion:**\n`;
    synthesized += extractConsensus(topResponses);

  } else if (config.powerLevel > 50) {
    // Medium power: Balanced synthesis
    synthesized += `Based on multiple AI analyses:\n\n`;

    const consensus = extractConsensus(topResponses);
    synthesized += consensus;

    synthesized += `\n\n**Key Insights:**\n`;
    keyPoints.slice(0, 5).forEach((point, idx) => {
      synthesized += `${idx + 1}. ${point}\n`;
    });

  } else {
    // Low power: Quick synthesis
    synthesized = topResponses[0].response;

    if (topResponses.length > 1) {
      synthesized += `\n\n*Additional insight: ${topResponses[1].response.slice(0, 150)}...*`;
    }
  }

  return synthesized.trim();
}

/**
 * Extract consensus from top responses
 */
function extractConsensus(responses) {
  // Find common themes (simplified - in production use NLP/embeddings)
  const commonWords = new Map();

  responses.forEach((r) => {
    const words = r.response.toLowerCase().match(/\b[a-z]{4,}\b/g) || [];
    words.forEach((word) => {
      commonWords.set(word, (commonWords.get(word) || 0) + 1);
    });
  });

  // Get most frequent meaningful words
  const frequent = Array.from(commonWords.entries())
    .filter(([word, count]) => count >= 2 && !isStopWord(word))
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([word]) => word);

  // Build consensus statement
  const consensus = `The analysis converges on several key themes: ${frequent.join(', ')}. ` +
    `${responses[0].response.slice(0, 200)}...`;

  return consensus;
}

/**
 * Simple stop word filter
 */
function isStopWord(word) {
  const stopWords = new Set([
    'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'would',
    'there', 'their', 'about', 'which', 'these', 'could', 'should', 'based',
  ]);
  return stopWords.has(word);
}

/**
 * Format for competition submission
 * @param {string} synthesized - Synthesized response
 * @param {Array} metadata - Response metadata
 * @returns {string} Competition-ready formatted response
 */
function formatForCompetition(synthesized, metadata) {
  return `# Response\n\n${synthesized}\n\n---\n\n` +
    `*Generated using multi-agent synthesis (${metadata.agentCount} models, ` +
    `${metadata.totalTime.toFixed(2)}s processing time)*`;
}

module.exports = {
  synthesizeResponses,
  formatForCompetition,
};
