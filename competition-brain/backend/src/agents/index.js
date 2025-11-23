require('dotenv').config();
const OpenAI = require('openai');
const Anthropic = require('@anthropic-ai/sdk');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const MistralClient = require('@mistralai/mistralai');
const { CohereClient } = require('cohere-ai');
const Groq = require('groq-sdk');
const axios = require('axios');

// Initialize AI clients
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || 'sk-demo',
});

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || 'sk-ant-demo',
});

const gemini = process.env.GOOGLE_API_KEY
  ? new GoogleGenerativeAI(process.env.GOOGLE_API_KEY)
  : null;

const mistral = process.env.MISTRAL_API_KEY
  ? new MistralClient(process.env.MISTRAL_API_KEY)
  : null;

const cohere = process.env.COHERE_API_KEY
  ? new CohereClient({ token: process.env.COHERE_API_KEY })
  : null;

const groq = process.env.GROQ_API_KEY
  ? new Groq({ apiKey: process.env.GROQ_API_KEY })
  : null;

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

  // Route to appropriate provider based on model ID
  let responsePromise;

  // OpenAI models (GPT and o1)
  if (modelId === 'o1' || modelId.startsWith('gpt-')) {
    responsePromise = queryOpenAI(modelId, query, powerLevel);
  }
  // Anthropic Claude models
  else if (modelId.startsWith('claude-')) {
    responsePromise = queryAnthropic(modelId, query, powerLevel);
  }
  // Google Gemini models
  else if (modelId.startsWith('gemini-')) {
    responsePromise = queryGemini(modelId, query, powerLevel);
  }
  // Mistral models
  else if (modelId.startsWith('mistral-')) {
    responsePromise = queryMistral(modelId, query, powerLevel);
  }
  // Cohere models
  else if (modelId.startsWith('command-')) {
    responsePromise = queryCohere(modelId, query, powerLevel);
  }
  // Llama models via Groq
  else if (modelId.startsWith('llama-')) {
    responsePromise = queryGroq(modelId, query, powerLevel);
  }
  // DeepSeek models
  else if (modelId.startsWith('deepseek-')) {
    responsePromise = queryDeepSeek(modelId, query, powerLevel);
  }
  // xAI Grok models
  else if (modelId.startsWith('grok-')) {
    responsePromise = queryXAI(modelId, query, powerLevel);
  }
  // Qwen/Alibaba models
  else if (modelId.startsWith('qwen-')) {
    responsePromise = queryQwen(modelId, query, powerLevel);
  }
  // Perplexity (web-grounded)
  else if (modelId === 'perplexity') {
    responsePromise = queryPerplexity(modelId, query, powerLevel);
  }
  // Fallback to mock
  else {
    responsePromise = queryMock(modelId, query, powerLevel);
  }

  // Race against timeout
  return Promise.race([responsePromise, timeoutPromise]);
}

/**
 * Query OpenAI models (GPT-4o, GPT-4o-mini, o1)
 */
async function queryOpenAI(modelId, query, powerLevel) {
  try {
    // Special handling for o1 reasoning model
    const isO1 = modelId === 'o1' || modelId === 'o1-preview' || modelId === 'o1-mini';

    const params = {
      model: modelId === 'o1' ? 'o1-preview' : modelId, // Map o1 to o1-preview
      messages: [{ role: 'user', content: query }],
    };

    // o1 doesn't support temperature or max_tokens in the same way
    if (!isO1) {
      params.temperature = 1 - (powerLevel / 200); // Lower temp for higher power
      params.max_tokens = Math.floor(4000 * (powerLevel / 100));
    }

    const response = await openai.chat.completions.create(params);

    return {
      text: response.choices[0].message.content,
      confidence: isO1 ? 0.99 : 0.92, // o1 has very high confidence
    };
  } catch (error) {
    console.error(`[OpenAI ${modelId}] Error:`, error.message);
    if (error.message.includes('API key') || error.message.includes('auth')) {
      return queryMock(modelId, query, powerLevel);
    }
    throw error;
  }
}

/**
 * Query Anthropic Claude models (Sonnet, Haiku)
 */
