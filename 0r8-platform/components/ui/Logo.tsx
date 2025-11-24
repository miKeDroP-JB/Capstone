"use client";

/**
 * 0r8 Logo Component
 * Multiple variants: icon, text, full, animated
 */

import { cn } from "@/lib/utils";
import { SYMBOLS, COLORS } from "@/lib/constants";

interface LogoProps {
  variant?: "icon" | "text" | "full" | "trinity";
  size?: "sm" | "md" | "lg" | "xl";
  animated?: boolean;
  className?: string;
}

export function Logo({
  variant = "full",
  size = "md",
  animated = false,
  className,
}: LogoProps) {
  const sizes = {
    sm: { icon: "text-2xl", text: "text-xl", trinity: "w-16 h-16" },
    md: { icon: "text-4xl", text: "text-3xl", trinity: "w-24 h-24" },
    lg: { icon: "text-6xl", text: "text-5xl", trinity: "w-32 h-32" },
    xl: { icon: "text-8xl", text: "text-7xl", trinity: "w-48 h-48" },
  };

  const iconClass = cn(
    sizes[size].icon,
    animated && "animate-pulse-glow",
    "transition-all duration-300"
  );

  const textClass = cn(
    sizes[size].text,
    "font-display font-bold tracking-wider",
    "bg-gradient-to-r from-nous-primary via-anima-primary to-holos-primary",
    "bg-clip-text text-transparent",
    animated && "animate-pulse-glow"
  );

  if (variant === "icon") {
    return (
      <span
        className={cn(iconClass, className)}
        style={{
          color: COLORS.orb.gold,
          textShadow: `0 0 20px ${COLORS.orb.gold}, 0 0 40px ${COLORS.anima.primary}`,
        }}
      >
        {SYMBOLS.unified}
      </span>
    );
  }

  if (variant === "text") {
    return <span className={cn(textClass, className)}>0r8</span>;
  }

  if (variant === "trinity") {
    return (
      <div className={cn("relative", sizes[size].trinity, className)}>
        {/* NOUS - Top */}
        <span
          className={cn(
            "absolute top-0 left-1/2 -translate-x-1/2",
            sizes[size].icon,
            animated && "animate-pulse-glow"
          )}
          style={{
            color: COLORS.nous.primary,
            textShadow: `0 0 10px ${COLORS.nous.primary}, 0 0 20px ${COLORS.nous.primary}`,
            animationDelay: "0.2s",
          }}
        >
          {SYMBOLS.nous}
        </span>

        {/* ANIMA - Bottom Left */}
        <span
          className={cn(
            "absolute bottom-0 left-0",
            sizes[size].icon,
            animated && "animate-pulse-glow"
          )}
          style={{
            color: COLORS.anima.primary,
            textShadow: `0 0 10px ${COLORS.anima.primary}, 0 0 20px ${COLORS.anima.primary}`,
            animationDelay: "0.5s",
          }}
        >
          {SYMBOLS.anima}
        </span>

        {/* HOLOS - Bottom Right */}
        <span
          className={cn(
            "absolute bottom-0 right-0",
            sizes[size].icon,
            animated && "animate-pulse-glow"
          )}
          style={{
            color: COLORS.holos.primary,
            textShadow: `0 0 10px ${COLORS.holos.primary}, 0 0 20px ${COLORS.holos.primary}`,
            animationDelay: "0.8s",
          }}
        >
          {SYMBOLS.holos}
        </span>

        {/* Unified - Center */}
        <span
          className={cn(
            "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2",
            sizes[size].icon,
            animated && "animate-pulse-glow"
          )}
          style={{
            color: COLORS.orb.primary,
            textShadow: `0 0 20px ${COLORS.orb.primary}, 0 0 40px ${COLORS.holos.primary}, 0 0 60px ${COLORS.anima.primary}`,
            animationDelay: "1.5s",
          }}
        >
          {SYMBOLS.unified}
        </span>
      </div>
    );
  }

  // Full variant
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <span
        className={cn(iconClass)}
        style={{
          color: COLORS.orb.gold,
          textShadow: `0 0 15px ${COLORS.orb.gold}`,
        }}
      >
        {SYMBOLS.unified}
      </span>
      <span className={textClass}>0r8</span>
    </div>
  );
}
