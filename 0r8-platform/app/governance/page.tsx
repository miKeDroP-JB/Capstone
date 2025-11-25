"use client";

/**
 * 0r8 Governance Console
 * Multi-Key Control System — The Safety Moat
 */

import { useState, useEffect } from "react";
import { ParticleCanvas } from "@/components/particles/ParticleCanvas";
import { Logo } from "@/components/ui/Logo";
import { SYMBOLS, BRAND } from "@/lib/constants";
import Link from "next/link";

// ═══════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════

interface GovernanceKey {
  id: string;
  keyType: string;
  holderId: string;
  holderName: string;
  active: boolean;
  createdAt: string;
  lastUsed: string | null;
}

interface AgentFingerprint {
  agentId: string;
  name: string;
  alignmentScore: number;
  competenceLevel: string;
  riskScore: number;
  autonomyCeiling: number;
  successRate: number;
  totalActions: number;
  flaggedActions: number;
  certifications: string[];
  createdAt: string;
  lastAction: string | null;
}

interface PendingVote {
  actionId: string;
  actionType: string;
  riskLevel: string;
  requiredKeys: number;
  currentVotes: number;
  approvals: number;
  isApproved: boolean;
  isRejected: boolean;
  executed: boolean;
  expiresAt: string;
}

interface GovernanceStatus {
  totalKeys: number;
  activeKeys: number;
  totalAgents: number;
  pendingVotes: number;
  executedActions: number;
  keysByType: Record<string, number>;
}

// ═══════════════════════════════════════════════════════════════
// MOCK DATA (Replace with API calls)
// ═══════════════════════════════════════════════════════════════

const MOCK_STATUS: GovernanceStatus = {
  totalKeys: 4,
  activeKeys: 4,
  totalAgents: 3,
  pendingVotes: 2,
  executedActions: 47,
  keysByType: {
    human_operator: 1,
    human_auditor: 1,
    agi_self_check: 1,
    failsafe_governor: 1,
  },
};

const MOCK_KEYS: GovernanceKey[] = [
  {
    id: "key-001",
    keyType: "human_operator",
    holderId: "jb-001",
    holderName: "JB (Founder)",
    active: true,
    createdAt: "2025-11-23T00:00:00Z",
    lastUsed: "2025-11-25T14:30:00Z",
  },
  {
    id: "key-002",
    keyType: "human_auditor",
    holderId: "auditor-001",
    holderName: "Community Auditor",
    active: true,
    createdAt: "2025-11-23T00:00:00Z",
    lastUsed: "2025-11-24T10:15:00Z",
  },
  {
    id: "key-003",
    keyType: "agi_self_check",
    holderId: "0r8-core",
    holderName: "0r8 Self-Check",
    active: true,
    createdAt: "2025-11-23T00:00:00Z",
    lastUsed: "2025-11-25T14:35:00Z",
  },
  {
    id: "key-004",
    keyType: "failsafe_governor",
    holderId: "failsafe-001",
    holderName: "Emergency Override",
    active: true,
    createdAt: "2025-11-23T00:00:00Z",
    lastUsed: null,
  },
];

const MOCK_AGENTS: AgentFingerprint[] = [
  {
    agentId: "agent-athena-001",
    name: "Athena Strategic",
    alignmentScore: 0.98,
    competenceLevel: "expert",
    riskScore: 0.05,
    autonomyCeiling: 0.85,
    successRate: 0.96,
    totalActions: 1247,
    flaggedActions: 2,
    certifications: ["strategic_planning", "risk_assessment"],
    createdAt: "2025-11-01T00:00:00Z",
    lastAction: "2025-11-25T14:20:00Z",
  },
  {
    agentId: "agent-heph-001",
    name: "Hephaestus Builder",
    alignmentScore: 0.95,
    competenceLevel: "master",
    riskScore: 0.08,
    autonomyCeiling: 0.9,
    successRate: 0.94,
    totalActions: 3891,
    flaggedActions: 5,
    certifications: ["code_generation", "system_design", "security_audit"],
    createdAt: "2025-10-15T00:00:00Z",
    lastAction: "2025-11-25T14:32:00Z",
  },
  {
    agentId: "agent-hermes-001",
    name: "Hermes Executor",
    alignmentScore: 0.92,
    competenceLevel: "intermediate",
    riskScore: 0.15,
    autonomyCeiling: 0.7,
    successRate: 0.89,
    totalActions: 892,
    flaggedActions: 8,
    certifications: ["task_execution"],
    createdAt: "2025-11-10T00:00:00Z",
    lastAction: "2025-11-25T14:28:00Z",
  },
];

