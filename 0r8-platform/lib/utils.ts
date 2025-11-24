/**
 * 0r8 Utility Functions
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { ThreeIWeights, Pillar, ProcessingMode } from "@/types";

/**
 * Merge Tailwind classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Generate a unique ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Calculate dominant pillar from weights
 */
export function getDominantPillar(weights: ThreeIWeights): Pillar {
  if (weights.nous >= weights.anima && weights.nous >= weights.holos) {
    return "nous";
  }
  if (weights.anima >= weights.nous && weights.anima >= weights.holos) {
    return "anima";
  }
  return "holos";
}

/**
 * Calculate AI temperature from 3i weights
 * Higher ANIMA = higher temperature (more creative)
 * Higher NOUS = lower temperature (more precise)
 */
export function calculateTemperature(weights: ThreeIWeights): number {
  const base = 0.7;
  const animaBoost = (weights.anima - 0.33) * 0.5;
  const nousReduction = (weights.nous - 0.33) * 0.3;
  return Math.max(0.1, Math.min(1.0, base + animaBoost - nousReduction));
}

/**
 * Normalize weights to sum to 1
 */
export function normalizeWeights(weights: ThreeIWeights): ThreeIWeights {
  const total = weights.nous + weights.anima + weights.holos;
  if (total === 0) return { nous: 0.33, anima: 0.33, holos: 0.34 };
  return {
    nous: weights.nous / total,
    anima: weights.anima / total,
    holos: weights.holos / total,
  };
}

/**
 * Blend two weight configurations
 */
export function blendWeights(
  w1: ThreeIWeights,
  w2: ThreeIWeights,
  ratio: number = 0.5
): ThreeIWeights {
  return normalizeWeights({
    nous: w1.nous * (1 - ratio) + w2.nous * ratio,
    anima: w1.anima * (1 - ratio) + w2.anima * ratio,
    holos: w1.holos * (1 - ratio) + w2.holos * ratio,
  });
}

/**
 * Format weights as percentages
 */
export function formatWeights(weights: ThreeIWeights): string {
  return `I₁ ${Math.round(weights.nous * 100)}% / I₂ ${Math.round(weights.anima * 100)}% / I₃ ${Math.round(weights.holos * 100)}%`;
}

/**
 * Get pillar color
 */
export function getPillarColor(pillar: Pillar): string {
  const colors = {
    nous: "#00D4FF",
    anima: "#8B5CF6",
    holos: "#F59E0B",
  };
  return colors[pillar];
}

/**
 * Get pillar symbol
 */
export function getPillarSymbol(pillar: Pillar): string {
  const symbols = {
    nous: "☿",
    anima: "🜍",
    holos: "🜔",
  };
  return symbols[pillar];
}

/**
 * Calculate harmony score from levels
 */
export function calculateHarmonyScore(
  nousLevel: number,
  animaLevel: number,
  holosLevel: number
): number {
  return (nousLevel + animaLevel + holosLevel) / 3;
}

/**
 * Check if user is unified (all pillars >= 70)
 */
export function isUnified(
  nousLevel: number,
  animaLevel: number,
  holosLevel: number
): boolean {
  return nousLevel >= 70 && animaLevel >= 70 && holosLevel >= 70;
}

/**
 * Format date for display
 */
export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + "...";
}
