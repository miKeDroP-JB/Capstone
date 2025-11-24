/**
 * 0r8 Type Definitions
 * The Operating System for Human Potential
 */

// ═══════════════════════════════════════════════════════════════
// 3i FRAMEWORK TYPES
// ═══════════════════════════════════════════════════════════════

export type Pillar = "nous" | "anima" | "holos";

export type ProcessingMode =
  | "analyst"
  | "creator"
  | "executor"
  | "sage"
  | "transcendent";

export interface ThreeIWeights {
  nous: number; // 0-1 — Intelligence
  anima: number; // 0-1 — Intuition
  holos: number; // 0-1 — Integration
}

// ═══════════════════════════════════════════════════════════════
// DEMIGODS
// ═══════════════════════════════════════════════════════════════

export interface Demigod {
  id: string;
  name: string;
  pillar: Pillar;
  domain: string;
  specialty: string;
  voice: string;
  symbol: string;
  defaultWeights: ThreeIWeights;
}

export type DemigodId =
  | "athena"
  | "mercury"
  | "hephaestus"
  | "apollo"
  | "artemis"
  | "hermes"
  | "ares";

// ═══════════════════════════════════════════════════════════════
// LIFE DOMAINS
// ═══════════════════════════════════════════════════════════════

export interface LifeDomain {
  id: string;
  name: string;
  icon: string;
  description: string;
  defaultWeights: ThreeIWeights;
  suggestedDemigods: DemigodId[];
}

export type DomainId =
  | "work"
  | "school"
  | "sports"
  | "create"
  | "spiritual"
  | "social"
  | "health"
  | "life";

// ═══════════════════════════════════════════════════════════════
// HISTORICAL FLAVORS
// ═══════════════════════════════════════════════════════════════

export interface HistoricalFlavor {
  id: string;
  name: string;
  essence: string;
  era: string;
  weights: ThreeIWeights;
}

// ═══════════════════════════════════════════════════════════════
// USER & HARMONY
// ═══════════════════════════════════════════════════════════════

export interface User {
  id: string;
  email: string;
  name?: string;
  walletAddress?: string;
  createdAt: string;
}

export interface UserHarmony {
  userId: string;
  nousLevel: number; // 0-100
  animaLevel: number; // 0-100
  holosLevel: number; // 0-100
  totalInteractions: number;
  harmonyScore: number; // Average of all three
  isUnified: boolean; // All pillars >= 70
}

// ═══════════════════════════════════════════════════════════════
// CHAT & MESSAGES
// ═══════════════════════════════════════════════════════════════

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  createdAt: string;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  demigod?: DemigodId;
  weights?: ThreeIWeights;
  tokensUsed?: number;
  model?: string;
  historicalFlavor?: string;
}

export interface Conversation {
  id: string;
  userId: string;
  title?: string;
  domain?: DomainId;
  demigod?: DemigodId;
  historicalFlavor?: string;
  weights: ThreeIWeights;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

// ═══════════════════════════════════════════════════════════════
// ROUTING
// ═══════════════════════════════════════════════════════════════

export interface RouteRequest {
  userId: string;
  message: string;
  mode?: ProcessingMode;
  domain?: DomainId;
  demigod?: DemigodId;
  historicalFlavor?: string;
  customWeights?: Partial<ThreeIWeights>;
}

export interface RouteResponse {
  weights: ThreeIWeights;
  dominantPillar: Pillar;
  demigod: Demigod;
  historicalFlavor?: string;
  temperature: number;
  modelTier: "fast" | "standard" | "premium";
  userHarmony: UserHarmony;
  domainContext?: string;
}

// ═══════════════════════════════════════════════════════════════
// API RESPONSES
// ═══════════════════════════════════════════════════════════════

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// ═══════════════════════════════════════════════════════════════
// UI STATE
// ═══════════════════════════════════════════════════════════════

export interface ThreeIModeConfig {
  mode: ProcessingMode;
  weights: ThreeIWeights;
  domain?: DomainId;
  demigod?: DemigodId;
  historicalFlavor?: string;
}

export interface ParticleConfig {
  type: Pillar;
  count: number;
  speed: number;
  connectDistance: number;
}
