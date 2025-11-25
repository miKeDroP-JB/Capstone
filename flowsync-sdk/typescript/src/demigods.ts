/**
 * FlowSync Demigod Selector — Intelligent Demigod selection utilities
 */

import type { Pillar, ProcessingMode, DemigodId, ThreeIWeights } from './types';

interface DemigodInfo {
  name: string;
  pillar: Pillar;
  symbol: string;
  domain: string;
  specialty: string;
  keywords: string[];
  defaultWeights: ThreeIWeights;
}

/**
 * The 7 Demigods with their attributes
 */
export const DEMIGODS: Record<DemigodId, DemigodInfo> = {
  // NOUS Pillar (☿ Mercury — Intelligence)
  athena: {
    name: 'Athena',
    pillar: 'nous',
    symbol: '🦉',
    domain: 'Strategy & Wisdom',
    specialty: 'Business planning, strategy, analysis, complex problem-solving',
    keywords: ['strategy', 'plan', 'analyze', 'business', 'wisdom', 'complex'],
    defaultWeights: { nous: 0.85, anima: 0.40, holos: 0.70 },
  },
  mercury: {
    name: 'Mercury',
    pillar: 'nous',
    symbol: '⚡',
    domain: 'Speed & Communication',
    specialty: 'Quick tasks, messaging, efficiency, rapid iteration',
    keywords: ['quick', 'fast', 'message', 'communicate', 'efficient', 'rapid'],
    defaultWeights: { nous: 0.80, anima: 0.50, holos: 0.75 },
  },
  hephaestus: {
    name: 'Hephaestus',
    pillar: 'nous',
    symbol: '🔨',
    domain: 'Building & Craft',
    specialty: 'Technical work, coding, engineering, systems design',
    keywords: ['code', 'build', 'engineer', 'technical', 'craft', 'system'],
    defaultWeights: { nous: 0.90, anima: 0.35, holos: 0.80 },
  },

  // ANIMA Pillar (🜍 Sulfur — Intuition)
  apollo: {
    name: 'Apollo',
    pillar: 'anima',
    symbol: '☀️',
    domain: 'Vision & Light',
    specialty: 'Creative direction, prophecy, arts, music, inspiration',
    keywords: ['create', 'art', 'design', 'music', 'inspire', 'vision', 'creative'],
    defaultWeights: { nous: 0.50, anima: 0.90, holos: 0.60 },
  },
  artemis: {
    name: 'Artemis',
    pillar: 'anima',
    symbol: '🏹',
    domain: 'Precision & Wild',
    specialty: 'Focus, targeting, independent work, nature, instinct',
    keywords: ['focus', 'target', 'hunt', 'precise', 'independent', 'instinct'],
    defaultWeights: { nous: 0.60, anima: 0.85, holos: 0.55 },
  },

  // HOLOS Pillar (🜔 Salt — Integration)
  hermes: {
    name: 'Hermes',
    pillar: 'holos',
    symbol: '🪽',
    domain: 'Execution & Speed',
    specialty: 'Getting things done, delivery, bridging gaps, travel',
    keywords: ['execute', 'ship', 'deliver', 'done', 'bridge', 'move'],
    defaultWeights: { nous: 0.65, anima: 0.55, holos: 0.90 },
  },
  ares: {
    name: 'Ares',
    pillar: 'holos',
    symbol: '⚔️',
    domain: 'Action & Courage',
    specialty: 'Bold moves, competition, breakthroughs, challenges',
    keywords: ['challenge', 'compete', 'bold', 'fight', 'breakthrough', 'action'],
    defaultWeights: { nous: 0.55, anima: 0.60, holos: 0.95 },
  },
};

/**
 * Intelligent Demigod selection based on message content and context.
 */
export class DemigodSelector {
  /**
   * Select the best Demigod for a given message.
   */
  select(
    message: string,
    options?: {
      preferredPillar?: Pillar;
      weights?: Partial<ThreeIWeights>;
    }
  ): [DemigodId, DemigodInfo] {
    const messageLower = message.toLowerCase();
    const scores: Record<DemigodId, number> = {} as any;

    for (const [id, info] of Object.entries(DEMIGODS) as [DemigodId, DemigodInfo][]) {
      let score = 0;

      // Keyword matching
      for (const keyword of info.keywords) {
        if (messageLower.includes(keyword)) {
          score += 2;
        }
      }

      // Pillar preference
      if (options?.preferredPillar && info.pillar === options.preferredPillar) {
        score += 3;
      }

      // Weight alignment
      if (options?.weights) {
        const dw = info.defaultWeights;
        const alignment =
          1 -
          (Math.abs((options.weights.nous || 0.33) - dw.nous) +
            Math.abs((options.weights.anima || 0.33) - dw.anima) +
            Math.abs((options.weights.holos || 0.34) - dw.holos)) /
            3;
        score += alignment * 2;
      }

      scores[id] = score;
    }

    // Select highest scoring
    const bestId = (Object.entries(scores) as [DemigodId, number][]).reduce(
      (a, b) => (b[1] > a[1] ? b : a)
    )[0];

    return [bestId, DEMIGODS[bestId]];
  }

  /**
   * Select best Demigod for a processing mode
   */
  selectForMode(mode: ProcessingMode): [DemigodId, DemigodInfo] {
    const modeDemigods: Record<ProcessingMode, DemigodId> = {
      analyst: 'athena',
      creator: 'apollo',
      executor: 'hermes',
      sage: 'athena',
      transcendent: 'hermes',
    };
    const id = modeDemigods[mode];
    return [id, DEMIGODS[id]];
  }

  /**
   * Select best Demigod for a task type
   */
  selectForTask(taskType: string): [DemigodId, DemigodInfo] {
    const taskMapping: Record<string, DemigodId> = {
      analyze: 'athena',
      research: 'athena',
      strategy: 'athena',
      plan: 'athena',
      code: 'hephaestus',
      build: 'hephaestus',
      engineer: 'hephaestus',
      debug: 'hephaestus',
      create: 'apollo',
      design: 'apollo',
      art: 'apollo',
      write: 'apollo',
      focus: 'artemis',
      target: 'artemis',
      hunt: 'artemis',
      execute: 'hermes',
      ship: 'hermes',
      deliver: 'hermes',
      challenge: 'ares',
      compete: 'ares',
      fight: 'ares',
      quick: 'mercury',
      fast: 'mercury',
      message: 'mercury',
    };

    const id = taskMapping[taskType.toLowerCase()] || 'athena';
    return [id, DEMIGODS[id]];
  }

  /**
   * Get all Demigods for a pillar
   */
  getByPillar(pillar: Pillar): [DemigodId, DemigodInfo][] {
    return (Object.entries(DEMIGODS) as [DemigodId, DemigodInfo][]).filter(
      ([, info]) => info.pillar === pillar
    );
  }

  /**
   * List all Demigods
   */
  listAll(): Record<DemigodId, DemigodInfo> {
    return DEMIGODS;
  }
}
