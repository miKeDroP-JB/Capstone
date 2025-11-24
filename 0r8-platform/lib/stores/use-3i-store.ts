/**
 * 0r8 3i State Management
 * Zustand store for 3i configuration
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  ThreeIWeights,
  ProcessingMode,
  DomainId,
  DemigodId,
  Pillar,
  UserHarmony,
} from "@/types";
import { MODE_WEIGHTS, DOMAINS, DEMIGODS } from "@/lib/constants";

interface ThreeIState {
  // Current configuration
  mode: ProcessingMode;
  weights: ThreeIWeights;
  domain: DomainId | null;
  demigod: DemigodId | null;
  historicalFlavor: string | null;

  // User harmony (persisted)
  harmony: UserHarmony | null;

  // Derived
  dominantPillar: Pillar;

  // Actions
  setMode: (mode: ProcessingMode) => void;
  setWeights: (weights: Partial<ThreeIWeights>) => void;
  setDomain: (domain: DomainId | null) => void;
  setDemigod: (demigod: DemigodId | null) => void;
  setHistoricalFlavor: (flavor: string | null) => void;
  setHarmony: (harmony: UserHarmony) => void;
  reset: () => void;
}

function getDominantPillar(weights: ThreeIWeights): Pillar {
  if (weights.nous >= weights.anima && weights.nous >= weights.holos) {
    return "nous";
  }
  if (weights.anima >= weights.nous && weights.anima >= weights.holos) {
    return "anima";
  }
  return "holos";
}

function normalizeWeights(weights: ThreeIWeights): ThreeIWeights {
  const total = weights.nous + weights.anima + weights.holos;
  if (total === 0) return { nous: 0.33, anima: 0.33, holos: 0.34 };
  return {
    nous: weights.nous / total,
    anima: weights.anima / total,
    holos: weights.holos / total,
  };
}

const initialWeights: ThreeIWeights = { nous: 0.33, anima: 0.33, holos: 0.34 };

export const use3iStore = create<ThreeIState>()(
  persist(
    (set, get) => ({
      // Initial state
      mode: "sage",
      weights: initialWeights,
      domain: null,
      demigod: null,
      historicalFlavor: null,
      harmony: null,
      dominantPillar: "holos",

      // Actions
      setMode: (mode) => {
        const newWeights = MODE_WEIGHTS[mode];
        set({
          mode,
          weights: newWeights,
          dominantPillar: getDominantPillar(newWeights),
        });
      },

      setWeights: (partialWeights) => {
        const currentWeights = get().weights;
        const newWeights = normalizeWeights({
          ...currentWeights,
          ...partialWeights,
        });
        set({
          weights: newWeights,
          dominantPillar: getDominantPillar(newWeights),
        });
      },

      setDomain: (domain) => {
        if (domain && DOMAINS[domain]) {
          const domainWeights = DOMAINS[domain].defaultWeights;
          const currentWeights = get().weights;
          // Blend domain defaults with current weights
          const blendedWeights = normalizeWeights({
            nous: (currentWeights.nous + domainWeights.nous) / 2,
            anima: (currentWeights.anima + domainWeights.anima) / 2,
            holos: (currentWeights.holos + domainWeights.holos) / 2,
          });
          set({
            domain,
            weights: blendedWeights,
            dominantPillar: getDominantPillar(blendedWeights),
          });
        } else {
          set({ domain: null });
        }
      },

      setDemigod: (demigod) => {
        if (demigod && DEMIGODS[demigod]) {
          set({ demigod });
        } else {
          set({ demigod: null });
        }
      },

      setHistoricalFlavor: (flavor) => {
        set({ historicalFlavor: flavor });
      },

      setHarmony: (harmony) => {
        set({ harmony });
      },

      reset: () => {
        set({
          mode: "sage",
          weights: initialWeights,
          domain: null,
          demigod: null,
          historicalFlavor: null,
          dominantPillar: "holos",
        });
      },
    }),
    {
      name: "0r8-3i-store",
      partialize: (state) => ({
        mode: state.mode,
        domain: state.domain,
        harmony: state.harmony,
      }),
    }
  )
);
