/**
 * 9-Stage Convergence Animation
 * The Meta-Animation showing the birth of 0r8
 *
 * Stages:
 * 1. Void → single white dot
 * 2. Dot pulses → becomes seed ⊛
 * 3. Seed splits → three points emerge (☿, 🜍, 🜔)
 * 4. Points drift apart → forming triangle
 * 5. Colors ignite → Cyan / Purple / Amber
 * 6. Triangle rotates → 11 BPM breathing pulse
 * 7. Lines connect → trinity forms
 * 8. Center illuminates → ☉ Gold-white sun
 * 9. Zoom out → 0r8 brand emerges below
 */

"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence, useAnimation } from "framer-motion";
import { COLORS, SYMBOLS, ANIMATION } from "@/lib/constants";

type ConvergenceStage = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;

const stageDescriptions: Record<ConvergenceStage, string> = {
  1: "Void awakens",
  2: "Seed of potential",
  3: "The three emerge",
  4: "Triangle forms",
  5: "Colors ignite",
  6: "Breath begins",
  7: "Trinity connects",
  8: "Sun illuminates",
  9: "0r8 revealed",
};

interface ConvergenceAnimationProps {
  autoPlay?: boolean;
  stageDuration?: number; // ms per stage
  showControls?: boolean;
  onComplete?: () => void;
  size?: "sm" | "md" | "lg" | "full";
}

