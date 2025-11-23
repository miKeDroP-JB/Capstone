import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

/**
 * Model information
 */
export interface Model {
  id: string;
  name: string;
  provider: string;
  free: boolean;
  power: number;
}

/**
 * Query configuration
 */
export interface QueryConfig {
  /** Array of model IDs to query */
  models: string[];
  /** Only use free models */
  freeOnly?: boolean;
  /** Time limit in seconds (5-300) */
  timeLimit?: number;
  /** Power level percentage (0-100) */
  powerLevel?: number;
  /** Enable response caching (default: true) */
  useCache?: boolean;
}

/**
 * Individual agent response
 */
export interface AgentResponse {
  model: string;
  response: string;
  confidence: number;
  time: number;
  success: boolean;
}

/**
 * Complete query result
 */
export interface QueryResult {
  id: string;
  query: string;
  synthesized: string;
  individual: AgentResponse[];
  totalTime: number;
  timestamp: Date;
  cached?: boolean;
  cacheAge?: number;
}

/**
 * Health check response
 */
export interface HealthResponse {
  status: 'ok' | 'error';
  version: string;
}

/**
 * Competition Brain Client Options
 */
export interface CompetitionBrainOptions {
  /** Base URL of the Competition Brain API */
  baseUrl?: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Custom axios configuration */
  axiosConfig?: AxiosRequestConfig;
}

/**
 * Official Competition Brain Client
 *
 * Multi-Agent AI Orchestration for competitions, research, and production use.
 *
 * @example
 * ```typescript
 * const client = new CompetitionBrain({ baseUrl: 'http://localhost:3001' });
 *
 * const result = await client.query('What is 2+2?', {
 *   models: ['gpt-4o', 'claude-sonnet-4.5'],
 *   powerLevel: 80
 * });
 *
 * console.log(result.synthesized);
 * ```
 */
