import { AxiosRequestConfig } from 'axios';
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
export declare class CompetitionBrain {
    private client;
    private baseUrl;
    constructor(options?: CompetitionBrainOptions);
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
    query(query: string, config: QueryConfig): Promise<QueryResult>;
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
    getModels(): Promise<Model[]>;
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
    health(): Promise<HealthResponse>;
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
    competitionQuery(query: string): Promise<QueryResult>;
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
    fastQuery(query: string): Promise<QueryResult>;
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
    freeQuery(query: string): Promise<QueryResult>;
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
    getStats(result: QueryResult): {
        totalModels: number;
        successfulModels: number;
        failedModels: number;
        avgConfidence: number;
        avgTime: number;
        totalTime: number;
        cached: boolean;
        cacheAge: number | undefined;
    };
    /**
     * Export result to JSON file format
     *
     * @param result - Query result
     * @returns JSON string
     */
    exportJSON(result: QueryResult): string;
    /**
     * Export result to Markdown format
     *
     * @param result - Query result
     * @returns Markdown string
     */
    exportMarkdown(result: QueryResult): string;
}
export default CompetitionBrain;
