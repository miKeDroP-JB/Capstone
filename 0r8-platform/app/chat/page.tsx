"use client";

/**
 * 0r8 Chat Interface
 * The Operating System for Human Potential
 */

import { useState, useRef, useEffect } from "react";
import { ParticleCanvas } from "@/components/particles/ParticleCanvas";
import { Logo } from "@/components/ui/Logo";
import { ThreeIModeSelector } from "@/components/3i/ThreeIModeSelector";
import { DomainSelector } from "@/components/3i/DomainSelector";
import { DemigodSelector } from "@/components/3i/DemigodSelector";
import { use3iStore } from "@/lib/stores/use-3i-store";
import { useChatStore } from "@/lib/stores/use-chat-store";
import { cn, generateId, getPillarColor, getPillarSymbol } from "@/lib/utils";
import { DEMIGODS, SYMBOLS } from "@/lib/constants";
import type { Message } from "@/types";
import Link from "next/link";

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [showConfig, setShowConfig] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { mode, weights, domain, demigod, dominantPillar } = use3iStore();
  const { messages, isLoading, addMessage, setLoading } = useChatStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: input.trim(),
      createdAt: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput("");
    setLoading(true);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const activeDemigod = demigod ? DEMIGODS[demigod] : null;
      const aiMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: `[${activeDemigod?.name || "0r8"}] This is a simulated response. Connect to the brain_3i.py backend for real AI responses.\n\nYour current configuration:\n- Mode: ${mode}\n- Domain: ${domain || "None"}\n- Demigod: ${activeDemigod?.name || "Auto-select"}\n- Weights: NOUS ${Math.round(weights.nous * 100)}% / ANIMA ${Math.round(weights.anima * 100)}% / HOLOS ${Math.round(weights.holos * 100)}%`,
        createdAt: new Date().toISOString(),
        metadata: {
          demigod: demigod || undefined,
          weights,
        },
      };
      addMessage(aiMessage);
      setLoading(false);
    }, 1500);
  };

  const activeDemigod = demigod ? DEMIGODS[demigod] : null;

  return (
    <div className="flex h-screen bg-void">
      {/* Particles (subtle in chat) */}
      <ParticleCanvas particleCount={60} connectDistance={80} />

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-30 w-80 bg-space border-r border-white/5 transition-transform duration-300 lg:relative lg:translate-x-0",
          showConfig ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full p-4 overflow-y-auto">
          {/* Logo */}
          <Link href="/" className="mb-6">
            <Logo variant="full" size="sm" />
          </Link>

          {/* Config Sections */}
          <div className="space-y-4 flex-1">
            <ThreeIModeSelector />
            <DomainSelector />
            <DemigodSelector />
          </div>

          {/* Close button (mobile) */}
          <button
            onClick={() => setShowConfig(false)}
            className="lg:hidden mt-4 btn-secondary w-full"
          >
            Close
          </button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative z-10">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-space/80 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowConfig(true)}
              className="lg:hidden p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>

            {/* Active Demigod */}
            {activeDemigod ? (
              <div className="flex items-center gap-2">
                <span className="text-2xl">{activeDemigod.symbol}</span>
                <div>
                  <div className="font-medium text-sm">{activeDemigod.name}</div>
                  <div className="text-xs text-white/40">
                    {activeDemigod.domain}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span
                  className="text-2xl"
                  style={{
                    color: getPillarColor(dominantPillar),
                    textShadow: `0 0 10px ${getPillarColor(dominantPillar)}`,
                  }}
                >
                  {getPillarSymbol(dominantPillar)}
                </span>
                <div>
                  <div className="font-medium text-sm">0r8</div>
                  <div className="text-xs text-white/40 capitalize">
                    {dominantPillar}-dominant
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Weights Display */}
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 text-xs">
              <span className="text-nous-primary">
                {SYMBOLS.nous} {Math.round(weights.nous * 100)}%
              </span>
              <span className="text-white/20">|</span>
              <span className="text-anima-primary">
                {SYMBOLS.anima} {Math.round(weights.anima * 100)}%
              </span>
              <span className="text-white/20">|</span>
              <span className="text-holos-primary">
                {SYMBOLS.holos} {Math.round(weights.holos * 100)}%
              </span>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Logo variant="trinity" size="lg" animated className="mb-8" />
              <h2 className="text-2xl font-display gradient-text-3i mb-2">
                Welcome to 0r8
              </h2>
              <p className="text-white/50 max-w-md">
                The Operating System for Human Potential. Configure your 3i
                balance and begin your journey.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "max-w-3xl",
                  message.role === "user" ? "ml-auto" : "mr-auto"
                )}
              >
                <div
                  className={cn(
                    "p-4 rounded-xl",
                    message.role === "user"
                      ? "bg-anima-primary/20 border border-anima-primary/30"
                      : "bg-white/5 border border-white/10"
                  )}
                >
                  {message.role === "assistant" && message.metadata?.demigod && (
                    <div className="flex items-center gap-2 mb-2 text-sm text-white/60">
                      <span>{DEMIGODS[message.metadata.demigod].symbol}</span>
                      <span>{DEMIGODS[message.metadata.demigod].name}</span>
                    </div>
                  )}
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="max-w-3xl mr-auto">
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-anima-primary animate-pulse" />
                  <div
                    className="w-2 h-2 rounded-full bg-nous-primary animate-pulse"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <div
                    className="w-2 h-2 rounded-full bg-holos-primary animate-pulse"
                    style={{ animationDelay: "0.4s" }}
                  />
                  <span className="text-sm text-white/40 ml-2">
                    Processing...
                  </span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-white/5 bg-space/80 backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Speak your intention..."
                className="input-dark flex-1"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </main>

      {/* Overlay for mobile sidebar */}
      {showConfig && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setShowConfig(false)}
        />
      )}
    </div>
  );
}
