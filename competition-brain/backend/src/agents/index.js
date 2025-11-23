require('dotenv').config();
const OpenAI = require('openai');
const Anthropic = require('@anthropic-ai/sdk');

// Initialize AI clients
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || 'sk-demo',
});

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || 'sk-ant-demo',
});

/**
 * Query a specific AI model
 * @param {string} modelId - Model identifier
 * @param {string} query - User query
 * @param {object} options - Query options (timeout, powerLevel)
 * @returns {Promise<object>} Response with text and confidence
 */
async function queryAgent(modelId, query, options = {}) {
  const { timeout = 60000, powerLevel = 80 } = options;

  console.log(`[Agent ${modelId}] Querying...`);

  // Create timeout promise
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Agent timeout')), timeout)
  );

  // Route to appropriate provider
  let responsePromise;

  if (modelId.startsWith('gpt-')) {
    responsePromise = queryOpenAI(modelId, query, powerLevel);
  } else if (modelId.startsWith('claude-')) {
    responsePromise = queryAnthropic(modelId, query, powerLevel);
  } else if (modelId.startsWith('gemini-')) {
    responsePromise = queryGemini(modelId, query, powerLevel);
  } else {
    responsePromise = queryMock(modelId, query, powerLevel);
  }

  // Race against timeout
  return Promise.race([responsePromise, timeoutPromise]);
}

/**
 * Query OpenAI models
 */
async function queryOpenAI(modelId, query, powerLevel) {
  try {
    const response = await openai.chat.completions.create({
      model: modelId,
      messages: [{ role: 'user', content: query }],
      temperature: 1 - (powerLevel / 200), // Lower temp for higher power
      max_tokens: Math.floor(4000 * (powerLevel / 100)),
    });

    return {
      text: response.choices[0].message.content,
      confidence: 0.9,
    };
  } catch (error) {
    if (error.message.includes('API key')) {
      // Fallback to mock for demo
      return queryMock(modelId, query, powerLevel);
    }
    throw error;
  }
}

/**
 * Query Anthropic models
 */
async function queryAnthropic(modelId, query, powerLevel) {
  try {
    const response = await anthropic.messages.create({
      model: modelId,
      max_tokens: Math.floor(4000 * (powerLevel / 100)),
      messages: [{ role: 'user', content: query }],
    });

    return {
      text: response.content[0].text,
      confidence: 0.95,
    };
  } catch (error) {
    if (error.message.includes('API key')) {
      return queryMock(modelId, query, powerLevel);
    }
    throw error;
  }
}

/**
 * Query Google Gemini models (placeholder)
 */
async function queryGemini(modelId, query, powerLevel) {
  // TODO: Implement Gemini API when available
  return queryMock(modelId, query, powerLevel);
}

/**
 * Mock AI response (for testing without API keys)
 */
async function queryMock(modelId, query, powerLevel) {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, Math.random() * 1000 + 500));

  const responses = [
    `[${modelId}] Based on my analysis, this question requires a comprehensive approach. Here's my perspective: ${query.slice(0, 50)}... The key considerations are accuracy, relevance, and depth of understanding.`,

    `[${modelId}] Excellent question! Let me break this down systematically. For "${query.slice(0, 40)}...", we should consider multiple angles including technical feasibility, practical implementation, and long-term implications.`,

    `[${modelId}] This is an interesting query that touches on several important aspects. My recommendation would be to approach this methodically, considering both theoretical foundations and real-world applications.`,
  ];

  const response = responses[Math.floor(Math.random() * responses.length)];

  return {
    text: response,
    confidence: 0.7 + (Math.random() * 0.2), // 0.7-0.9
  };
}

module.exports = { queryAgent };