export class CompetitionBrain {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(options: CompetitionBrainOptions = {}) {
    this.baseUrl = options.baseUrl || 'http://localhost:3001';

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: options.timeout || 300000, // 5 minute default
      headers: {
        'Content-Type': 'application/json',
      },
      ...options.axiosConfig,
    });
  }

  /**
   * Query multiple AI models and synthesize responses
   *
   * @param query - The question or prompt
   * @param config - Query configuration (models, settings)
   * @returns Promise<QueryResult>
   *
   * @example
   * ```typescript
   * const result = await client.query('Explain quantum computing', {
   *   models: ['o1', 'claude-sonnet-4.5', 'gemini-exp-1206'],
   *   powerLevel: 95,
   *   timeLimit: 180
   * });
   * ```
   */
  async query(query: string, config: QueryConfig): Promise<QueryResult> {
    const response = await this.client.post<QueryResult>('/api/query', {
      query,
      config,
    });

    // Convert timestamp string to Date object
    return {
      ...response.data,
      timestamp: new Date(response.data.timestamp),
    };
  }

  /**
   * Get list of available AI models
   *
   * @returns Promise<Model[]>
   *
   * @example
   * ```typescript
   * const models = await client.getModels();
   * const freeModels = models.filter(m => m.free);
   * ```
   */
  async getModels(): Promise<Model[]> {
    const response = await this.client.get<{ models: Model[] }>('/api/models');
    return response.data.models;
  }

  /**
   * Check API health status
   *
   * @returns Promise<HealthResponse>
   *
   * @example
   * ```typescript
   * const health = await client.health();
   * console.log(health.status); // 'ok'
   * ```
   */
  async health(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  /**
   * Query with competition preset (top 5 models, max power)
   *
   * @param query - The question or prompt
   * @returns Promise<QueryResult>
   *
   * @example
   * ```typescript
   * const result = await client.competitionQuery('Solve this: ...');
   * ```
   */
  async competitionQuery(query: string): Promise<QueryResult> {
    const models = await this.getModels();
    const topModels = models
      .sort((a, b) => b.power - a.power)
      .slice(0, 5)
      .map(m => m.id);

    return this.query(query, {
      models: topModels,
      powerLevel: 95,
      timeLimit: 180,
    });
  }

  /**
   * Query with fast preset (3 models, 30s)
   *
   * @param query - The question or prompt
   * @returns Promise<QueryResult>
   *
   * @example
   * ```typescript
   * const result = await client.fastQuery('Quick question?');
   * ```
   */
  async fastQuery(query: string): Promise<QueryResult> {
    const models = await this.getModels();
    const fastModels = models.slice(0, 3).map(m => m.id);

    return this.query(query, {
      models: fastModels,
      powerLevel: 50,
      timeLimit: 30,
    });
  }

  /**
   * Query with free models only
   *
   * @param query - The question or prompt
   * @returns Promise<QueryResult>
   *
   * @example
   * ```typescript
   * const result = await client.freeQuery('Budget-friendly query');
   * ```
   */
  async freeQuery(query: string): Promise<QueryResult> {
    const models = await this.getModels();
    const freeModels = models.filter(m => m.free).map(m => m.id);

    return this.query(query, {
      models: freeModels,
      freeOnly: true,
      powerLevel: 70,
      timeLimit: 60,
    });
  }

  /**
   * Get detailed stats from a query result
   *
   * @param result - Query result
   * @returns Statistics object
   *
   * @example
   * ```typescript
   * const result = await client.query(...);
   * const stats = client.getStats(result);
   * console.log(`Average confidence: ${stats.avgConfidence}%`);
   * ```
   */
  getStats(result: QueryResult) {
    const successful = result.individual.filter(r => r.success);

    return {
      totalModels: result.individual.length,
      successfulModels: successful.length,
      failedModels: result.individual.length - successful.length,
      avgConfidence: successful.reduce((sum, r) => sum + r.confidence, 0) / successful.length,
      avgTime: successful.reduce((sum, r) => sum + r.time, 0) / successful.length,
      totalTime: result.totalTime,
      cached: result.cached || false,
      cacheAge: result.cacheAge,
    };
  }

  /**
   * Export result to JSON file format
   *
   * @param result - Query result
   * @returns JSON string
   */
  exportJSON(result: QueryResult): string {
    return JSON.stringify(result, null, 2);
  }

  /**
   * Export result to Markdown format
   *
   * @param result - Query result
   * @returns Markdown string
   */
  exportMarkdown(result: QueryResult): string {
    const stats = this.getStats(result);

    let md = `# Competition Brain Result\n\n`;
    md += `**Query**: ${result.query}\n\n`;
    md += `**Timestamp**: ${result.timestamp.toISOString()}\n\n`;
    md += `**Total Time**: ${result.totalTime.toFixed(2)}s\n\n`;

    if (result.cached) {
      md += `**Cached**: Yes (${(result.cacheAge! / 1000 / 60).toFixed(1)} minutes old)\n\n`;
    }

    md += `## Synthesized Response\n\n`;
    md += `${result.synthesized}\n\n`;

    md += `## Statistics\n\n`;
    md += `- Models Queried: ${stats.totalModels}\n`;
    md += `- Successful: ${stats.successfulModels}\n`;
    md += `- Failed: ${stats.failedModels}\n`;
    md += `- Average Confidence: ${(stats.avgConfidence * 100).toFixed(1)}%\n`;
    md += `- Average Response Time: ${stats.avgTime.toFixed(2)}s\n\n`;

    md += `## Individual Responses\n\n`;

    result.individual.forEach((resp, i) => {
      md += `### ${i + 1}. ${resp.model}\n\n`;
      md += `- **Confidence**: ${(resp.confidence * 100).toFixed(1)}%\n`;
      md += `- **Time**: ${resp.time.toFixed(2)}s\n`;
      md += `- **Status**: ${resp.success ? '✅ Success' : '❌ Failed'}\n\n`;
      md += `**Response**:\n\n${resp.response}\n\n`;
      md += `---\n\n`;
    });

    return md;
  }
}

// Export everything
export default CompetitionBrain;