async function queryAnthropic(modelId, query, powerLevel) {
  try {
    // Map friendly names to API model names
    const modelMap = {
      'claude-sonnet-4.5': 'claude-sonnet-4-20250514',
      'claude-3.7-sonnet': 'claude-3-7-sonnet-20250219',
      'claude-3-5-haiku': 'claude-3-5-haiku-20241022',
    };

    const apiModel = modelMap[modelId] || modelId;

    const response = await anthropic.messages.create({
      model: apiModel,
      max_tokens: Math.floor(4000 * (powerLevel / 100)),
      messages: [{ role: 'user', content: query }],
    });

    return {
      text: response.content[0].text,
      confidence: modelId.includes('4.5') ? 0.98 : 0.95,
    };
  } catch (error) {
    console.error(`[Anthropic ${modelId}] Error:`, error.message);
    if (error.message.includes('API key') || error.message.includes('auth')) {
      return queryMock(modelId, query, powerLevel);
    }
    throw error;
  }
}

/**
 * Query Google Gemini models
 */
async function queryGemini(modelId, query, powerLevel) {
  if (!gemini) {
    console.log(`[Gemini ${modelId}] No API key, using mock`);
    return queryMock(modelId, query, powerLevel);
  }

  try {
    // Map friendly names to API model names
    const modelMap = {
      'gemini-exp-1206': 'gemini-exp-1206',
      'gemini-2.0-flash-thinking': 'gemini-2.0-flash-thinking-exp-01-21',
      'gemini-1.5-flash': 'gemini-1.5-flash',
      'gemini-1.5-pro': 'gemini-1.5-pro',
    };

    const apiModel = modelMap[modelId] || modelId;
    const model = gemini.getGenerativeModel({ model: apiModel });

    const result = await model.generateContent({
      contents: [{ role: 'user', parts: [{ text: query }] }],
      generationConfig: {
        temperature: 1 - (powerLevel / 200),
        maxOutputTokens: Math.floor(4000 * (powerLevel / 100)),
      },
    });

    const response = result.response;
    const text = response.text();

    return {
      text,
      confidence: modelId.includes('exp') ? 0.97 : 0.90,
    };
  } catch (error) {
    console.error(`[Gemini ${modelId}] Error:`, error.message);
    return queryMock(modelId, query, powerLevel);
  }
}

/**
 * Query Mistral models
 */
async function queryMistral(modelId, query, powerLevel) {
  if (!mistral) {
    console.log(`[Mistral ${modelId}] No API key, using mock`);
    return queryMock(modelId, query, powerLevel);
  }

  try {
    const response = await mistral.chat({
      model: modelId === 'mistral-small' ? 'mistral-small-latest' : modelId,
      messages: [{ role: 'user', content: query }],
      temperature: 1 - (powerLevel / 200),
      maxTokens: Math.floor(4000 * (powerLevel / 100)),
    });

    return {
      text: response.choices[0].message.content,
      confidence: 0.85,
    };
  } catch (error) {
    console.error(`[Mistral ${modelId}] Error:`, error.message);
    return queryMock(modelId, query, powerLevel);
  }
}

/**
 * Query Cohere models (Command R7B)
 */
async function queryCohere(modelId, query, powerLevel) {
  if (!cohere) {
    console.log(`[Cohere ${modelId}] No API key, using mock`);
    return queryMock(modelId, query, powerLevel);
  }

  try {
    const response = await cohere.chat({
      model: modelId === 'command-r7b' ? 'command-r' : modelId,
      message: query,
      temperature: 1 - (powerLevel / 200),
      maxTokens: Math.floor(4000 * (powerLevel / 100)),
    });

    return {
      text: response.text,
      confidence: 0.88,
    };
  } catch (error) {
    console.error(`[Cohere ${modelId}] Error:`, error.message);
    return queryMock(modelId, query, powerLevel);
  }
}

/**
 * Query Llama models via Groq (fast inference)
 */
async function queryGroq(modelId, query, powerLevel) {
  if (!groq) {
    console.log(`[Groq ${modelId}] No API key, using mock`);
    return queryMock(modelId, query, powerLevel);
  }

  try {
    // Map to Groq model names
    const modelMap = {
      'llama-3.3-70b': 'llama-3.3-70b-versatile',
      'llama-3.1-70b': 'llama-3.1-70b-versatile',
    };

    const apiModel = modelMap[modelId] || modelId;

    const response = await groq.chat.completions.create({
      model: apiModel,
      messages: [{ role: 'user', content: query }],
      temperature: 1 - (powerLevel / 200),
      max_tokens: Math.floor(4000 * (powerLevel / 100)),
    });

    return {
      text: response.choices[0].message.content,
      confidence: 0.86,
    };
  } catch (error) {
    console.error(`[Groq ${modelId}] Error:`, error.message);
    return queryMock(modelId, query, powerLevel);
  }
}

/**
 * Query DeepSeek models via API
 */
