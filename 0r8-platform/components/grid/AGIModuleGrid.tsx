/**
 * AGI Module Grid Component
 * Displays the 9 AGI modules organized by pillar
 */

"use client";

import React from "react";
import { motion } from "framer-motion";
import { COLORS, SYMBOLS } from "@/lib/constants";
import type { Pillar } from "@/types";

interface AGIModule {
  name: string;
  module: string;
  pillar: Pillar;
  description: string;
  capabilities: string[];
  activationLevel?: number;
}

// The 9 AGI Modules
const AGI_MODULES: Record<Pillar, AGIModule[]> = {
  nous: [
    {
      name: "Pattern Engine",
      module: "pattern_engine",
      pillar: "nous",
      description: "Detects structure, patterns, and hidden order",
      capabilities: ["Structural analysis", "Pattern recognition", "Anomaly detection"],
    },
    {
      name: "Inference Engine",
      module: "inference_engine",
      pillar: "nous",
      description: "Builds logical chains and deductive reasoning",
      capabilities: ["Logical deduction", "Causal reasoning", "Hypothesis generation"],
    },
    {
      name: "Compression Engine",
      module: "compression_engine",
      pillar: "nous",
      description: "Distills complexity to essential meaning",
      capabilities: ["Summarization", "Key insight extraction", "Noise filtering"],
    },
  ],
  anima: [
    {
      name: "Resonance Layer",
      module: "resonance_layer",
      pillar: "anima",
      description: "Recognizes emotional and aesthetic truth",
      capabilities: ["Emotional intelligence", "Aesthetic judgment", "Truth resonance"],
    },
    {
      name: "Perception Layer",
      module: "perception_layer",
      pillar: "anima",
      description: "Reads between lines, understands subtext",
      capabilities: ["Subtext analysis", "Implicit meaning", "Nuance detection"],
    },
    {
      name: "Adaptive Persona",
      module: "adaptive_persona",
      pillar: "anima",
      description: "Context-sensitive voice and personality",
      capabilities: ["Tone matching", "Voice adaptation", "Rapport building"],
    },
  ],
  holos: [
    {
      name: "Geometry Engine",
      module: "geometry_engine",
      pillar: "holos",
      description: "Organizes into actionable frameworks",
      capabilities: ["Structure creation", "Framework design", "Hierarchy building"],
    },
    {
      name: "Memory Web",
      module: "memory_web",
      pillar: "holos",
      description: "Connects information across time and context",
      capabilities: ["Context persistence", "Temporal linking", "Knowledge graph"],
    },
    {
      name: "Framework Forge",
      module: "framework_forge",
      pillar: "holos",
      description: "Outputs systems, templates, and action plans",
      capabilities: ["System design", "Template generation", "Action plans"],
    },
  ],
};

const pillarConfig: Record<Pillar, { symbol: string; color: string; name: string }> = {
  nous: { symbol: SYMBOLS.nous, color: COLORS.nous.primary, name: "NOUS" },
  anima: { symbol: SYMBOLS.anima, color: COLORS.anima.primary, name: "ANIMA" },
  holos: { symbol: SYMBOLS.holos, color: COLORS.holos.primary, name: "HOLOS" },
};

interface ModuleCardProps {
  module: AGIModule;
  activationLevel?: number;
  onClick?: () => void;
}

export function ModuleCard({ module, activationLevel = 0, onClick }: ModuleCardProps) {
  const config = pillarConfig[module.pillar];
  const isActive = activationLevel > 0;

  return (
    <motion.div
      className={`
        relative p-4 rounded-xl border cursor-pointer
        transition-all duration-300
        ${isActive ? "border-opacity-60" : "border-opacity-20"}
      `}
      style={{
        borderColor: config.color,
        backgroundColor: isActive ? `${config.color}10` : "transparent",
        boxShadow: isActive ? `0 0 20px ${config.color}20` : "none",
      }}
      whileHover={{ scale: 1.02, y: -2 }}
      onClick={onClick}
    >
      {/* Activation indicator */}
      {isActive && (
        <motion.div
          className="absolute top-2 right-2 w-2 h-2 rounded-full"
          style={{ backgroundColor: config.color }}
          animate={{ scale: [1, 1.3, 1], opacity: [1, 0.6, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        />
      )}

      {/* Module name */}
      <h4
        className="font-display font-semibold text-sm mb-1"
        style={{ color: config.color }}
      >
        {module.name}
      </h4>

      {/* Description */}
      <p className="text-xs text-white/50 mb-3">{module.description}</p>

      {/* Capabilities */}
      <div className="flex flex-wrap gap-1">
        {module.capabilities.slice(0, 2).map((cap, i) => (
          <span
            key={i}
            className="text-xs px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: `${config.color}15`,
              color: `${config.color}CC`,
            }}
          >
            {cap}
          </span>
        ))}
      </div>

      {/* Activation bar */}
      {isActive && (
        <div className="mt-3 h-1 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: config.color }}
            initial={{ width: 0 }}
            animate={{ width: `${activationLevel * 100}%` }}
          />
        </div>
      )}
    </motion.div>
  );
}

interface AGIModuleGridProps {
  activeModules?: Record<Pillar, string[]>;
  activationLevels?: Record<string, number>;
  layout?: "grid" | "list" | "compact";
  onModuleClick?: (module: AGIModule) => void;
}

export function AGIModuleGrid({
  activeModules,
  activationLevels = {},
  layout = "grid",
  onModuleClick,
}: AGIModuleGridProps) {
  const pillars: Pillar[] = ["nous", "anima", "holos"];

  if (layout === "compact") {
    return (
      <div className="flex gap-2 justify-center">
        {pillars.map((pillar) => {
          const config = pillarConfig[pillar];
          const modules = AGI_MODULES[pillar];
          const activeCount = activeModules?.[pillar]?.length || 0;

          return (
            <div
              key={pillar}
              className="flex items-center gap-1 px-3 py-1 rounded-full border"
              style={{
                borderColor: `${config.color}40`,
                backgroundColor: activeCount > 0 ? `${config.color}10` : "transparent",
              }}
            >
              <span style={{ color: config.color }}>{config.symbol}</span>
              <span className="text-xs text-white/50">
                {activeCount}/{modules.length}
              </span>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {pillars.map((pillar) => {
        const config = pillarConfig[pillar];
        const modules = AGI_MODULES[pillar];

        return (
          <div key={pillar}>
            {/* Pillar header */}
            <div className="flex items-center gap-2 mb-3">
              <span
                className="text-xl"
                style={{
                  color: config.color,
                  textShadow: `0 0 10px ${config.color}`,
                }}
              >
                {config.symbol}
              </span>
              <h3
                className="font-display font-semibold text-sm tracking-wider"
                style={{ color: config.color }}
              >
                {config.name} ENGINES
              </h3>
              <div className="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent" />
            </div>

            {/* Modules */}
            <div
              className={
                layout === "grid"
                  ? "grid grid-cols-1 md:grid-cols-3 gap-3"
                  : "space-y-2"
              }
            >
              {modules.map((module) => (
                <ModuleCard
                  key={module.module}
                  module={module}
                  activationLevel={activationLevels[module.module]}
                  onClick={() => onModuleClick?.(module)}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Export modules data for use elsewhere
export { AGI_MODULES };
