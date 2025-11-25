/**
 * FlowSync Type Definitions
 * The 0r8 3i Architecture type system
 */

// ═══════════════════════════════════════════════════════════════
// ENUMS
// ═══════════════════════════════════════════════════════════════

export type Pillar = 'nous' | 'anima' | 'holos';

export type ProcessingMode = 'analyst' | 'creator' | 'executor' | 'sage' | 'transcendent';

export type CompetenceLevel = 'novice' | 'intermediate' | 'expert' | 'master';

export type RiskLevel = 'minimal' | 'low' | 'medium' | 'high' | 'critical';

export type DemigodId = 'athena' | 'mercury' | 'hephaestus' | 'apollo' | 'artemis' | 'hermes' | 'ares';

export type DomainId = 'work' | 'school' | 'sports' | 'create' | 'spiritual' | 'social' | 'health' | 'life';

export type HistoricalFlavorId = 'leonardo' | 'tesla' | 'jobs' | 'sun_tzu' | 'rumi' | 'curie' | 'einstein' | 'aurelius';

// ═══════════════════════════════════════════════════════════════
// CORE TYPES
// ═══════════════════════════════════════════════════════════════

export interface ThreeIWeights {
  nous: number;   // I₁ — Intelligence
  anima: number;  // I₂ — Intuition
  holos: number;  // I₃ — Integration
}

export interface Demigod {
  id: DemigodId;
  name: string;
  pillar: Pillar;
  domain: string;
  specialty: string;
  voice: string;
  symbol: string;
  defaultWeights: ThreeIWeights;
}

export interface Domain {
  id: DomainId;
  name: string;
  icon: string;
  description: string;
  defaultWeights: ThreeIWeights;
  suggestedDemigods: DemigodId[];
}

// ═══════════════════════════════════════════════════════════════
// REQUEST/RESPONSE TYPES
// ═══════════════════════════════════════════════════════════════

export interface RouteRequest {
  userId: string;
  message: string;
  mode?: ProcessingMode;
  domain?: DomainId;
  demigod?: DemigodId;
  historicalFlavor?: HistoricalFlavorId;
  customWeights?: Partial<ThreeIWeights>;
}

export interface TransmutationStage {
  stage: number;
  name: string;
  description: string;
  processor: string;
  intensity?: number;
  status: string;
}

export interface TransmutationCascade {
  cascade: string;
  stages: TransmutationStage[];
  axiom: string;
}

export interface ActiveModule {
  name: string;
  module: string;
  activationLevel: number;
  capabilities: string[];
}

export interface ActiveModules {
  nous: ActiveModule[];
  anima: ActiveModule[];
  holos: ActiveModule[];
}

export interface UserHarmony {
  userId: string;
  nousLevel: number;
  animaLevel: number;
  holosLevel: number;
  harmonyScore: number;
  isUnified: boolean;
  totalInteractions: number;
}

export interface CommunityInfo {
  name: string;
  movement: string;
  revealDate: string;
}

export interface RouteResponse {
  weights: ThreeIWeights;
  dominantPillar: Pillar;
  demigod: {
    name: string;
    pillar: Pillar;
    domain: string;
    specialty: string;
    voice: string;
    symbol: string;
  };
  historicalFlavor: string | null;
  temperature: number;
  modelTier: 'fast' | 'standard' | 'premium';
  userHarmony: UserHarmony;
  domainContext: string | null;
  activeModules: ActiveModules;
  transmutation: TransmutationCascade;
  community: CommunityInfo;
}

// ═══════════════════════════════════════════════════════════════
// GOVERNANCE TYPES
// ═══════════════════════════════════════════════════════════════

export interface AgentFingerprint {
  agentId: string;
  name: string;
  alignmentScore: number;
  competenceLevel: CompetenceLevel;
  riskScore: number;
  autonomyCeiling: number;
  successRate: number;
  totalActions: number;
  flaggedActions: number;
  certifications: string[];
  createdAt: string;
  lastAction: string | null;
}

export interface GovernanceStatus {
  totalKeys: number;
  activeKeys: number;
  totalAgents: number;
  pendingVotes: number;
  executedActions: number;
  keysByType: Record<string, number>;
  keyTypes: string[];
  riskLevels: string[];
  competenceLevels: string[];
  keyRequirements: Record<string, number>;
}

export interface AuthorizationRequest {
  actionId: string;
  actionType: string;
  riskLevel: RiskLevel;
  agentId: string;
}

export interface AuthorizationResponse {
  approved: boolean;
  message: string;
  pendingVote: {
    actionId: string;
    actionType: string;
    riskLevel: string;
    requiredKeys: number;
    currentVotes: number;
    approvals: number;
    isApproved: boolean;
    isRejected: boolean;
    executed: boolean;
    expiresAt: string;
  } | null;
}

// ═══════════════════════════════════════════════════════════════
// CLIENT TYPES
// ═══════════════════════════════════════════════════════════════

export interface FlowSyncConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
}

export interface SystemStatus {
  name: string;
  tagline: string;
  version: string;
  status: string;
  cycles: number;
  performance: string;
  pillars: Record<Pillar, string>;
  demigods: DemigodId[];
  domains: DomainId[];
  security: {
    gate: string;
    auditLog: string;
    costTracking: string;
    encryption: string;
  };
}
