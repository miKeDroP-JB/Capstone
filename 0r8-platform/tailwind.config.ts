import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // 0r8 Design System Colors
      colors: {
        // NOUS - Mercury - Intelligence
        nous: {
          primary: "#00D4FF",
          glow: "#00F0FF",
          dark: "#0A1628",
        },
        // ANIMA - Sulfur - Intuition
        anima: {
          primary: "#8B5CF6",
          glow: "#A78BFA",
          dark: "#1E1033",
        },
        // HOLOS - Salt - Integration
        holos: {
          primary: "#F59E0B",
          glow: "#FBBF24",
          dark: "#1C1508",
        },
        // 0r8 Unified
        orb: {
          primary: "#FFF7ED",
          glow: "#FFFFFF",
          gold: "#FFD700",
        },
        // Backgrounds
        void: "#050505",
        space: "#0A0A0F",
        subtle: "#111118",
      },
      // Typography
      fontFamily: {
        display: ["Cinzel", "serif"],
        body: ["Space Grotesk", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      // Animations
      animation: {
        "pulse-glow": "pulse-glow 5.45s ease-in-out infinite",
        "fade-in-up": "fadeInUp 0.8s ease-out forwards",
        "symbol-reveal": "symbolReveal 1s ease-out forwards",
        "draw-line": "drawLine 1.5s ease-out forwards",
        float: "float 3s ease-in-out infinite",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { opacity: "1", filter: "brightness(1)" },
          "50%": { opacity: "0.85", filter: "brightness(1.2)" },
        },
        fadeInUp: {
          from: { opacity: "0", transform: "translateY(30px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        symbolReveal: {
          from: {
            opacity: "0",
            filter: "blur(10px)",
            transform: "scale(0.8)",
          },
          to: { opacity: "1", filter: "blur(0)", transform: "scale(1)" },
        },
        drawLine: {
          from: { strokeDashoffset: "200" },
          to: { strokeDashoffset: "0" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
      // Box shadows for glows
      boxShadow: {
        "nous-glow":
          "0 0 10px #00D4FF, 0 0 20px #00D4FF, 0 0 40px rgba(0, 212, 255, 0.4)",
        "anima-glow":
          "0 0 10px #8B5CF6, 0 0 20px #8B5CF6, 0 0 40px rgba(139, 92, 246, 0.4)",
        "holos-glow":
          "0 0 10px #F59E0B, 0 0 20px #F59E0B, 0 0 40px rgba(245, 158, 11, 0.4)",
        "unified-glow":
          "0 0 20px #FFF7ED, 0 0 40px #F59E0B, 0 0 60px #8B5CF6, 0 0 80px #00D4FF",
      },
    },
  },
  plugins: [],
};

export default config;