async function queryDeepSeek(modelId, query, powerLevel) {
  const apiKey = process.env.DEEPSEEK_API_KEY;

  if (!apiKey) {
    console.log(`[DeepSeek ${modelId}] No API key, using mock`);
    return queryMock(modelId, query, powerLevel);
  }

  try {
    const response = await axios.post(
      'https://api.deepseek.com/v1/chat/completions',
      {
        model: modelId === 'deepseek-v3' ? 'deepseek-chat' : modelId,
        messages: [{ role: 'user', content: query }],
        temperature: 1 - (powerLevel / 200),
        max_tokens: Math.floor(4000 * (powerLevel / 100)),
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
      }
    );

    return {
      text: response.data.choices[0].message.content,
      confidence: 0.92, // DeepSeek V3 is very strong
    };
  } catch (error) {
    console.error(`[DeepSeek ${modelId}] Error:`, error.message);
    return queryMock(modelId, query, powerLevel);
  }
}

/**
 * Query xAI Grok models
 */
async function queryXAI(modelId, query, powerLevel) {
  const apiKey = process.env.XAI_API_KEY;

  if (!apiKey) {
    console.log(`[xAI ${modelId}] No API key, using mock`);
    return queryMock(modelId, query, powerLevel);
  }

  try {
    const response = await axios.post(
      'https://api.x.ai/v1/chat/completions',
      {
        model: modelId === 'grok-2' ? 'grok-2-latest' : modelId,
        messages: [{ role: 'user', content: query }],
        temperature: 1 - (powerLevel / 200),
        max_tokens: Math.floor(4000 * (powerLevel / 100)),
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
      }
    );

    return {
      text: response.data.choices[0].message.content,
      confidence: 0.90,
    };
  } catch (error) {
    console.error(`[xAI ${modelId}] Error:`, error.message);
    return queryMock(modelId, query, powerLevel);
  }
}

/**
 * Query Qwen/Alibaba models
 */
async function queryQwen(modelId, query, powerLevel) {
  // Qwen can be accessed via various platforms (Replicate, HuggingFace, etc.)
  // For now, using mock until specific API endpoint is configured
  console.log(`[Qwen ${modelId}] Using mock (configure API endpoint for real integration)`);
  return queryMock(modelId, query, powerLevel);
}

/**
 * Query Perplexity (web-grounded responses)
 */
async function queryPerplexity(modelId, query, powerLevel) {
  const apiKey = process.env.PERPLEXITY_API_KEY;

  if (!apiKey) {
    console.log(`[Perplexity ${modelId}] No API key, using mock`);
    return queryMock(modelId, query, powerLevel);
  }

  try {
    const response = await axios.post(
      'https://api.perplexity.ai/chat/completions',
      {
        model: 'llama-3.1-sonar-large-128k-online',
        messages: [{ role: 'user', content: query }],
        temperature: 1 - (powerLevel / 200),
        max_tokens: Math.floor(4000 * (powerLevel / 100)),
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
      }
    );

    return {
      text: response.data.choices[0].message.content,
      confidence: 0.94, // Web-grounded = higher confidence for facts
    };
  } catch (error) {
    console.error(`[Perplexity ${modelId}] Error:`, error.message);
    return queryMock(modelId, query, powerLevel);
  }
}

/**
 * Mock AI response (for testing without API keys)
 */
async function queryMock(modelId, query, powerLevel) {
  // Simulate network delay based on power level (higher power = longer processing)
  const delay = 500 + Math.random() * 1000 * (powerLevel / 100);
  await new Promise((resolve) => setTimeout(resolve, delay));

  const responses = [
    `[${modelId}] Based on my analysis, this question requires a comprehensive approach. Here's my perspective: ${query.slice(0, 50)}... The key considerations are accuracy, relevance, and depth of understanding.`,

    `[${modelId}] Excellent question! Let me break this down systematically. For "${query.slice(0, 40)}...", we should consider multiple angles including technical feasibility, practical implementation, and long-term implications.`,

    `[${modelId}] This is an interesting query that touches on several important aspects. My recommendation would be to approach this methodically, considering both theoretical foundations and real-world applications.`,

    `[${modelId}] After careful consideration of your query about "${query.slice(0, 45)}...", I believe the optimal solution involves balancing efficiency with effectiveness while maintaining scalability.`,
  ];

  const response = responses[Math.floor(Math.random() * responses.length)];

  return {
    text: response,
    confidence: 0.65 + (Math.random() * 0.15), // 0.65-0.80 for mock
  };
}

module.exports = { queryAgent };
