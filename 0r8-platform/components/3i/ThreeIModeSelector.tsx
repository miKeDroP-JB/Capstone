"use client";

/**
 * 3i Mode Selector Component
 * Allows users to adjust the balance between NOUS, ANIMA, and HOLOS
 */

import { useState } from "react";
import { use3iStore } from "@/lib/stores/use-3i-store";
import { cn, formatWeights, getPillarColor, getPillarSymbol } from "@/lib/utils";
import { MODE_WEIGHTS, SYMBOLS } from "@/lib/constants";
import type { ProcessingMode, Pillar } from "@/types";

const MODES: { id: ProcessingMode; name: string; description: string }[] = [
  { id: "analyst", name: "Analyst", description: "Pure logic, research, data" },
  { id: "creator", name: "Creator", description: "Wild creativity, brainstorming" },
  { id: "executor", name: "Executor", description: "Action-oriented, getting things done" },
  { id: "sage", name: "Sage", description: "Balanced wisdom, advice" },
  { id: "transcendent", name: "Transcendent", description: "Full power, reality bends" },
];

interface PillarSliderProps {
  pillar: Pillar;
  value: number;
  onChange: (value: number) => void;
}

function PillarSlider({ pillar, value, onChange }: PillarSliderProps) {
  const symbol = getPillarSymbol(pillar);
  const color = getPillarColor(pillar);
  const labels = {
    nous: { name: "NOUS", subtitle: "Intelligence" },
    anima: { name: "ANIMA", subtitle: "Intuition" },
    holos: { name: "HOLOS", subtitle: "Integration" },
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className="text-2xl"
            style={{ color, textShadow: `0 0 10px ${color}` }}
          >
            {symbol}
          </span>
          <div>
            <div className="font-medium text-sm" style={{ color }}>
              {labels[pillar].name}
            </div>
            <div className="text-xs text-white/40">{labels[pillar].subtitle}</div>
          </div>
        </div>
        <span className="text-sm font-mono" style={{ color }}>
          {Math.round(value * 100)}%
        </span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        value={value * 100}
        onChange={(e) => onChange(Number(e.target.value) / 100)}
        className="w-full h-2 rounded-full appearance-none cursor-pointer"
        style={{
          background: `linear-gradient(to right, ${color} ${value * 100}%, rgba(255,255,255,0.1) ${value * 100}%)`,
        }}
      />
    </div>
  );
}

export function ThreeIModeSelector() {
  const { mode, weights, setMode, setWeights } = use3iStore();
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-subtle rounded-xl border border-white/5 overflow-hidden">
      {/* Mode Buttons */}
      <div className="p-4 border-b border-white/5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-white/70">Processing Mode</h3>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-white/40 hover:text-white/70 transition-colors"
          >
            {isExpanded ? "Simple" : "Advanced"}
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          {MODES.map((m) => (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-sm font-medium transition-all",
                mode === m.id
                  ? "bg-gradient-to-r from-nous-primary/20 via-anima-primary/20 to-holos-primary/20 text-white border border-white/20"
                  : "bg-white/5 text-white/50 hover:text-white/80 hover:bg-white/10"
              )}
              title={m.description}
            >
              {m.name}
            </button>
          ))}
        </div>
      </div>

      {/* Weight Display / Sliders */}
      <div className="p-4">
        {isExpanded ? (
          <div className="space-y-4">
            <PillarSlider
              pillar="nous"
              value={weights.nous}
              onChange={(v) => setWeights({ nous: v })}
            />
            <PillarSlider
              pillar="anima"
              value={weights.anima}
              onChange={(v) => setWeights({ anima: v })}
            />
            <PillarSlider
              pillar="holos"
              value={weights.holos}
              onChange={(v) => setWeights({ holos: v })}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center gap-6">
            {/* NOUS */}
            <div className="text-center">
              <span
                className="text-2xl block"
                style={{
                  color: getPillarColor("nous"),
                  textShadow: `0 0 10px ${getPillarColor("nous")}`,
                }}
              >
                {SYMBOLS.nous}
              </span>
              <span className="text-xs text-white/40">
                {Math.round(weights.nous * 100)}%
              </span>
            </div>

            {/* ANIMA */}
            <div className="text-center">
              <span
                className="text-2xl block"
                style={{
                  color: getPillarColor("anima"),
                  textShadow: `0 0 10px ${getPillarColor("anima")}`,
                }}
              >
                {SYMBOLS.anima}
              </span>
              <span className="text-xs text-white/40">
                {Math.round(weights.anima * 100)}%
              </span>
            </div>

            {/* HOLOS */}
            <div className="text-center">
              <span
                className="text-2xl block"
                style={{
                  color: getPillarColor("holos"),
                  textShadow: `0 0 10px ${getPillarColor("holos")}`,
                }}
              >
                {SYMBOLS.holos}
              </span>
              <span className="text-xs text-white/40">
                {Math.round(weights.holos * 100)}%
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
