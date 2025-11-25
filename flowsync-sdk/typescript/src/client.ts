/**
 * FlowSync Client — The main interface to 0r8 Brain
 */

import type {
  FlowSyncConfig,
  RouteRequest,
  RouteResponse,
  SystemStatus,
  GovernanceStatus,
  AgentFingerprint,
  AuthorizationRequest,
  AuthorizationResponse,
} from './types';

export class FlowSyncError extends Error {
  constructor(
    message: string,
    public code?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'FlowSyncError';
  }
}

export class AuthenticationError extends FlowSyncError {
  constructor(message: string) {
    super(message, 403);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends FlowSyncError {
  constructor(message: string) {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}

/**
 * FlowSync SDK Client
 *
 * The main interface to the 0r8 Brain API.
 * Route messages through 3i-ATLAS, summon Demigods, and harness the power
 * of Intelligence, Intuition, and Integration.
 *
 * @example
 * ```typescript
 * const client = new FlowSync({ apiKey: 'your-api-key' });
 * const response = await client.route({
 *   userId: 'user-123',
 *   message: 'Help me analyze this data',
 *   mode: 'analyst',
 *   demigod: 'athena'
 * });
 * ```
 */
export class FlowSync {
  private apiKey: string;
  private baseUrl: string;
  private timeout: number;

  constructor(config: FlowSyncConfig) {
    this.apiKey = config.apiKey;
    this.baseUrl = (config.baseUrl || 'http://127.0.0.1:3000').replace(/\/$/, '');
    this.timeout = config.timeout || 30000;
  }

  private async request<T>(
    method: 'GET' | 'POST',
    endpoint: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (response.status === 403) {
          throw new AuthenticationError('Authentication failed');
        }
        if (response.status === 429) {
          throw new RateLimitError('Rate limit exceeded');
        }
        throw new FlowSyncError(
          `API error: ${response.statusText}`,
          response.status
        );
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof FlowSyncError) throw error;
      throw new FlowSyncError(`Request failed: ${error}`);
    }
  }

  // ═══════════════════════════════════════════════════════════════
  // CORE ROUTING
  // ═══════════════════════════════════════════════════════════════

  /**
   * Route a message through 3i-ATLAS.
   *
   * This is the core method for interacting with 0r8. It determines:
   * - Which Demigod should handle the request
   * - What 3i weights to apply
   * - What temperature and model tier to use
   * - Which AGI modules to activate
   */
  async route(request: RouteRequest): Promise<RouteResponse> {
    const body = {
      user_id: request.userId,
      message: request.message,
      mode: request.mode,
      domain: request.domain,
      demigod: request.demigod,
      historical_flavor: request.historicalFlavor,
      custom_weights: request.customWeights,
    };

    const response = await this.request<any>('POST', '/route', body);

    // Transform snake_case to camelCase
    return {
      weights: response.weights,
      dominantPillar: response.dominant_pillar,
      demigod: response.demigod,
      historicalFlavor: response.historical_flavor,
      temperature: response.temperature,
      modelTier: response.model_tier,
      userHarmony: {
        userId: response.user_harmony.user_id,
        nousLevel: response.user_harmony.nous_level,
        animaLevel: response.user_harmony.anima_level,
        holosLevel: response.user_harmony.holos_level,
        harmonyScore: response.user_harmony.harmony_score,
        isUnified: response.user_harmony.is_unified,
        totalInteractions: response.user_harmony.total_interactions,
      },
      domainContext: response.domain_context,
      activeModules: response.active_modules,
      transmutation: response.transmutation,
      community: response.community,
    };
  }

  /**
   * Quick routing for simple use cases.
   */
  async quickRoute(message: string, mode: string = 'sage'): Promise<RouteResponse> {
    return this.route({
      userId: 'quick-user',
      message,
      mode: mode as any,
    });
  }

  // ═══════════════════════════════════════════════════════════════
  // DEMIGODS
  // ═══════════════════════════════════════════════════════════════

  async listDemigods(): Promise<Record<string, any>> {
    return this.request('GET', '/demigods');
  }

  async getDemigod(name: string): Promise<any> {
    return this.request('GET', `/demigods/${name}`);
  }

  // ═══════════════════════════════════════════════════════════════
  // DOMAINS
  // ═══════════════════════════════════════════════════════════════

  async listDomains(): Promise<Record<string, any>> {
    return this.request('GET', '/domains');
  }

  // ═══════════════════════════════════════════════════════════════
  // AGI MODULES
  // ═══════════════════════════════════════════════════════════════

  async listModules(): Promise<any> {
    return this.request('GET', '/modules');
  }

  async getModule(name: string): Promise<any> {
    return this.request('GET', `/modules/${name}`);
  }

  // ═══════════════════════════════════════════════════════════════
  // HISTORICAL FLAVORS
  // ═══════════════════════════════════════════════════════════════

  async listFlavors(): Promise<Record<string, any>> {
    return this.request('GET', '/flavors');
  }

  // ═══════════════════════════════════════════════════════════════
  // USER HARMONY
  // ═══════════════════════════════════════════════════════════════

  async getHarmony(userId: string): Promise<any> {
    return this.request('GET', `/harmony/${userId}`);
  }

  // ═══════════════════════════════════════════════════════════════
  // GOVERNANCE
  // ═══════════════════════════════════════════════════════════════

  async governanceStatus(): Promise<GovernanceStatus> {
    const response = await this.request<any>('GET', '/governance');
    return {
      totalKeys: response.total_keys,
      activeKeys: response.active_keys,
      totalAgents: response.total_agents,
      pendingVotes: response.pending_votes,
      executedActions: response.executed_actions,
      keysByType: response.keys_by_type,
      keyTypes: response.key_types,
      riskLevels: response.risk_levels,
      competenceLevels: response.competence_levels,
      keyRequirements: response.key_requirements,
    };
  }

  async registerAgent(agentId: string, name: string): Promise<AgentFingerprint> {
    const response = await this.request<any>('POST', '/governance/agents', {
      agent_id: agentId,
      name,
    });
    const fp = response.fingerprint;
    return {
      agentId: fp.agent_id,
      name: fp.name,
      alignmentScore: fp.alignment_score,
      competenceLevel: fp.competence_level,
      riskScore: fp.risk_score,
      autonomyCeiling: fp.autonomy_ceiling,
      successRate: fp.success_rate,
      totalActions: fp.total_actions,
      flaggedActions: fp.flagged_actions,
      certifications: fp.certifications,
      createdAt: fp.created_at,
      lastAction: fp.last_action,
    };
  }

  async getAgentFingerprint(agentId: string): Promise<AgentFingerprint> {
    const fp = await this.request<any>('GET', `/governance/agents/${agentId}`);
    return {
      agentId: fp.agent_id,
      name: fp.name,
      alignmentScore: fp.alignment_score,
      competenceLevel: fp.competence_level,
      riskScore: fp.risk_score,
      autonomyCeiling: fp.autonomy_ceiling,
      successRate: fp.success_rate,
      totalActions: fp.total_actions,
      flaggedActions: fp.flagged_actions,
      certifications: fp.certifications,
      createdAt: fp.created_at,
      lastAction: fp.last_action,
    };
  }

  async requestAuthorization(request: AuthorizationRequest): Promise<AuthorizationResponse> {
    const response = await this.request<any>('POST', '/governance/authorize', {
      action_id: request.actionId,
      action_type: request.actionType,
      risk_level: request.riskLevel,
      agent_id: request.agentId,
    });
    return {
      approved: response.approved,
      message: response.message,
      pendingVote: response.pending_vote ? {
        actionId: response.pending_vote.action_id,
        actionType: response.pending_vote.action_type,
        riskLevel: response.pending_vote.risk_level,
        requiredKeys: response.pending_vote.required_keys,
        currentVotes: response.pending_vote.current_votes,
        approvals: response.pending_vote.approvals,
        isApproved: response.pending_vote.is_approved,
        isRejected: response.pending_vote.is_rejected,
        executed: response.pending_vote.executed,
        expiresAt: response.pending_vote.expires_at,
      } : null,
    };
  }

  async getLeaderboard(limit: number = 10): Promise<any[]> {
    const response = await this.request<any>('GET', `/governance/leaderboard?limit=${limit}`);
    return response.leaderboard;
  }

  // ═══════════════════════════════════════════════════════════════
  // SYSTEM
  // ═══════════════════════════════════════════════════════════════

  async status(): Promise<SystemStatus> {
    const url = `${this.baseUrl}/`;
    const response = await fetch(url);
    return response.json();
  }

  async stats(): Promise<any> {
    return this.request('GET', '/stats');
  }
}