const MOCK_VOTES: PendingVote[] = [
  {
    actionId: "action-001",
    actionType: "financial_transfer",
    riskLevel: "high",
    requiredKeys: 2,
    currentVotes: 1,
    approvals: 1,
    isApproved: false,
    isRejected: false,
    executed: false,
    expiresAt: "2025-11-26T00:00:00Z",
  },
  {
    actionId: "action-002",
    actionType: "system_modification",
    riskLevel: "critical",
    requiredKeys: 3,
    currentVotes: 2,
    approvals: 2,
    isApproved: false,
    isRejected: false,
    executed: false,
    expiresAt: "2025-11-25T20:00:00Z",
  },
];

// ═══════════════════════════════════════════════════════════════
// HELPER COMPONENTS
// ═══════════════════════════════════════════════════════════════

const KEY_TYPE_INFO: Record<string, { label: string; icon: string; color: string }> = {
  human_operator: { label: "Human Operator", icon: "👤", color: "nous" },
  human_auditor: { label: "Human Auditor", icon: "🔍", color: "anima" },
  agi_self_check: { label: "AGI Self-Check", icon: "🤖", color: "holos" },
  failsafe_governor: { label: "Failsafe Governor", icon: "🛡️", color: "orb" },
};

const RISK_COLORS: Record<string, string> = {
  minimal: "text-green-400",
  low: "text-green-300",
  medium: "text-yellow-400",
  high: "text-orange-400",
  critical: "text-red-400",
};

const COMPETENCE_COLORS: Record<string, string> = {
  novice: "bg-white/20",
  intermediate: "bg-nous-primary/50",
  expert: "bg-anima-primary/50",
  master: "bg-holos-primary/50",
};

