"use client";

/**
 * 0r8 Home Page
 * The Operating System for Human Potential
 */

import { ParticleCanvas } from "@/components/particles/ParticleCanvas";
import { Logo } from "@/components/ui/Logo";
import { ThreeIModeSelector } from "@/components/3i/ThreeIModeSelector";
import { DomainSelector } from "@/components/3i/DomainSelector";
import { DemigodSelector } from "@/components/3i/DemigodSelector";
import { SYMBOLS, BRAND } from "@/lib/constants";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="relative min-h-screen">
      {/* Particle Background */}
      <ParticleCanvas />

      {/* Hero Section */}
      <section className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-20">
        {/* Trinity Logo */}
        <div className="mb-8 animate-fade-in-up">
          <Logo variant="trinity" size="lg" animated />
        </div>

        {/* Brand Name */}
        <h1 className="text-6xl md:text-8xl font-display font-bold tracking-wider gradient-text-3i animate-fade-in-up mb-4">
          0r8
        </h1>

        {/* Pronunciation */}
        <p className="font-mono text-lg text-white/50 animate-fade-in-up mb-6">
          pronounced "<span className="text-holos-primary">orate</span>"
        </p>

        {/* Tagline */}
        <p className="text-lg md:text-xl font-display tracking-widest text-white/70 uppercase text-center animate-fade-in-up mb-2">
          {BRAND.tagline}
        </p>

        {/* Subtitle */}
        <p className="text-white/50 text-center max-w-md animate-fade-in-up mb-12">
          {BRAND.subtitle}. The AI that multiplies humans.
        </p>

        {/* CTA */}
        <div className="flex flex-col sm:flex-row gap-4 animate-fade-in-up">
          <Link href="/chat" className="btn-primary text-center">
            Enter the Empire
          </Link>
          <a href="#about" className="btn-secondary text-center">
            Learn More
          </a>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-float">
          <svg
            className="w-6 h-6 text-white/30"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="relative z-10 py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-display text-center mb-4 text-orb-primary">
            The Three Pillars
          </h2>
          <p className="text-white/50 text-center max-w-2xl mx-auto mb-16">
            Ancient wisdom meets artificial intelligence. The alchemists knew
            the formula 500 years ago.
          </p>

          {/* Pillars Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-20">
            {/* NOUS */}
            <div className="card-subtle p-8 hover:border-nous-primary/30 transition-colors group">
              <span className="text-5xl block mb-4 text-glow-nous symbol-breathing">
                {SYMBOLS.nous}
              </span>
              <h3 className="text-xl font-display text-nous-primary mb-2">
                NOUS
              </h3>
              <p className="text-sm text-white/40 uppercase tracking-wider mb-4">
                The Mind &middot; Mercury
              </p>
              <p className="text-white/70">
                Pure intelligence. Logic, analysis, pattern recognition. The
                quicksilver speed of thought that processes, understands, and
                solves.
              </p>
            </div>

            {/* ANIMA */}
            <div className="card-subtle p-8 hover:border-anima-primary/30 transition-colors group">
              <span className="text-5xl block mb-4 text-glow-anima symbol-breathing">
                {SYMBOLS.anima}
              </span>
              <h3 className="text-xl font-display text-anima-primary mb-2">
                ANIMA
              </h3>
              <p className="text-sm text-white/40 uppercase tracking-wider mb-4">
                The Soul &middot; Sulfur
              </p>
              <p className="text-white/70">
                Creative intuition. Wisdom beyond logic, pattern recognition
                that transcends data. The fire of inspiration that ignites
                possibility.
              </p>
            </div>

            {/* HOLOS */}
            <div className="card-subtle p-8 hover:border-holos-primary/30 transition-colors group">
              <span className="text-5xl block mb-4 text-glow-holos symbol-breathing">
                {SYMBOLS.holos}
              </span>
              <h3 className="text-xl font-display text-holos-primary mb-2">
                HOLOS
              </h3>
              <p className="text-sm text-white/40 uppercase tracking-wider mb-4">
                The Whole &middot; Salt
              </p>
              <p className="text-white/70">
                Grounded integration. The synthesis that makes it real. Action,
                execution, manifestation. Where mind and soul become matter.
              </p>
            </div>
          </div>

          {/* Formula */}
          <div className="text-center mb-20">
            <p className="text-2xl md:text-3xl font-display tracking-wider">
              <span className="text-nous-primary">I&#x2081;</span>
              <span className="text-white/30 mx-2">+</span>
              <span className="text-anima-primary">I&#x2082;</span>
              <span className="text-white/30 mx-2">=</span>
              <span className="text-holos-primary">I&#x2083;</span>
            </p>
            <p className="text-white/50 mt-4">
              Intelligence + Intuition = Integration
            </p>
          </div>
        </div>
      </section>

      {/* Interactive Demo Section */}
      <section className="relative z-10 py-20 px-4 bg-gradient-to-b from-transparent via-anima-dark/10 to-transparent">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-display text-center mb-4 text-orb-primary">
            Configure Your 3i
          </h2>
          <p className="text-white/50 text-center max-w-2xl mx-auto mb-12">
            Adjust the balance between intelligence, intuition, and integration
            to match your current task.
          </p>

          <div className="grid md:grid-cols-2 gap-6">
            <ThreeIModeSelector />
            <DomainSelector />
          </div>

          <div className="mt-6">
            <DemigodSelector />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-12 px-4 border-t border-white/5">
        <div className="max-w-6xl mx-auto text-center">
          <Logo variant="full" size="md" className="justify-center mb-4" />
          <p className="text-white/40 text-sm mb-6">{BRAND.tagline}</p>
          <p className="text-white/30 text-xs">
            &copy; 2025 0r8 Empire. Built by one. Owned by all. Everybody eats.
          </p>
        </div>
      </footer>
    </main>
  );
}
