/**
 * Elemental Grid UI System
 * Three-zone layout based on 3i pillars
 *
 * Blue Zone (NOUS): Thinking mode, input, analysis
 * Purple Zone (ANIMA): Feeling mode, resonance, intuition
 * Gold Zone (HOLOS): Structuring mode, output, frameworks
 */

"use client";

import React, { ReactNode } from "react";
import { motion } from "framer-motion";
import { COLORS, SYMBOLS } from "@/lib/constants";
import type { Pillar } from "@/types";

interface ZoneProps {
  children: ReactNode;
  pillar: Pillar;
  title?: string;
  active?: boolean;
  className?: string;
}

const zoneConfig = {
  nous: {
    symbol: SYMBOLS.nous,
    name: "NOUS",
    subtitle: "The Mind",
    color: COLORS.nous.primary,
    glow: COLORS.nous.glow,
    dark: COLORS.nous.dark,
    gradient: "from-cyan-500/10 to-transparent",
    borderColor: "border-cyan-500/30",
    hoverBorder: "hover:border-cyan-400/50",
    description: "Thinking · Analysis · Logic",
  },
  anima: {
    symbol: SYMBOLS.anima,
    name: "ANIMA",
    subtitle: "The Soul",
    color: COLORS.anima.primary,
    glow: COLORS.anima.glow,
    dark: COLORS.anima.dark,
    gradient: "from-purple-500/10 to-transparent",
    borderColor: "border-purple-500/30",
    hoverBorder: "hover:border-purple-400/50",
    description: "Feeling · Intuition · Resonance",
  },
  holos: {
    symbol: SYMBOLS.holos,
    name: "HOLOS",
    subtitle: "The Whole",
    color: COLORS.holos.primary,
    glow: COLORS.holos.glow,
    dark: COLORS.holos.dark,
    gradient: "from-amber-500/10 to-transparent",
    borderColor: "border-amber-500/30",
    hoverBorder: "hover:border-amber-400/50",
    description: "Structuring · Output · Frameworks",
  },
};

export function ElementalZone({
  children,
  pillar,
  title,
  active = false,
  className = "",
}: ZoneProps) {
  const config = zoneConfig[pillar];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        relative rounded-2xl border backdrop-blur-sm
        bg-gradient-to-br ${config.gradient}
        ${config.borderColor} ${config.hoverBorder}
        transition-all duration-300
        ${active ? "ring-2 ring-opacity-50" : ""}
        ${className}
      `}
      style={{
        boxShadow: active ? `0 0 30px ${config.color}20` : undefined,
        borderColor: active ? config.color : undefined,
      }}
    >
      {/* Zone Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-white/5">
        <span
          className="text-2xl"
          style={{
            color: config.color,
            textShadow: `0 0 10px ${config.glow}`,
          }}
        >
          {config.symbol}
        </span>
        <div>
          <h3
            className="font-display font-semibold text-sm tracking-wider"
            style={{ color: config.color }}
          >
            {config.name}
          </h3>
          <p className="text-xs text-white/40">{title || config.description}</p>
        </div>
        {active && (
          <motion.div
            className="ml-auto w-2 h-2 rounded-full"
            style={{ backgroundColor: config.color }}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 2 }}
          />
        )}
      </div>

      {/* Zone Content */}
      <div className="p-4">{children}</div>
    </motion.div>
  );
}

interface ElementalGridProps {
  nousContent: ReactNode;
  animaContent: ReactNode;
  holosContent: ReactNode;
  activeZone?: Pillar | null;
  layout?: "horizontal" | "vertical" | "trinity";
}

export function ElementalGrid({
  nousContent,
  animaContent,
  holosContent,
  activeZone = null,
  layout = "trinity",
}: ElementalGridProps) {
  if (layout === "horizontal") {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ElementalZone pillar="nous" active={activeZone === "nous"}>
          {nousContent}
        </ElementalZone>
        <ElementalZone pillar="anima" active={activeZone === "anima"}>
          {animaContent}
        </ElementalZone>
        <ElementalZone pillar="holos" active={activeZone === "holos"}>
          {holosContent}
        </ElementalZone>
      </div>
    );
  }

  if (layout === "vertical") {
    return (
      <div className="flex flex-col gap-4">
        <ElementalZone pillar="nous" active={activeZone === "nous"}>
          {nousContent}
        </ElementalZone>
        <ElementalZone pillar="anima" active={activeZone === "anima"}>
          {animaContent}
        </ElementalZone>
        <ElementalZone pillar="holos" active={activeZone === "holos"}>
          {holosContent}
        </ElementalZone>
      </div>
    );
  }

  // Trinity layout - inverted triangle
  return (
    <div className="flex flex-col gap-4">
      {/* Top row - NOUS centered */}
      <div className="flex justify-center">
        <div className="w-full max-w-md">
          <ElementalZone pillar="nous" active={activeZone === "nous"}>
            {nousContent}
          </ElementalZone>
        </div>
      </div>

      {/* Bottom row - ANIMA and HOLOS */}
      <div className="grid grid-cols-2 gap-4">
        <ElementalZone pillar="anima" active={activeZone === "anima"}>
          {animaContent}
        </ElementalZone>
        <ElementalZone pillar="holos" active={activeZone === "holos"}>
          {holosContent}
        </ElementalZone>
      </div>
    </div>
  );
}

// Specialized zone components for specific use cases
export function NousInputZone({
  children,
  active = false,
}: {
  children: ReactNode;
  active?: boolean;
}) {
  return (
    <ElementalZone pillar="nous" title="Input · Analysis" active={active}>
      {children}
    </ElementalZone>
  );
}

export function AnimaProcessZone({
  children,
  active = false,
}: {
  children: ReactNode;
  active?: boolean;
}) {
  return (
    <ElementalZone pillar="anima" title="Processing · Resonance" active={active}>
      {children}
    </ElementalZone>
  );
}

export function HolosOutputZone({
  children,
  active = false,
}: {
  children: ReactNode;
  active?: boolean;
}) {
  return (
    <ElementalZone pillar="holos" title="Output · Structure" active={active}>
      {children}
    </ElementalZone>
  );
}
