/**
 * Transmutation Flow Component
 * Visualizes the 4-stage processing cascade:
 * INPUT → DISTILL → RECOMBINE → REVEAL
 */

"use client";

import React from "react";
import { motion } from "framer-motion";
import { COLORS, SYMBOLS } from "@/lib/constants";

type TransmutationStage = "input" | "distill" | "recombine" | "reveal";

interface StageConfig {
  name: string;
  pillar: "all" | "nous" | "anima" | "holos";
  symbol: string;
  color: string;
  description: string;
}

const stages: Record<TransmutationStage, StageConfig> = {
  input: {
    name: "INPUT",
    pillar: "all",
    symbol: "⊛",
    color: "#FFFFFF",
    description: "Raw material enters",
  },
  distill: {
    name: "DISTILL",
    pillar: "nous",
    symbol: SYMBOLS.nous,
    color: COLORS.nous.primary,
    description: "NOUS extracts structure",
  },
  recombine: {
    name: "RECOMBINE",
    pillar: "anima",
    symbol: SYMBOLS.anima,
    color: COLORS.anima.primary,
    description: "ANIMA infuses meaning",
  },
  reveal: {
    name: "REVEAL",
    pillar: "holos",
    symbol: SYMBOLS.holos,
    color: COLORS.holos.primary,
    description: "HOLOS delivers form",
  },
};

const stageOrder: TransmutationStage[] = ["input", "distill", "recombine", "reveal"];

interface TransmutationFlowProps {
  currentStage: TransmutationStage;
  completedStages?: TransmutationStage[];
  showLabels?: boolean;
  size?: "sm" | "md" | "lg";
}

export function TransmutationFlow({
  currentStage,
  completedStages = [],
  showLabels = true,
  size = "md",
}: TransmutationFlowProps) {
  const currentIndex = stageOrder.indexOf(currentStage);

  const sizeClasses = {
    sm: { icon: "text-xl", text: "text-xs", gap: "gap-2", padding: "p-2" },
    md: { icon: "text-2xl", text: "text-sm", gap: "gap-4", padding: "p-3" },
    lg: { icon: "text-3xl", text: "text-base", gap: "gap-6", padding: "p-4" },
  };

  const s = sizeClasses[size];

  return (
    <div className={`flex items-center justify-between ${s.gap}`}>
      {stageOrder.map((stage, index) => {
        const config = stages[stage];
        const isCompleted = completedStages.includes(stage);
        const isCurrent = stage === currentStage;
        const isPending = index > currentIndex && !isCompleted;

        return (
          <React.Fragment key={stage}>
            {/* Stage Node */}
            <motion.div
              className={`flex flex-col items-center ${s.gap}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              {/* Circle */}
              <motion.div
                className={`
                  relative flex items-center justify-center rounded-full
                  border-2 transition-all duration-300 ${s.padding}
                `}
                style={{
                  borderColor: isPending ? "rgba(255,255,255,0.2)" : config.color,
                  backgroundColor: isCurrent
                    ? `${config.color}20`
                    : isCompleted
                    ? `${config.color}10`
                    : "transparent",
                  boxShadow: isCurrent ? `0 0 20px ${config.color}40` : "none",
                }}
                animate={
                  isCurrent
                    ? {
                        scale: [1, 1.05, 1],
                        boxShadow: [
                          `0 0 20px ${config.color}40`,
                          `0 0 30px ${config.color}60`,
                          `0 0 20px ${config.color}40`,
                        ],
                      }
                    : {}
                }
                transition={{ repeat: Infinity, duration: 2 }}
              >
                <span
                  className={s.icon}
                  style={{
                    color: isPending ? "rgba(255,255,255,0.3)" : config.color,
                    textShadow: isPending ? "none" : `0 0 10px ${config.color}`,
                  }}
                >
                  {config.symbol}
                </span>

                {/* Completion check */}
                {isCompleted && !isCurrent && (
                  <motion.div
                    className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-green-500 flex items-center justify-center"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                  >
                    <span className="text-xs">✓</span>
                  </motion.div>
                )}
              </motion.div>

              {/* Label */}
              {showLabels && (
                <div className="text-center">
                  <p
                    className={`font-display font-semibold ${s.text}`}
                    style={{
                      color: isPending ? "rgba(255,255,255,0.4)" : config.color,
                    }}
                  >
                    {config.name}
                  </p>
                  <p className="text-white/40 text-xs">{config.description}</p>
                </div>
              )}
            </motion.div>

            {/* Connector Line */}
            {index < stageOrder.length - 1 && (
              <div className="flex-1 h-0.5 relative">
                <div className="absolute inset-0 bg-white/10" />
                <motion.div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r"
                  style={{
                    background: `linear-gradient(to right, ${config.color}, ${
                      stages[stageOrder[index + 1]].color
                    })`,
                  }}
                  initial={{ width: "0%" }}
                  animate={{
                    width: isCompleted || index < currentIndex ? "100%" : "0%",
                  }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

interface TransmutationCascadeProps {
  isProcessing?: boolean;
  progress?: number; // 0-100
}

export function TransmutationCascade({
  isProcessing = false,
  progress = 0,
}: TransmutationCascadeProps) {
  // Calculate current stage based on progress
  const getCurrentStage = (): TransmutationStage => {
    if (progress < 25) return "input";
    if (progress < 50) return "distill";
    if (progress < 75) return "recombine";
    return "reveal";
  };

  const getCompletedStages = (): TransmutationStage[] => {
    const completed: TransmutationStage[] = [];
    if (progress >= 25) completed.push("input");
    if (progress >= 50) completed.push("distill");
    if (progress >= 75) completed.push("recombine");
    if (progress >= 100) completed.push("reveal");
    return completed;
  };

  return (
    <div className="space-y-4">
      <TransmutationFlow
        currentStage={getCurrentStage()}
        completedStages={getCompletedStages()}
      />

      {/* Progress bar */}
      {isProcessing && (
        <div className="relative h-1 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{
              background: `linear-gradient(to right, ${COLORS.nous.primary}, ${COLORS.anima.primary}, ${COLORS.holos.primary})`,
            }}
            initial={{ width: "0%" }}
            animate={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Axiom */}
      <p className="text-center text-xs text-white/30 font-mono">
        0r8 = Transmutation Engine
      </p>
    </div>
  );
}