export function ConvergenceAnimation({
  autoPlay = true,
  stageDuration = 2000,
  showControls = false,
  onComplete,
  size = "md",
}: ConvergenceAnimationProps) {
  const [stage, setStage] = useState<ConvergenceStage>(1);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const controls = useAnimation();

  // Size configurations
  const sizeConfig = {
    sm: { width: 200, height: 200 },
    md: { width: 320, height: 320 },
    lg: { width: 480, height: 480 },
    full: { width: 640, height: 640 },
  };
  const { width, height } = sizeConfig[size];
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.3;

  // Triangle vertices
  const getTrianglePoints = (r: number, rotation: number = 0) => ({
    nous: {
      x: centerX + r * Math.sin(rotation),
      y: centerY - r * Math.cos(rotation),
    },
    anima: {
      x: centerX + r * Math.sin(rotation + (2 * Math.PI) / 3),
      y: centerY - r * Math.cos(rotation + (2 * Math.PI) / 3),
    },
    holos: {
      x: centerX + r * Math.sin(rotation + (4 * Math.PI) / 3),
      y: centerY - r * Math.cos(rotation + (4 * Math.PI) / 3),
    },
  });

  // Auto-advance stages
  useEffect(() => {
    if (!isPlaying) return;

    const timer = setTimeout(() => {
      if (stage < 9) {
        setStage((s) => (s + 1) as ConvergenceStage);
      } else {
        setIsPlaying(false);
        onComplete?.();
      }
    }, stageDuration);

    return () => clearTimeout(timer);
  }, [stage, isPlaying, stageDuration, onComplete]);

  // Canvas animation for particle effects
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      color: string;
      alpha: number;
    }> = [];

    // Create particles based on stage
    const createParticles = () => {
      particles.length = 0;

      if (stage >= 3) {
        const points = getTrianglePoints(radius);
        const colors = [
          COLORS.nous.primary,
          COLORS.anima.primary,
          COLORS.holos.primary,
        ];
        const positions = [points.nous, points.anima, points.holos];

        positions.forEach((pos, i) => {
          for (let j = 0; j < 10; j++) {
            particles.push({
              x: pos.x + (Math.random() - 0.5) * 20,
              y: pos.y + (Math.random() - 0.5) * 20,
              vx: (Math.random() - 0.5) * 0.5,
              vy: (Math.random() - 0.5) * 0.5,
              size: Math.random() * 2 + 1,
              color: colors[i],
              alpha: stage >= 5 ? Math.random() * 0.5 + 0.3 : 0,
            });
          }
        });
      }
    };

    createParticles();

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        // Contain particles
        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color
          .replace(")", `, ${p.alpha})`)
          .replace("rgb", "rgba");
        ctx.fill();
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [stage, width, height, radius]);

  const trianglePoints = getTrianglePoints(stage >= 4 ? radius : 0);

  return (
    <div className="relative flex flex-col items-center">
      {/* Main animation container */}
      <div
        className="relative"
        style={{ width, height }}
      >
        {/* Particle canvas */}
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          className="absolute inset-0 pointer-events-none"
        />

        {/* Stage 1: White dot */}
        <AnimatePresence>
          {stage >= 1 && (
            <motion.div
              className="absolute"
              style={{ left: centerX, top: centerY }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{
                scale: stage === 1 ? [0, 1, 0.8, 1] : stage === 2 ? 1.5 : 0,
                opacity: stage <= 2 ? 1 : 0,
              }}
              transition={{ duration: 0.5 }}
            >
              <div
                className="w-4 h-4 rounded-full -translate-x-1/2 -translate-y-1/2"
                style={{
                  backgroundColor: "#FFFFFF",
                  boxShadow: "0 0 20px #FFFFFF, 0 0 40px #FFFFFF50",
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stage 2: Seed symbol */}
        <AnimatePresence>
          {stage === 2 && (
            <motion.div
              className="absolute font-mono text-2xl text-white"
              style={{ left: centerX, top: centerY }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 2, opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              <span className="-translate-x-1/2 -translate-y-1/2 block">
                {SYMBOLS.seed}
              </span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stage 3+: Three symbols */}
        {stage >= 3 && (
          <>
            {/* NOUS - Mercury */}
            <motion.div
              className="absolute text-3xl"
              initial={{ x: centerX, y: centerY, opacity: 0 }}
              animate={{
                x: trianglePoints.nous.x,
                y: trianglePoints.nous.y,
                opacity: 1,
                scale: stage >= 6 ? [1, 1.1, 1] : 1,
              }}
              transition={{
                duration: stage === 3 ? 1 : 0.5,
                scale: {
                  repeat: stage >= 6 ? Infinity : 0,
                  duration: ANIMATION.breathCycle,
                },
              }}
              style={{
                color: stage >= 5 ? COLORS.nous.primary : "#FFFFFF",
                textShadow:
                  stage >= 5
                    ? `0 0 20px ${COLORS.nous.primary}, 0 0 40px ${COLORS.nous.primary}50`
                    : "none",
              }}
            >
              <span className="-translate-x-1/2 -translate-y-1/2 block">
                {SYMBOLS.nous}
              </span>
            </motion.div>

            {/* ANIMA - Sulfur */}
            <motion.div
              className="absolute text-3xl"
              initial={{ x: centerX, y: centerY, opacity: 0 }}
              animate={{
                x: trianglePoints.anima.x,
                y: trianglePoints.anima.y,
                opacity: 1,
                scale: stage >= 6 ? [1, 1.1, 1] : 1,
              }}
              transition={{
                duration: stage === 3 ? 1 : 0.5,
                delay: stage === 3 ? 0.2 : 0,
                scale: {
                  repeat: stage >= 6 ? Infinity : 0,
                  duration: ANIMATION.breathCycle,
                  delay: 0.5,
                },
              }}
              style={{
                color: stage >= 5 ? COLORS.anima.primary : "#FFFFFF",
                textShadow:
                  stage >= 5
                    ? `0 0 20px ${COLORS.anima.primary}, 0 0 40px ${COLORS.anima.primary}50`
                    : "none",
              }}
            >
              <span className="-translate-x-1/2 -translate-y-1/2 block">
                {SYMBOLS.anima}
              </span>
            </motion.div>

            {/* HOLOS - Salt */}
            <motion.div
              className="absolute text-3xl"
              initial={{ x: centerX, y: centerY, opacity: 0 }}
              animate={{
                x: trianglePoints.holos.x,
                y: trianglePoints.holos.y,
                opacity: 1,
                scale: stage >= 6 ? [1, 1.1, 1] : 1,
              }}
              transition={{
                duration: stage === 3 ? 1 : 0.5,
                delay: stage === 3 ? 0.4 : 0,
                scale: {
                  repeat: stage >= 6 ? Infinity : 0,
                  duration: ANIMATION.breathCycle,
                  delay: 1,
                },
              }}
              style={{
                color: stage >= 5 ? COLORS.holos.primary : "#FFFFFF",
                textShadow:
                  stage >= 5
                    ? `0 0 20px ${COLORS.holos.primary}, 0 0 40px ${COLORS.holos.primary}50`
                    : "none",
              }}
            >
              <span className="-translate-x-1/2 -translate-y-1/2 block">
                {SYMBOLS.holos}
              </span>
            </motion.div>
          </>
        )}

        {/* Stage 7+: Connection lines */}
        {stage >= 7 && (
          <svg
            className="absolute inset-0 pointer-events-none"
            width={width}
            height={height}
          >
            {/* NOUS to ANIMA */}
            <motion.line
              x1={trianglePoints.nous.x}
              y1={trianglePoints.nous.y}
              x2={trianglePoints.anima.x}
              y2={trianglePoints.anima.y}
              stroke={COLORS.nous.primary}
              strokeWidth="1"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.6 }}
              transition={{ duration: 0.5 }}
              style={{ filter: `drop-shadow(0 0 4px ${COLORS.nous.primary})` }}
            />
            {/* ANIMA to HOLOS */}
            <motion.line
              x1={trianglePoints.anima.x}
              y1={trianglePoints.anima.y}
              x2={trianglePoints.holos.x}
              y2={trianglePoints.holos.y}
              stroke={COLORS.anima.primary}
              strokeWidth="1"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.6 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              style={{ filter: `drop-shadow(0 0 4px ${COLORS.anima.primary})` }}
            />
            {/* HOLOS to NOUS */}
            <motion.line
              x1={trianglePoints.holos.x}
              y1={trianglePoints.holos.y}
              x2={trianglePoints.nous.x}
              y2={trianglePoints.nous.y}
              stroke={COLORS.holos.primary}
              strokeWidth="1"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.6 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              style={{ filter: `drop-shadow(0 0 4px ${COLORS.holos.primary})` }}
            />
          </svg>
        )}

        {/* Stage 8+: Center sun */}
        {stage >= 8 && (
          <motion.div
            className="absolute text-4xl"
            style={{ left: centerX, top: centerY }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{
              scale: [0, 1.2, 1],
              opacity: 1,
            }}
            transition={{ duration: 0.8 }}
          >
            <span
              className="-translate-x-1/2 -translate-y-1/2 block"
              style={{
                color: COLORS.orb.primary,
                textShadow: `
                  0 0 20px ${COLORS.orb.primary},
                  0 0 40px ${COLORS.holos.primary},
                  0 0 60px ${COLORS.anima.primary},
                  0 0 80px ${COLORS.nous.primary}
                `,
              }}
            >
              {SYMBOLS.unified}
            </span>
          </motion.div>
        )}

        {/* Stage 9: Brand name */}
        {stage >= 9 && (
          <motion.div
            className="absolute bottom-4 left-0 right-0 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1
              className="font-display text-4xl font-bold tracking-wider"
              style={{
                background: `linear-gradient(135deg, ${COLORS.nous.primary}, ${COLORS.anima.primary}, ${COLORS.holos.primary})`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              0r8
            </h1>
            <p className="text-white/50 text-sm mt-1">The Awakening</p>
          </motion.div>
        )}
      </div>

      {/* Stage indicator */}
      <div className="mt-4 flex items-center gap-2">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((s) => (
          <motion.div
            key={s}
            className="w-2 h-2 rounded-full"
            style={{
              backgroundColor:
                s <= stage
                  ? s <= 3
                    ? COLORS.nous.primary
                    : s <= 6
                    ? COLORS.anima.primary
                    : COLORS.holos.primary
                  : "rgba(255,255,255,0.2)",
            }}
            animate={s === stage ? { scale: [1, 1.3, 1] } : {}}
            transition={{ repeat: Infinity, duration: 1 }}
          />
        ))}
      </div>

      {/* Stage description */}
      <motion.p
        className="mt-2 text-sm text-white/50"
        key={stage}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {stageDescriptions[stage]}
      </motion.p>

      {/* Controls */}
      {showControls && (
        <div className="mt-4 flex gap-2">
          <button
            className="px-3 py-1 text-sm bg-white/10 rounded hover:bg-white/20 transition"
            onClick={() => setStage(1)}
          >
            Reset
          </button>
          <button
            className="px-3 py-1 text-sm bg-white/10 rounded hover:bg-white/20 transition"
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? "Pause" : "Play"}
          </button>
          <button
            className="px-3 py-1 text-sm bg-white/10 rounded hover:bg-white/20 transition disabled:opacity-50"
            onClick={() => stage < 9 && setStage((s) => (s + 1) as ConvergenceStage)}
            disabled={stage >= 9}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

// Export a simpler version for logo use
export function ConvergenceLogo({ size = 64 }: { size?: number }) {
  const r = size * 0.35;
  const cx = size / 2;
  const cy = size / 2;

  const points = {
    nous: { x: cx, y: cy - r },
    anima: { x: cx - r * 0.866, y: cy + r * 0.5 },
    holos: { x: cx + r * 0.866, y: cy + r * 0.5 },
  };

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* Triangle lines */}
      <path
        d={`M ${points.nous.x} ${points.nous.y} L ${points.anima.x} ${points.anima.y} L ${points.holos.x} ${points.holos.y} Z`}
        fill="none"
        stroke="url(#gradient)"
        strokeWidth="1"
        opacity="0.6"
      />

      {/* Center sun */}
      <circle
        cx={cx}
        cy={cy}
        r={size * 0.1}
        fill={COLORS.orb.primary}
        filter="url(#glow)"
      />

      {/* Gradient definition */}
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={COLORS.nous.primary} />
          <stop offset="50%" stopColor={COLORS.anima.primary} />
          <stop offset="100%" stopColor={COLORS.holos.primary} />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
    </svg>
  );
}
