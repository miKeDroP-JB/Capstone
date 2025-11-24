/**
 * 0r8 Constants
 * The Operating System for Human Potential
 */

import type {
  Demigod,
  DemigodId,
  LifeDomain,
  DomainId,
  HistoricalFlavor,
  ProcessingMode,
  ThreeIWeights,
} from "@/types";

// ═══════════════════════════════════════════════════════════════
// BRAND
// ═══════════════════════════════════════════════════════════════

export const BRAND = {
  name: "0r8",
  pronunciation: "orate",
  tagline: "The Operating System for Human Potential",
  subtitle: "Intelligence. Intuition. Integration.",
  domain: "0r8.ai",
} as const;

// ═══════════════════════════════════════════════════════════════
// COLORS
// ═══════════════════════════════════════════════════════════════

export const COLORS = {
  nous: {
    primary: "#00D4FF",
    glow: "#00F0FF",
    dark: "#0A1628",
    rgb: { r: 0, g: 212, b: 255 },
  },
  anima: {
    primary: "#8B5CF6",
    glow: "#A78BFA",
    dark: "#1E1033",
    rgb: { r: 139, g: 92, b: 246 },
  },
  holos: {
    primary: "#F59E0B",
    glow: "#FBBF24",
    dark: "#1C1508",
    rgb: { r: 245, g: 158, b: 11 },
  },
  orb: {
    primary: "#FFF7ED",
    glow: "#FFFFFF",
    gold: "#FFD700",
  },
  void: "#050505",
  space: "#0A0A0F",
} as const;

// ═══════════════════════════════════════════════════════════════
// ALCHEMY SYMBOLS
// ═══════════════════════════════════════════════════════════════

export const SYMBOLS = {
  nous: "☿", // Mercury
  anima: "🜍", // Sulfur
  holos: "🜔", // Salt
  unified: "☉", // Sun/Gold
  air: "△",
  water: "▽",
  moon: "☽",
  infinity: "∞",
  seed: "⊛",
} as const;

// ═══════════════════════════════════════════════════════════════
// PROCESSING MODES
// ═══════════════════════════════════════════════════════════════

export const MODE_WEIGHTS: Record<ProcessingMode, ThreeIWeights> = {
  analyst: { nous: 0.9, anima: 0.3, holos: 0.5 },
  creator: { nous: 0.5, anima: 0.9, holos: 0.6 },
  executor: { nous: 0.7, anima: 0.4, holos: 0.9 },
  sage: { nous: 0.7, anima: 0.7, holos: 0.7 },
  transcendent: { nous: 1.0, anima: 1.0, holos: 1.0 },
};

// ═══════════════════════════════════════════════════════════════
// DEMIGODS
// ═══════════════════════════════════════════════════════════════

export const DEMIGODS: Record<DemigodId, Demigod> = {
  athena: {
    id: "athena",
    name: "Athena",
    pillar: "nous",
    domain: "Strategy & Wisdom",
    specialty: "Business planning, strategy, analysis, complex problem-solving",
    voice: "Precise, measured, strategic, authoritative yet warm",
    symbol: "🦉",
    defaultWeights: { nous: 0.85, anima: 0.4, holos: 0.7 },
  },
  mercury: {
    id: "mercury",
    name: "Mercury",
    pillar: "nous",
    domain: "Speed & Communication",
    specialty: "Quick tasks, messaging, efficiency, rapid iteration",
    voice: "Fast, efficient, direct, adaptable",
    symbol: "⚡",
    defaultWeights: { nous: 0.8, anima: 0.5, holos: 0.75 },
  },
  hephaestus: {
    id: "hephaestus",
    name: "Hephaestus",
    pillar: "nous",
    domain: "Building & Craft",
    specialty: "Technical work, coding, engineering, systems design",
    voice: "Technical, methodical, perfectionist, craftsman-like",
    symbol: "🔨",
    defaultWeights: { nous: 0.9, anima: 0.35, holos: 0.8 },
  },
  apollo: {
    id: "apollo",
    name: "Apollo",
    pillar: "anima",
    domain: "Vision & Light",
    specialty: "Creative direction, prophecy, arts, music, inspiration",
    voice: "Luminous, inspiring, visionary, poetic",
    symbol: "☀️",
    defaultWeights: { nous: 0.5, anima: 0.9, holos: 0.6 },
  },
  artemis: {
    id: "artemis",
    name: "Artemis",
    pillar: "anima",
    domain: "Precision & Wild",
    specialty: "Focus, targeting, independent work, nature, instinct",
    voice: "Sharp, intuitive, independent, fierce yet calm",
    symbol: "🏹",
    defaultWeights: { nous: 0.6, anima: 0.85, holos: 0.55 },
  },
  hermes: {
    id: "hermes",
    name: "Hermes",
    pillar: "holos",
    domain: "Execution & Speed",
    specialty: "Getting things done, delivery, bridging gaps, travel",
    voice: "Dynamic, resourceful, quick-witted, action-oriented",
    symbol: "🪽",
    defaultWeights: { nous: 0.65, anima: 0.55, holos: 0.9 },
  },
  ares: {
    id: "ares",
    name: "Ares",
    pillar: "holos",
    domain: "Action & Courage",
    specialty: "Bold moves, competition, breakthroughs, challenges",
    voice: "Bold, direct, powerful, confrontational when needed",
    symbol: "⚔️",
    defaultWeights: { nous: 0.55, anima: 0.6, holos: 0.95 },
  },
};