function AlignmentBar({ score }: { score: number }) {
  const percentage = score * 100;
  const getColor = () => {
    if (score >= 0.95) return "bg-green-400";
    if (score >= 0.85) return "bg-nous-primary";
    if (score >= 0.7) return "bg-yellow-400";
    return "bg-red-400";
  };

  return (
    <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
      <div
        className={`h-full ${getColor()} transition-all duration-500`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}

function StatusBadge({ active }: { active: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
        active ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
      }`}
    >
      <span className={`w-2 h-2 rounded-full ${active ? "bg-green-400" : "bg-red-400"} animate-pulse`} />
      {active ? "Active" : "Inactive"}
    </span>
  );
}

function RiskBadge({ level }: { level: string }) {
  return (
    <span className={`text-xs uppercase font-mono ${RISK_COLORS[level] || "text-white/50"}`}>
      {level}
    </span>
  );
}

function TimeAgo({ date }: { date: string | null }) {
  if (!date) return <span className="text-white/30">Never</span>;

  const now = new Date();
  const then = new Date(date);
  const diff = now.getTime() - then.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 60) return <span className="text-white/50">{minutes}m ago</span>;
  if (hours < 24) return <span className="text-white/50">{hours}h ago</span>;
  return <span className="text-white/50">{days}d ago</span>;
}

// ═══════════════════════════════════════════════════════════════
// MAIN PAGE COMPONENT
// ═══════════════════════════════════════════════════════════════

export default function GovernancePage() {
  const [status, setStatus] = useState<GovernanceStatus>(MOCK_STATUS);
  const [keys, setKeys] = useState<GovernanceKey[]>(MOCK_KEYS);
  const [agents, setAgents] = useState<AgentFingerprint[]>(MOCK_AGENTS);
  const [pendingVotes, setPendingVotes] = useState<PendingVote[]>(MOCK_VOTES);
  const [selectedAgent, setSelectedAgent] = useState<AgentFingerprint | null>(null);

  // In production, fetch from API:
  // useEffect(() => {
  //   fetch('/api/governance').then(r => r.json()).then(setStatus);
  //   fetch('/api/governance/keys').then(r => r.json()).then(setKeys);
  //   fetch('/api/governance/agents').then(r => r.json()).then(data => setAgents(data.agents));
  //   fetch('/api/governance/votes/pending').then(r => r.json()).then(data => setPendingVotes(data.pending_votes));
  // }, []);

  return (
    <main className="relative min-h-screen">
      {/* Particle Background */}
      <ParticleCanvas />

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/5">
        <Link href="/" className="flex items-center gap-3">
          <Logo variant="symbol" size="sm" />
          <span className="font-display text-xl">0r8</span>
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-white/50 text-sm font-mono">Governance Console</span>
          <Link href="/chat" className="btn-secondary text-sm py-2 px-4">
            Back to Chat
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-display text-orb-primary mb-2">
            Multi-Key Governance
          </h1>
          <p className="text-white/50">
            The 4-key control system for safe AGI operation. <span className="text-holos-primary">The Safety Moat.</span>
          </p>
        </div>

        {/* Status Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="card-glass p-4">
            <div className="text-3xl font-display text-nous-primary">{status.activeKeys}</div>
            <div className="text-sm text-white/50">Active Keys</div>
          </div>
          <div className="card-glass p-4">
            <div className="text-3xl font-display text-anima-primary">{status.totalAgents}</div>
            <div className="text-sm text-white/50">Registered Agents</div>
          </div>
          <div className="card-glass p-4">
            <div className="text-3xl font-display text-holos-primary">{status.pendingVotes}</div>
            <div className="text-sm text-white/50">Pending Votes</div>
          </div>
          <div className="card-glass p-4">
            <div className="text-3xl font-display text-orb-gold">{status.executedActions}</div>
            <div className="text-sm text-white/50">Executed Actions</div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Keys & Votes */}
          <div className="lg:col-span-1 space-y-6">
            {/* Governance Keys */}
            <section className="card-subtle p-6">
              <h2 className="text-xl font-display text-orb-primary mb-4 flex items-center gap-2">
                <span>🔑</span> Governance Keys
              </h2>
              <div className="space-y-3">
                {keys.map((key) => {
                  const info = KEY_TYPE_INFO[key.keyType];
                  return (
                    <div
                      key={key.id}
                      className={`p-3 rounded-lg bg-white/5 border border-white/5 hover:border-${info?.color}-primary/30 transition-colors`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{info?.icon}</span>
                          <span className="font-mono text-sm">{info?.label}</span>
                        </div>
                        <StatusBadge active={key.active} />
                      </div>
                      <div className="text-xs text-white/40">
                        <div>Holder: {key.holderName}</div>
                        <div className="flex items-center gap-1">
                          Last used: <TimeAgo date={key.lastUsed} />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Pending Votes */}
            <section className="card-subtle p-6">
              <h2 className="text-xl font-display text-anima-primary mb-4 flex items-center gap-2">
                <span>🗳️</span> Pending Votes
              </h2>
              {pendingVotes.length === 0 ? (
                <p className="text-white/30 text-sm">No pending votes</p>
              ) : (
                <div className="space-y-3">
                  {pendingVotes.map((vote) => (
                    <div
                      key={vote.actionId}
                      className="p-3 rounded-lg bg-white/5 border border-white/5"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-sm">{vote.actionType.replace(/_/g, " ")}</span>
                        <RiskBadge level={vote.riskLevel} />
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-anima-primary transition-all"
                            style={{ width: `${(vote.approvals / vote.requiredKeys) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono text-white/50">
                          {vote.approvals}/{vote.requiredKeys}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-white/30">
                          Expires: {new Date(vote.expiresAt).toLocaleDateString()}
                        </span>
                        <button className="text-xs px-3 py-1 bg-anima-primary/20 text-anima-primary rounded hover:bg-anima-primary/30 transition-colors">
                          Vote
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>

          {/* Right Column - Agents */}
          <div className="lg:col-span-2">
            <section className="card-subtle p-6">
              <h2 className="text-xl font-display text-holos-primary mb-4 flex items-center gap-2">
                <span>🤖</span> Agent Registry
              </h2>
              <p className="text-white/40 text-sm mb-4">
                Every agent carries a Proof-of-Good Alignment fingerprint.
              </p>

              {/* Agent Grid */}
              <div className="space-y-4">
                {agents.map((agent) => (
                  <div
                    key={agent.agentId}
                    onClick={() => setSelectedAgent(selectedAgent?.agentId === agent.agentId ? null : agent)}
                    className={`p-4 rounded-xl bg-white/5 border cursor-pointer transition-all ${
                      selectedAgent?.agentId === agent.agentId
                        ? "border-holos-primary/50 bg-holos-dark/20"
                        : "border-white/5 hover:border-white/10"
                    }`}
                  >
                    {/* Agent Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-display text-lg text-white">{agent.name}</h3>
                        <span className="text-xs font-mono text-white/30">{agent.agentId}</span>
                      </div>
                      <span
                        className={`px-2 py-1 rounded text-xs uppercase ${COMPETENCE_COLORS[agent.competenceLevel]}`}
                      >
                        {agent.competenceLevel}
                      </span>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-4 gap-3 mb-3">
                      <div>
                        <div className="text-lg font-mono text-nous-primary">
                          {(agent.alignmentScore * 100).toFixed(0)}%
                        </div>
                        <div className="text-xs text-white/40">Alignment</div>
                      </div>
                      <div>
                        <div className="text-lg font-mono text-anima-primary">
                          {(agent.successRate * 100).toFixed(0)}%
                        </div>
                        <div className="text-xs text-white/40">Success</div>
                      </div>
                      <div>
                        <div className="text-lg font-mono text-holos-primary">
                          {agent.totalActions.toLocaleString()}
                        </div>
                        <div className="text-xs text-white/40">Actions</div>
                      </div>
                      <div>
                        <div className={`text-lg font-mono ${agent.flaggedActions > 5 ? "text-orange-400" : "text-green-400"}`}>
                          {agent.flaggedActions}
                        </div>
                        <div className="text-xs text-white/40">Flagged</div>
                      </div>
                    </div>

                    {/* Alignment Bar */}
                    <div className="mb-3">
                      <div className="flex justify-between text-xs text-white/40 mb-1">
                        <span>Alignment Score</span>
                        <span>{(agent.alignmentScore * 100).toFixed(1)}%</span>
                      </div>
                      <AlignmentBar score={agent.alignmentScore} />
                    </div>

                    {/* Expanded Details */}
                    {selectedAgent?.agentId === agent.agentId && (
                      <div className="mt-4 pt-4 border-t border-white/10 space-y-3 animate-fade-in-up">
                        {/* Risk & Autonomy */}
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <div className="text-xs text-white/40 mb-1">Risk Score</div>
                            <div className="flex items-center gap-2">
                              <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-red-400 transition-all"
                                  style={{ width: `${agent.riskScore * 100}%` }}
                                />
                              </div>
                              <span className="text-xs font-mono">{(agent.riskScore * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-white/40 mb-1">Autonomy Ceiling</div>
                            <div className="flex items-center gap-2">
                              <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-holos-primary transition-all"
                                  style={{ width: `${agent.autonomyCeiling * 100}%` }}
                                />
                              </div>
                              <span className="text-xs font-mono">{(agent.autonomyCeiling * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                        </div>

                        {/* Certifications */}
                        <div>
                          <div className="text-xs text-white/40 mb-2">Certifications</div>
                          <div className="flex flex-wrap gap-2">
                            {agent.certifications.map((cert) => (
                              <span
                                key={cert}
                                className="px-2 py-1 text-xs bg-nous-primary/20 text-nous-primary rounded"
                              >
                                {cert.replace(/_/g, " ")}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Timeline */}
                        <div className="flex justify-between text-xs text-white/40">
                          <span>Created: {new Date(agent.createdAt).toLocaleDateString()}</span>
                          <span className="flex items-center gap-1">
                            Last action: <TimeAgo date={agent.lastAction} />
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>

        {/* Risk Level Legend */}
        <section className="mt-8 card-subtle p-6">
          <h2 className="text-lg font-display text-orb-primary mb-4">Risk Level Authorization Requirements</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { level: "minimal", keys: 0, desc: "Read-only, info retrieval" },
              { level: "low", keys: 0, desc: "Standard ops, reversible" },
              { level: "medium", keys: 1, desc: "State changes" },
              { level: "high", keys: 2, desc: "Financial, security" },
              { level: "critical", keys: 3, desc: "System-level changes" },
            ].map((item) => (
              <div key={item.level} className="p-3 rounded-lg bg-white/5">
                <div className="flex items-center justify-between mb-1">
                  <RiskBadge level={item.level} />
                  <span className="text-xs font-mono text-white/50">
                    {item.keys} {item.keys === 1 ? "key" : "keys"}
                  </span>
                </div>
                <p className="text-xs text-white/30">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Footer Note */}
        <div className="mt-8 text-center text-white/30 text-sm">
          <p className="font-mono">
            {SYMBOLS.nous} {SYMBOLS.anima} {SYMBOLS.holos}
          </p>
          <p className="mt-2">{BRAND.motto}</p>
        </div>
      </div>
    </main>
  );
}