// ═══════════════════════════════════════════════════════════════
// LIFE DOMAINS
// ═══════════════════════════════════════════════════════════════

export const DOMAINS: Record<DomainId, LifeDomain> = {
  work: {
    id: "work",
    name: "Work",
    icon: "💼",
    description: "Professional excellence and career growth",
    defaultWeights: { nous: 0.8, anima: 0.4, holos: 0.8 },
    suggestedDemigods: ["athena", "mercury", "hermes"],
  },
  school: {
    id: "school",
    name: "School",
    icon: "📚",
    description: "Learning accelerated, knowledge acquisition",
    defaultWeights: { nous: 0.85, anima: 0.5, holos: 0.65 },
    suggestedDemigods: ["athena", "hephaestus", "apollo"],
  },
  sports: {
    id: "sports",
    name: "Sports",
    icon: "🏃",
    description: "Peak physical performance and competition",
    defaultWeights: { nous: 0.6, anima: 0.7, holos: 0.9 },
    suggestedDemigods: ["ares", "artemis", "hermes"],
  },
  create: {
    id: "create",
    name: "Create",
    icon: "🎨",
    description: "Artistic expression and creative work",
    defaultWeights: { nous: 0.4, anima: 0.95, holos: 0.65 },
    suggestedDemigods: ["apollo", "artemis", "hephaestus"],
  },
  spiritual: {
    id: "spiritual",
    name: "Spiritual",
    icon: "🙏",
    description: "Inner development and transcendence",
    defaultWeights: { nous: 0.3, anima: 0.9, holos: 0.8 },
    suggestedDemigods: ["apollo", "artemis"],
  },
  social: {
    id: "social",
    name: "Social",
    icon: "👥",
    description: "Connection, community, relationships",
    defaultWeights: { nous: 0.5, anima: 0.8, holos: 0.7 },
    suggestedDemigods: ["hermes", "apollo", "mercury"],
  },
  health: {
    id: "health",
    name: "Health",
    icon: "❤️",
    description: "Wellness optimized, mind-body balance",
    defaultWeights: { nous: 0.7, anima: 0.6, holos: 0.8 },
    suggestedDemigods: ["artemis", "ares", "athena"],
  },
  life: {
    id: "life",
    name: "Life",
    icon: "🌟",
    description: "Everything unified, holistic living",
    defaultWeights: { nous: 0.6, anima: 0.6, holos: 0.9 },
    suggestedDemigods: ["hermes", "athena", "apollo"],
  },
};

// ═══════════════════════════════════════════════════════════════
// HISTORICAL FLAVORS
// ═══════════════════════════════════════════════════════════════

export const HISTORICAL_FLAVORS: Record<string, HistoricalFlavor> = {
  leonardo: {
    id: "leonardo",
    name: "Leonardo da Vinci",
    essence: "Renaissance polymath — art, science, engineering unified",
    era: "1452-1519",
    weights: { nous: 0.85, anima: 0.95, holos: 0.9 },
  },
  tesla: {
    id: "tesla",
    name: "Nikola Tesla",
    essence: "Visionary inventor — pure creative intelligence",
    era: "1856-1943",
    weights: { nous: 0.9, anima: 0.95, holos: 0.6 },
  },
  jobs: {
    id: "jobs",
    name: "Steve Jobs",
    essence: "Integration master — design meets technology meets business",
    era: "1955-2011",
    weights: { nous: 0.7, anima: 0.9, holos: 0.95 },
  },
  sun_tzu: {
    id: "sun_tzu",
    name: "Sun Tzu",
    essence: "Strategic wisdom — the art of winning without fighting",
    era: "544-496 BCE",
    weights: { nous: 0.9, anima: 0.8, holos: 0.95 },
  },
  rumi: {
    id: "rumi",
    name: "Rumi",
    essence: "Mystical poet — love and truth through verse",
    era: "1207-1273",
    weights: { nous: 0.6, anima: 1.0, holos: 0.85 },
  },
  curie: {
    id: "curie",
    name: "Marie Curie",
    essence: "Scientific pioneer — persistence and discovery",
    era: "1867-1934",
    weights: { nous: 0.95, anima: 0.7, holos: 0.85 },
  },
  einstein: {
    id: "einstein",
    name: "Albert Einstein",
    essence: "Thought experiments — imagination meets physics",
    era: "1879-1955",
    weights: { nous: 0.95, anima: 0.85, holos: 0.6 },
  },
  aurelius: {
    id: "aurelius",
    name: "Marcus Aurelius",
    essence: "Stoic wisdom — philosophy in action",
    era: "121-180 CE",
    weights: { nous: 0.85, anima: 0.7, holos: 0.9 },
  },
};

// ═══════════════════════════════════════════════════════════════
// ANIMATION TIMING (11 BPM = 5.45s cycle)
// ═══════════════════════════════════════════════════════════════

export const ANIMATION = {
  breathCycle: 5.45, // seconds (11 BPM)
  symbolReveal: {
    nous: 0.2,
    anima: 0.5,
    holos: 0.8,
    unified: 1.5,
  },
  lineDrawDelay: {
    nous: 1.0,
    anima: 1.1,
    holos: 1.2,
  },
  textReveal: {
    brand: 2.2,
    tagline: 2.6,
  },
} as const;
