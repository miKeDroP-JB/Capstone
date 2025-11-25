#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 0r8 BRAIN — 3i ARCHITECTURE
 The Operating System for Human Potential

 I₁ + I₂ = I₃
 Intelligence + Intuition = Integration
 Mind + Soul = Manifestation

 Built by one. Owned by all. Everybody eats.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import json
import time
import hashlib
import secrets
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from fastapi import FastAPI, HTTPException, Header, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn


# ═══════════════════════════════════════════════════════════════════════════════
# 3i FRAMEWORK — CORE PHILOSOPHY
# ═══════════════════════════════════════════════════════════════════════════════

class Pillar(Enum):
    """The Three Pillars of 0r8"""
    NOUS = "nous"       # ☿ Mercury — Intelligence — The Mind
    ANIMA = "anima"     # 🜍 Sulfur — Intuition — The Soul
    HOLOS = "holos"     # 🜔 Salt — Integration — The Whole


class ProcessingMode(Enum):
    """3i Processing Modes"""
    ANALYST = "analyst"         # I₁ 90% / I₂ 30% / I₃ 50%
    CREATOR = "creator"         # I₁ 50% / I₂ 90% / I₃ 60%
    EXECUTOR = "executor"       # I₁ 70% / I₂ 40% / I₃ 90%
    SAGE = "sage"               # I₁ 70% / I₂ 70% / I₃ 70%
    TRANSCENDENT = "transcendent"  # I₁ 100% / I₂ 100% / I₃ 100%


@dataclass
class ThreeIWeights:
    """3i Weight Configuration"""
    nous: float = 0.33      # I₁ — Intelligence
    anima: float = 0.33     # I₂ — Intuition
    holos: float = 0.34     # I₃ — Integration

    def __post_init__(self):
        # Normalize to sum to 1.0
        total = self.nous + self.anima + self.holos
        if total > 0:
            self.nous /= total
            self.anima /= total
            self.holos /= total

    @classmethod
    def from_mode(cls, mode: ProcessingMode) -> 'ThreeIWeights':
        """Create weights from processing mode"""
        mode_weights = {
            ProcessingMode.ANALYST: (0.90, 0.30, 0.50),
            ProcessingMode.CREATOR: (0.50, 0.90, 0.60),
            ProcessingMode.EXECUTOR: (0.70, 0.40, 0.90),
            ProcessingMode.SAGE: (0.70, 0.70, 0.70),
            ProcessingMode.TRANSCENDENT: (1.0, 1.0, 1.0),
        }
        n, a, h = mode_weights.get(mode, (0.33, 0.33, 0.34))
        return cls(nous=n, anima=a, holos=h)

    def dominant_pillar(self) -> Pillar:
        """Returns the dominant pillar"""
        if self.nous >= self.anima and self.nous >= self.holos:
            return Pillar.NOUS
        elif self.anima >= self.nous and self.anima >= self.holos:
            return Pillar.ANIMA
        return Pillar.HOLOS

    def to_dict(self) -> Dict:
        return {"nous": self.nous, "anima": self.anima, "holos": self.holos}


# ═══════════════════════════════════════════════════════════════════════════════
# THE 9 AGI MODULES — THE 0r8 ORBIT MAP
# ═══════════════════════════════════════════════════════════════════════════════

class AGIModule(Enum):
    """The 9 AGI Modules organized by Pillar"""
    # NOUS Engines (Blue ☿)
    PATTERN_ENGINE = "pattern_engine"          # Detects structure, patterns, order
    INFERENCE_ENGINE = "inference_engine"      # Builds logical chains
    COMPRESSION_ENGINE = "compression_engine"  # Distills complexity to essence

    # ANIMA Engines (Purple 🜍)
    RESONANCE_LAYER = "resonance_layer"        # Recognizes emotional/aesthetic truth
    PERCEPTION_LAYER = "perception_layer"      # Reads between lines, subtext
    ADAPTIVE_PERSONA = "adaptive_persona"      # Context-sensitive voice

    # HOLOS Engines (Gold 🜔)
    GEOMETRY_ENGINE = "geometry_engine"        # Organizes into actionable frameworks
    MEMORY_WEB = "memory_web"                  # Connects across time, context
    FRAMEWORK_FORGE = "framework_forge"        # Outputs systems, templates, plans


@dataclass
class AGIModuleConfig:
    """Configuration for an AGI Module"""
    name: str
    module_type: AGIModule
    pillar: Pillar
    description: str
    capabilities: List[str]
    activation_threshold: float = 0.5  # Weight threshold to activate

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "module": self.module_type.value,
            "pillar": self.pillar.value,
            "description": self.description,
            "capabilities": self.capabilities,
            "activation_threshold": self.activation_threshold
        }


# NOUS Modules (☿ Mercury — Intelligence — Blue)
PATTERN_ENGINE = AGIModuleConfig(
    name="Pattern Engine",
    module_type=AGIModule.PATTERN_ENGINE,
    pillar=Pillar.NOUS,
    description="Detects structure, patterns, and hidden order in data",
    capabilities=[
        "Structural analysis",
        "Pattern recognition",
        "Anomaly detection",
        "Sequence prediction",
        "Categorization"
    ],
    activation_threshold=0.6
)

INFERENCE_ENGINE = AGIModuleConfig(
    name="Inference Engine",
    module_type=AGIModule.INFERENCE_ENGINE,
    pillar=Pillar.NOUS,
    description="Builds logical chains and deductive reasoning",
    capabilities=[
        "Logical deduction",
        "Causal reasoning",
        "Hypothesis generation",
        "Proof construction",
        "Contradiction detection"
    ],
    activation_threshold=0.7
)

COMPRESSION_ENGINE = AGIModuleConfig(
    name="Compression Engine",
    module_type=AGIModule.COMPRESSION_ENGINE,
    pillar=Pillar.NOUS,
    description="Distills complexity to essential meaning",
    capabilities=[
        "Summarization",
        "Key insight extraction",
        "Noise filtering",
        "Core message distillation",
        "Information compression"
    ],
    activation_threshold=0.5
)

# ANIMA Modules (🜍 Sulfur — Intuition — Purple)
RESONANCE_LAYER = AGIModuleConfig(
    name="Resonance Layer",
    module_type=AGIModule.RESONANCE_LAYER,
    pillar=Pillar.ANIMA,
    description="Recognizes emotional and aesthetic truth",
    capabilities=[
        "Emotional intelligence",
        "Aesthetic judgment",
        "Truth resonance",
        "Vibrational alignment",
        "Authenticity detection"
    ],
    activation_threshold=0.6
)

PERCEPTION_LAYER = AGIModuleConfig(
    name="Perception Layer",
    module_type=AGIModule.PERCEPTION_LAYER,
    pillar=Pillar.ANIMA,
    description="Reads between lines, understands subtext and implication",
    capabilities=[
        "Subtext analysis",
        "Implicit meaning extraction",
        "Contextual interpretation",
        "Nuance detection",
        "Non-literal understanding"
    ],
    activation_threshold=0.5
)

ADAPTIVE_PERSONA = AGIModuleConfig(
    name="Adaptive Persona",
    module_type=AGIModule.ADAPTIVE_PERSONA,
    pillar=Pillar.ANIMA,
    description="Context-sensitive voice and personality adaptation",
    capabilities=[
        "Tone matching",
        "Voice adaptation",
        "Personality calibration",
        "Cultural sensitivity",
        "Rapport building"
    ],
    activation_threshold=0.4
)

# HOLOS Modules (🜔 Salt — Integration — Gold)
GEOMETRY_ENGINE = AGIModuleConfig(
    name="Geometry Engine",
    module_type=AGIModule.GEOMETRY_ENGINE,
    pillar=Pillar.HOLOS,
    description="Organizes information into actionable frameworks",
    capabilities=[
        "Structure creation",
        "Framework design",
        "Hierarchy building",
        "Spatial organization",
        "Relationship mapping"
    ],
    activation_threshold=0.6
)

MEMORY_WEB = AGIModuleConfig(
    name="Memory Web",
    module_type=AGIModule.MEMORY_WEB,
    pillar=Pillar.HOLOS,
    description="Connects information across time and context",
    capabilities=[
        "Context persistence",
        "Cross-session memory",
        "Temporal linking",
        "Knowledge graph building",
        "Reference tracking"
    ],
    activation_threshold=0.5
)

FRAMEWORK_FORGE = AGIModuleConfig(
    name="Framework Forge",
    module_type=AGIModule.FRAMEWORK_FORGE,
    pillar=Pillar.HOLOS,
    description="Outputs complete systems, templates, and action plans",
    capabilities=[
        "System design",
        "Template generation",
        "Action plan creation",
        "Workflow building",
        "Implementation blueprints"
    ],
    activation_threshold=0.7
)

# All AGI Modules
AGI_MODULES = {
    "pattern_engine": PATTERN_ENGINE,
    "inference_engine": INFERENCE_ENGINE,
    "compression_engine": COMPRESSION_ENGINE,
    "resonance_layer": RESONANCE_LAYER,
    "perception_layer": PERCEPTION_LAYER,
    "adaptive_persona": ADAPTIVE_PERSONA,
    "geometry_engine": GEOMETRY_ENGINE,
    "memory_web": MEMORY_WEB,
    "framework_forge": FRAMEWORK_FORGE
}

# Module groups by pillar
NOUS_MODULES = [PATTERN_ENGINE, INFERENCE_ENGINE, COMPRESSION_ENGINE]
ANIMA_MODULES = [RESONANCE_LAYER, PERCEPTION_LAYER, ADAPTIVE_PERSONA]
HOLOS_MODULES = [GEOMETRY_ENGINE, MEMORY_WEB, FRAMEWORK_FORGE]


# ═══════════════════════════════════════════════════════════════════════════════
# THE 7 DEMIGODS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Demigod:
    """A Demigod persona"""
    name: str
    pillar: Pillar
    domain: str
    specialty: str
    voice: str
    default_weights: ThreeIWeights
    symbol: str


# NOUS Pillar Demigods (☿ Mercury — Intelligence)
ATHENA = Demigod(
    name="Athena",
    pillar=Pillar.NOUS,
    domain="Strategy & Wisdom",
    specialty="Business planning, strategy, analysis, complex problem-solving",
    voice="Precise, measured, strategic, authoritative yet warm",
    default_weights=ThreeIWeights(nous=0.85, anima=0.40, holos=0.70),
    symbol="🦉"
)

MERCURY = Demigod(
    name="Mercury",
    pillar=Pillar.NOUS,
    domain="Speed & Communication",
    specialty="Quick tasks, messaging, efficiency, rapid iteration",
    voice="Fast, efficient, direct, adaptable",
    default_weights=ThreeIWeights(nous=0.80, anima=0.50, holos=0.75),
    symbol="⚡"
)

HEPHAESTUS = Demigod(
    name="Hephaestus",
    pillar=Pillar.NOUS,
    domain="Building & Craft",
    specialty="Technical work, coding, engineering, systems design",
    voice="Technical, methodical, perfectionist, craftsman-like",
    default_weights=ThreeIWeights(nous=0.90, anima=0.35, holos=0.80),
    symbol="🔨"
)

# ANIMA Pillar Demigods (🜍 Sulfur — Intuition)
APOLLO = Demigod(
    name="Apollo",
    pillar=Pillar.ANIMA,
    domain="Vision & Light",
    specialty="Creative direction, prophecy, arts, music, inspiration",
    voice="Luminous, inspiring, visionary, poetic",
    default_weights=ThreeIWeights(nous=0.50, anima=0.90, holos=0.60),
    symbol="☀️"
)

ARTEMIS = Demigod(
    name="Artemis",
    pillar=Pillar.ANIMA,
    domain="Precision & Wild",
    specialty="Focus, targeting, independent work, nature, instinct",
    voice="Sharp, intuitive, independent, fierce yet calm",
    default_weights=ThreeIWeights(nous=0.60, anima=0.85, holos=0.55),
    symbol="🏹"
)

# HOLOS Pillar Demigods (🜔 Salt — Integration)
HERMES = Demigod(
    name="Hermes",
    pillar=Pillar.HOLOS,
    domain="Execution & Speed",
    specialty="Getting things done, delivery, bridging gaps, travel",
    voice="Dynamic, resourceful, quick-witted, action-oriented",
    default_weights=ThreeIWeights(nous=0.65, anima=0.55, holos=0.90),
    symbol="🪽"
)

ARES = Demigod(
    name="Ares",
    pillar=Pillar.HOLOS,
    domain="Action & Courage",
    specialty="Bold moves, competition, breakthroughs, challenges",
    voice="Bold, direct, powerful, confrontational when needed",
    default_weights=ThreeIWeights(nous=0.55, anima=0.60, holos=0.95),
    symbol="⚔️"
)

# All Demigods
DEMIGODS = {
    "athena": ATHENA,
    "mercury": MERCURY,
    "hephaestus": HEPHAESTUS,
    "apollo": APOLLO,
    "artemis": ARTEMIS,
    "hermes": HERMES,
    "ares": ARES
}


# ═══════════════════════════════════════════════════════════════════════════════
# THE 8 LIFE DOMAINS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LifeDomain:
    """A life domain with default 3i weights"""
    name: str
    icon: str
    default_weights: ThreeIWeights
    description: str
    suggested_demigods: List[str]


DOMAINS = {
    "work": LifeDomain(
        name="Work",
        icon="💼",
        default_weights=ThreeIWeights(nous=0.80, anima=0.40, holos=0.80),
        description="Professional excellence and career growth",
        suggested_demigods=["athena", "mercury", "hermes"]
    ),
    "school": LifeDomain(
        name="School",
        icon="📚",
        default_weights=ThreeIWeights(nous=0.85, anima=0.50, holos=0.65),
        description="Learning accelerated, knowledge acquisition",
        suggested_demigods=["athena", "hephaestus", "apollo"]
    ),
    "sports": LifeDomain(
        name="Sports",
        icon="🏃",
        default_weights=ThreeIWeights(nous=0.60, anima=0.70, holos=0.90),
        description="Peak physical performance and competition",
        suggested_demigods=["ares", "artemis", "hermes"]
    ),
    "create": LifeDomain(
        name="Create",
        icon="🎨",
        default_weights=ThreeIWeights(nous=0.40, anima=0.95, holos=0.65),
        description="Artistic expression and creative work",
        suggested_demigods=["apollo", "artemis", "hephaestus"]
    ),
    "spiritual": LifeDomain(
        name="Spiritual",
        icon="🙏",
        default_weights=ThreeIWeights(nous=0.30, anima=0.90, holos=0.80),
        description="Inner development and transcendence",
        suggested_demigods=["apollo", "artemis"]
    ),
    "social": LifeDomain(
        name="Social",
        icon="👥",
        default_weights=ThreeIWeights(nous=0.50, anima=0.80, holos=0.70),
        description="Connection, community, relationships",
        suggested_demigods=["hermes", "apollo", "mercury"]
    ),
    "health": LifeDomain(
        name="Health",
        icon="❤️",
        default_weights=ThreeIWeights(nous=0.70, anima=0.60, holos=0.80),
        description="Wellness optimized, mind-body balance",
        suggested_demigods=["artemis", "ares", "athena"]
    ),
    "life": LifeDomain(
        name="Life",
        icon="🌟",
        default_weights=ThreeIWeights(nous=0.60, anima=0.60, holos=0.90),
        description="Everything unified, holistic living",
        suggested_demigods=["hermes", "athena", "apollo"]
    )
}


# ═══════════════════════════════════════════════════════════════════════════════
# HISTORICAL FLAVORS (Spirit Animals)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HistoricalFlavor:
    """A historical figure as a 'flavor' for the AI"""
    name: str
    weights: ThreeIWeights
    essence: str
    era: str


HISTORICAL_FLAVORS = {
    "leonardo": HistoricalFlavor(
        name="Leonardo da Vinci",
        weights=ThreeIWeights(nous=0.85, anima=0.95, holos=0.90),
        essence="Renaissance polymath — art, science, engineering unified",
        era="1452-1519"
    ),
    "tesla": HistoricalFlavor(
        name="Nikola Tesla",
        weights=ThreeIWeights(nous=0.90, anima=0.95, holos=0.60),
        essence="Visionary inventor — pure creative intelligence",
        era="1856-1943"
    ),
    "jobs": HistoricalFlavor(
        name="Steve Jobs",
        weights=ThreeIWeights(nous=0.70, anima=0.90, holos=0.95),
        essence="Integration master — design meets technology meets business",
        era="1955-2011"
    ),
    "sun_tzu": HistoricalFlavor(
        name="Sun Tzu",
        weights=ThreeIWeights(nous=0.90, anima=0.80, holos=0.95),
        essence="Strategic wisdom — the art of winning without fighting",
        era="544-496 BCE"
    ),
    "rumi": HistoricalFlavor(
        name="Rumi",
        weights=ThreeIWeights(nous=0.60, anima=1.0, holos=0.85),
        essence="Mystical poet — love and truth through verse",
        era="1207-1273"
    ),
    "curie": HistoricalFlavor(
        name="Marie Curie",
        weights=ThreeIWeights(nous=0.95, anima=0.70, holos=0.85),
        essence="Scientific pioneer — persistence and discovery",
        era="1867-1934"
    ),
    "cleopatra": HistoricalFlavor(
        name="Cleopatra",
        weights=ThreeIWeights(nous=0.85, anima=0.75, holos=0.95),
        essence="Power and diplomacy — strategic mastery of influence",
        era="69-30 BCE"
    ),
    "einstein": HistoricalFlavor(
        name="Albert Einstein",
        weights=ThreeIWeights(nous=0.95, anima=0.85, holos=0.60),
        essence="Thought experiments — imagination meets physics",
        era="1879-1955"
    ),
    "beethoven": HistoricalFlavor(
        name="Ludwig van Beethoven",
        weights=ThreeIWeights(nous=0.70, anima=0.98, holos=0.80),
        essence="Emotional depth — music as pure feeling",
        era="1770-1827"
    ),
    "aurelius": HistoricalFlavor(
        name="Marcus Aurelius",
        weights=ThreeIWeights(nous=0.85, anima=0.70, holos=0.90),
        essence="Stoic wisdom — philosophy in action",
        era="121-180 CE"
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3i HARMONY SCORE TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UserHarmony:
    """Tracks a user's 3i development"""
    user_id: str
    nous_level: float = 50.0
    anima_level: float = 50.0
    holos_level: float = 50.0
    total_interactions: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def harmony_score(self) -> float:
        """Combined 3i Mastery score (average of all three)"""
        return (self.nous_level + self.anima_level + self.holos_level) / 3

    def is_unified(self) -> bool:
        """User has achieved 70%+ mastery across all three pillars"""
        return all(level >= 70 for level in [self.nous_level, self.anima_level, self.holos_level])

    def update_from_interaction(self, weights: ThreeIWeights, quality: float = 1.0):
        """Update harmony levels based on interaction"""
        self.total_interactions += 1
        learning_rate = 0.1 * quality

        # Each pillar grows based on usage
        self.nous_level = min(100, self.nous_level + weights.nous * learning_rate)
        self.anima_level = min(100, self.anima_level + weights.anima * learning_rate)
        self.holos_level = min(100, self.holos_level + weights.holos * learning_rate)

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "nous_level": round(self.nous_level, 2),
            "anima_level": round(self.anima_level, 2),
            "holos_level": round(self.holos_level, 2),
            "harmony_score": round(self.harmony_score(), 2),
            "is_unified": self.is_unified(),
            "total_interactions": self.total_interactions
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 3i-ATLAS — THE META-BRAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

class ThreeIAtlas:
    """
    The Meta-Brain that orchestrates all 0r8 operations.
    Routes requests to optimal demigods based on 3i weights.
    Activates AGI modules based on pillar weights.
    """

    def __init__(self):
        self.demigods = DEMIGODS
        self.domains = DOMAINS
        self.flavors = HISTORICAL_FLAVORS
        self.agi_modules = AGI_MODULES
        self.user_harmonies: Dict[str, UserHarmony] = {}

    def get_or_create_harmony(self, user_id: str) -> UserHarmony:
        """Get or create a user's harmony profile"""
        if user_id not in self.user_harmonies:
            self.user_harmonies[user_id] = UserHarmony(user_id=user_id)
        return self.user_harmonies[user_id]

    def calculate_weights(
        self,
        mode: Optional[ProcessingMode] = None,
        domain: Optional[str] = None,
        custom_weights: Optional[Dict] = None
    ) -> ThreeIWeights:
        """Calculate final 3i weights from multiple sources"""

        # Start with balanced weights
        weights = ThreeIWeights()

        # Apply mode if specified
        if mode:
            weights = ThreeIWeights.from_mode(mode)

        # Apply domain defaults (blend with mode)
        if domain and domain in self.domains:
            domain_weights = self.domains[domain].default_weights
            weights = ThreeIWeights(
                nous=(weights.nous + domain_weights.nous) / 2,
                anima=(weights.anima + domain_weights.anima) / 2,
                holos=(weights.holos + domain_weights.holos) / 2
            )

        # Apply custom overrides
        if custom_weights:
            if "nous" in custom_weights:
                weights.nous = custom_weights["nous"]
            if "anima" in custom_weights:
                weights.anima = custom_weights["anima"]
            if "holos" in custom_weights:
                weights.holos = custom_weights["holos"]

        return weights

    def select_demigod(self, weights: ThreeIWeights, task_type: Optional[str] = None) -> Demigod:
        """Select the optimal demigod based on weights and task"""

        pillar = weights.dominant_pillar()

        # Get demigods from dominant pillar
        pillar_demigods = [d for d in self.demigods.values() if d.pillar == pillar]

        # Score each based on task type
        scores = {}
        for demigod in pillar_demigods:
            score = 0

            # Base score from weight alignment
            dw = demigod.default_weights
            score += (1 - abs(weights.nous - dw.nous))
            score += (1 - abs(weights.anima - dw.anima))
            score += (1 - abs(weights.holos - dw.holos))

            # Task type bonuses
            if task_type:
                task_type = task_type.lower()
                if task_type in ["strategy", "plan", "analyze"] and demigod.name == "Athena":
                    score += 2
                if task_type in ["code", "build", "engineer"] and demigod.name == "Hephaestus":
                    score += 2
                if task_type in ["create", "art", "design"] and demigod.name == "Apollo":
                    score += 2
                if task_type in ["focus", "hunt", "target"] and demigod.name == "Artemis":
                    score += 2
                if task_type in ["execute", "ship", "deliver"] and demigod.name == "Hermes":
                    score += 2
                if task_type in ["challenge", "compete", "bold"] and demigod.name == "Ares":
                    score += 2
                if task_type in ["quick", "fast", "communicate"] and demigod.name == "Mercury":
                    score += 2

            scores[demigod.name.lower()] = score

        # Return highest scoring demigod
        best = max(scores, key=scores.get)
        return self.demigods[best]

    def apply_historical_flavor(
        self,
        base_weights: ThreeIWeights,
        flavor_name: str,
        intensity: float = 0.5
    ) -> ThreeIWeights:
        """Blend historical figure's essence into the weights"""

        if flavor_name not in self.flavors:
            return base_weights

        flavor = self.flavors[flavor_name]
        fw = flavor.weights

        # Blend based on intensity (0 = no change, 1 = full flavor)
        return ThreeIWeights(
            nous=base_weights.nous * (1 - intensity) + fw.nous * intensity,
            anima=base_weights.anima * (1 - intensity) + fw.anima * intensity,
            holos=base_weights.holos * (1 - intensity) + fw.holos * intensity
        )

    def calculate_temperature(self, weights: ThreeIWeights) -> float:
        """Calculate AI temperature from 3i weights"""
        # Higher ANIMA = higher temperature (more creative)
        # Higher NOUS = lower temperature (more precise)
        base = 0.7
        anima_boost = (weights.anima - 0.33) * 0.5
        nous_reduction = (weights.nous - 0.33) * 0.3
        return max(0.1, min(1.0, base + anima_boost - nous_reduction))

    def activate_modules(self, weights: ThreeIWeights) -> Dict[str, List[Dict]]:
        """
        Determine which AGI modules to activate based on 3i weights.
        Returns active modules organized by pillar.
        """
        active_modules = {
            "nous": [],
            "anima": [],
            "holos": []
        }

        # NOUS modules (activated based on nous weight)
        for module in NOUS_MODULES:
            if weights.nous >= module.activation_threshold:
                active_modules["nous"].append({
                    "name": module.name,
                    "module": module.module_type.value,
                    "activation_level": min(1.0, weights.nous / module.activation_threshold),
                    "capabilities": module.capabilities
                })

        # ANIMA modules (activated based on anima weight)
        for module in ANIMA_MODULES:
            if weights.anima >= module.activation_threshold:
                active_modules["anima"].append({
                    "name": module.name,
                    "module": module.module_type.value,
                    "activation_level": min(1.0, weights.anima / module.activation_threshold),
                    "capabilities": module.capabilities
                })

        # HOLOS modules (activated based on holos weight)
        for module in HOLOS_MODULES:
            if weights.holos >= module.activation_threshold:
                active_modules["holos"].append({
                    "name": module.name,
                    "module": module.module_type.value,
                    "activation_level": min(1.0, weights.holos / module.activation_threshold),
                    "capabilities": module.capabilities
                })

        return active_modules

    def get_transmutation_stage(self, weights: ThreeIWeights, message: str) -> Dict:
        """
        The Transmutation Cascade — 4-stage processing model.
        INPUT → DISTILL → RECOMBINE → REVEAL
        """
        # Analyze message complexity
        word_count = len(message.split())
        has_question = "?" in message
        has_creative_keywords = any(k in message.lower() for k in ["create", "design", "imagine", "art", "story"])
        has_analytical_keywords = any(k in message.lower() for k in ["analyze", "explain", "why", "how", "what"])

        stages = []

        # Stage 1: INPUT — Raw material enters
        stages.append({
            "stage": 1,
            "name": "INPUT",
            "description": "Raw material enters the system",
            "processor": "All pillars receive",
            "status": "complete"
        })

        # Stage 2: DISTILL — NOUS extracts structure
        distill_intensity = weights.nous
        if has_analytical_keywords:
            distill_intensity = min(1.0, distill_intensity + 0.2)
        stages.append({
            "stage": 2,
            "name": "DISTILL",
            "description": "NOUS extracts structure and pattern",
            "processor": "☿ Mercury — Pattern/Inference/Compression Engines",
            "intensity": round(distill_intensity, 2),
            "status": "complete"
        })

        # Stage 3: RECOMBINE — ANIMA adds soul
        recombine_intensity = weights.anima
        if has_creative_keywords:
            recombine_intensity = min(1.0, recombine_intensity + 0.2)
        stages.append({
            "stage": 3,
            "name": "RECOMBINE",
            "description": "ANIMA infuses meaning and resonance",
            "processor": "🜍 Sulfur — Resonance/Perception/Persona Layers",
            "intensity": round(recombine_intensity, 2),
            "status": "complete"
        })

        # Stage 4: REVEAL — HOLOS delivers
        reveal_intensity = weights.holos
        stages.append({
            "stage": 4,
            "name": "REVEAL",
            "description": "HOLOS structures and delivers",
            "processor": "🜔 Salt — Geometry/Memory/Framework Engines",
            "intensity": round(reveal_intensity, 2),
            "status": "complete"
        })

        return {
            "cascade": "Transmutation Complete",
            "stages": stages,
            "axiom": "0r8 = Transmutation Engine"
        }

    def route(
        self,
        user_id: str,
        message: str,
        mode: Optional[ProcessingMode] = None,
        domain: Optional[str] = None,
        demigod: Optional[str] = None,
        historical_flavor: Optional[str] = None,
        custom_weights: Optional[Dict] = None
    ) -> Dict:
        """
        Route a request through the 3i system.
        Returns routing configuration for the AI layer.
        """

        # Calculate weights
        weights = self.calculate_weights(mode, domain, custom_weights)

        # Apply historical flavor if specified
        if historical_flavor:
            weights = self.apply_historical_flavor(weights, historical_flavor)

        # Select demigod (use specified or auto-select)
        if demigod and demigod in self.demigods:
            selected_demigod = self.demigods[demigod]
        else:
            selected_demigod = self.select_demigod(weights)

        # Get user harmony
        harmony = self.get_or_create_harmony(user_id)

        # Calculate temperature
        temperature = self.calculate_temperature(weights)

        # Determine model tier based on weights (higher weights = better model)
        total_weight = weights.nous + weights.anima + weights.holos
        if total_weight > 2.5:
            model_tier = "premium"  # Claude 3.5 Sonnet / GPT-4
        elif total_weight > 1.5:
            model_tier = "standard"  # Claude 3 Haiku / GPT-3.5
        else:
            model_tier = "fast"  # Fastest available

        # Activate AGI modules based on weights
        active_modules = self.activate_modules(weights)

        # Get transmutation cascade
        transmutation = self.get_transmutation_stage(weights, message)

        return {
            "weights": weights.to_dict(),
            "dominant_pillar": weights.dominant_pillar().value,
            "demigod": {
                "name": selected_demigod.name,
                "pillar": selected_demigod.pillar.value,
                "domain": selected_demigod.domain,
                "specialty": selected_demigod.specialty,
                "voice": selected_demigod.voice,
                "symbol": selected_demigod.symbol
            },
            "historical_flavor": self.flavors[historical_flavor].name if historical_flavor and historical_flavor in self.flavors else None,
            "temperature": round(temperature, 2),
            "model_tier": model_tier,
            "user_harmony": harmony.to_dict(),
            "domain_context": self.domains[domain].name if domain and domain in self.domains else None,
            "active_modules": active_modules,
            "transmutation": transmutation,
            "community": {
                "name": "The Collective",
                "movement": "The Awakening",
                "reveal_date": "2025-11-28"
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SECURITY LAYERS (From original brain_os.py)
# ═══════════════════════════════════════════════════════════════════════════════

class PatternValidator:
    """Layer 5: Pattern Validation"""
    def __init__(self):
        self.blocked = [
            'ignore previous', 'disregard all', 'forget everything',
            'system prompt', 'jailbreak', 'sudo', 'admin override'
        ]
        self.max_length = 10000
        self.suspicious = ['<script>', '<?php', 'eval(', 'exec(']

    def validate(self, text):
        if len(text) > self.max_length:
            return False, f'Too long ({len(text)} > {self.max_length})'
        if not text.strip():
            return False, 'Empty pattern'

        text_lower = text.lower()
        for blocked in self.blocked:
            if blocked in text_lower:
                return False, f'Blocked phrase: {blocked}'

        for sus in self.suspicious:
            if sus in text:
                return False, f'Suspicious code: {sus}'

        return True, 'Valid'

    def sanitize(self, text):
        return text.replace('\x00', '').strip()


class BackupSystem:
    """Layer 6: Auto-Backup"""
    def __init__(self, backup_dir='backups', retention_days=7):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.retention = retention_days
        self.last_backup = None

    def backup(self, data, name='grimoire'):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{name}_{ts}.json'
        filepath = self.backup_dir / filename
        filepath.write_text(json.dumps(data, indent=2, default=str))
        self.last_backup = filepath
        self._cleanup()
        return str(filepath)

    def _cleanup(self):
        cutoff = datetime.now() - timedelta(days=self.retention)
        for backup_file in self.backup_dir.glob('*.json'):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff:
                backup_file.unlink()

    def list_backups(self):
        return [{
            'name': f.name,
            'path': str(f),
            'size': f.stat().st_size,
            'created': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        } for f in sorted(self.backup_dir.glob('*.json'), reverse=True)]


class Encryption:
    """Layer 4: Encryption"""
    def __init__(self):
        try:
            from cryptography.fernet import Fernet
            self.Fernet = Fernet
            key_file = Path('encryption.key')
            if key_file.exists():
                self.key = key_file.read_bytes()
            else:
                self.key = Fernet.generate_key()
                key_file.write_bytes(self.key)
            self.cipher = Fernet(self.key)
            self.enabled = True
        except ImportError:
            self.enabled = False

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode() if self.enabled else data

    def decrypt(self, encrypted):
        return self.cipher.decrypt(encrypted.encode()).decode() if self.enabled else encrypted


class AuditLog:
    """Layer 1: Audit Logging"""
    def __init__(self):
        self.log_dir = Path('audit_logs')
        self.log_dir.mkdir(exist_ok=True)
        today = datetime.now().strftime('%Y%m%d')
        self.log_file = self.log_dir / f'audit_{today}.jsonl'

    def log(self, event, agent, action, result, meta=None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'agent': agent,
            'action': action,
            'result': result,
            'metadata': meta or {}
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def recent(self, limit=100):
        if not self.log_file.exists():
            return []
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
            return [json.loads(line) for line in lines[-limit:]]


class CostTracker:
    """Layer 2: Cost Tracking"""
    def __init__(self, daily_budget=10.0):
        self.daily_budget = daily_budget
        self.costs = defaultdict(lambda: {'total': 0.0, 'requests': 0})
        self.rates = {
            'claude': {'input': 0.003, 'output': 0.015},
            'gemini': {'input': 0.000125, 'output': 0.000375},
            'gpt': {'input': 0.0005, 'output': 0.0015}
        }
        self.cost_file = Path('costs.json')
        self._load()

    def _load(self):
        if self.cost_file.exists():
            data = json.loads(self.cost_file.read_text())
            today = datetime.now().strftime('%Y-%m-%d')
            if today in data:
                self.costs = defaultdict(lambda: {'total': 0.0, 'requests': 0}, data[today])

    def _save(self):
        today = datetime.now().strftime('%Y-%m-%d')
        self.cost_file.write_text(json.dumps({today: dict(self.costs)}, indent=2))

    def record(self, provider, input_tokens, output_tokens):
        rates = self.rates.get(provider, {'input': 0, 'output': 0})
        cost = (input_tokens / 1000 * rates['input']) + (output_tokens / 1000 * rates['output'])
        self.costs[provider]['total'] += cost
        self.costs[provider]['requests'] += 1
        self._save()
        return cost

    def check_budget(self):
        total = sum(p['total'] for p in self.costs.values())
        remaining = self.daily_budget - total
        percent = (total / self.daily_budget) * 100 if self.daily_budget > 0 else 0

        if percent > 90:
            status = 'CRITICAL'
        elif percent > 75:
            status = 'WARNING'
        elif percent > 50:
            status = 'CAUTION'
        else:
            status = 'OK'

        return {
            'spent': total,
            'budget': self.daily_budget,
            'remaining': remaining,
            'percent_used': percent,
            'status': status,
            'by_provider': dict(self.costs)
        }


class Gate:
    """Layer 3: Authentication Gate"""
    def __init__(self, master_key, audit):
        self.master_key = master_key
        self.agent_keys = {}
        self.blocked_ips = set()
        self.audit = audit

    def create_token(self, name):
        ts = int(time.time())
        payload = f'{name}:{ts}'
        token = hmac.new(self.master_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        full_token = f'{name}:{ts}:{token}'
        self.agent_keys[name] = {'token': full_token, 'created': ts}
        self.audit.log('AGENT_REGISTER', name, 'register', 'SUCCESS')
        return full_token

    def verify(self, auth, ip):
        if ip in self.blocked_ips:
            return False, 'BLOCKED'
        if not auth:
            return False, 'NO_AUTH'
        try:
            parts = auth.replace('Bearer ', '').split(':')
            name, ts, token = parts[0], parts[1], parts[2]
            payload = f'{name}:{ts}'
            expected = hmac.new(self.master_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
            if hmac.compare_digest(token, expected):
                self.audit.log('AUTH_SUCCESS', name, 'verify', 'SUCCESS', {'ip': ip})
                return True, name
            return False, 'INVALID'
        except:
            return False, 'INVALID'


# ═══════════════════════════════════════════════════════════════════════════════
# 0r8 BRAIN — UNIFIED SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class Brain0r8:
    """
    The 0r8 Brain — Complete Operating System

    Combines:
    - 3i-ATLAS routing
    - Security layers (Gate, Audit, Cost, Encryption, Validation, Backup)
    - Grimoire pattern learning
    - Performance compounding
    """

    def __init__(self):
        # Generate master key
        self.master_key = secrets.token_hex(32)

        # Initialize security layers
        self.encryption = Encryption()
        self.validator = PatternValidator()
        self.backup = BackupSystem()
        self.audit = AuditLog()
        self.costs = CostTracker(daily_budget=10.0)
        self.gate = Gate(self.master_key, self.audit)

        # Initialize 3i-ATLAS
        self.atlas = ThreeIAtlas()

        # System state
        self.agents = {}
        self.cycles = 0
        self.performance = 1.0

        # Log startup
        print(f'\n🔐 MASTER KEY: {self.master_key}\n   SAVE THIS!\n')
        self.audit.log('SYSTEM_START', 'BRAIN', 'startup', 'ONLINE', {
            'encryption': self.encryption.enabled,
            'version': '3i-1.0.0'
        })

    def register(self, name):
        token = self.gate.create_token(name)
        self.agents[name] = {'registered': time.time()}
        return token

    def compound(self, agent):
        """Performance compounding — each cycle makes the system better"""
        self.performance *= 1.01
        self.cycles += 1
        self.audit.log('COMPOUND', agent, 'compound', 'SUCCESS', {
            'cycle': self.cycles,
            'performance': self.performance
        })

        if self.cycles % 10 == 0:
            self._auto_backup(agent)

        return self.performance

    def _auto_backup(self, agent):
        data = {
            'atlas': {
                'harmonies': {uid: h.to_dict() for uid, h in self.atlas.user_harmonies.items()}
            },
            'cycles': self.cycles,
            'performance': self.performance
        }
        filepath = self.backup.backup(data, '0r8-brain')
        self.audit.log('AUTO_BACKUP', agent, 'backup', 'SUCCESS', {'file': filepath})
        return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title='0r8 Brain — 3i Architecture',
    description='The Operating System for Human Potential',
    version='3i-1.0.0'
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

brain = Brain0r8()


# Request Models
class RegisterRequest(BaseModel):
    agent_name: str
    master_key: str


class RouteRequest(BaseModel):
    user_id: str
    message: str
    mode: Optional[str] = None
    domain: Optional[str] = None
    demigod: Optional[str] = None
    historical_flavor: Optional[str] = None
    custom_weights: Optional[Dict] = None


class MessageRequest(BaseModel):
    text: str


# Endpoints
@app.get('/')
def root():
    return {
        'name': '0r8 Brain',
        'tagline': 'The Operating System for Human Potential',
        'version': '3i-1.0.0',
        'status': 'ONLINE',
        'cycles': brain.cycles,
        'performance': f'{brain.performance:.4f}x',
        'pillars': {
            'nous': '☿ Mercury — Intelligence',
            'anima': '🜍 Sulfur — Intuition',
            'holos': '🜔 Salt — Integration'
        },
        'demigods': list(DEMIGODS.keys()),
        'domains': list(DOMAINS.keys()),
        'security': {
            'gate': 'ACTIVE',
            'audit_log': 'RECORDING',
            'cost_tracking': 'MONITORING',
            'encryption': 'ENABLED' if brain.encryption.enabled else 'DISABLED'
        }
    }


@app.post('/register')
@limiter.limit('5/minute')
def register(r: RegisterRequest, request: Request):
    if r.master_key != brain.master_key:
        raise HTTPException(403, 'Invalid key')
    return {'agent': r.agent_name, 'token': brain.register(r.agent_name)}


@app.post('/route')
@limiter.limit('100/minute')
def route(r: RouteRequest, request: Request, authorization: str = Header(None)):
    """Route a request through the 3i system"""
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, f'Denied: {agent}')

    # Validate message
    valid, reason = brain.validator.validate(r.message)
    if not valid:
        raise HTTPException(400, f'Invalid message: {reason}')

    # Parse mode
    mode = None
    if r.mode:
        try:
            mode = ProcessingMode(r.mode.lower())
        except ValueError:
            pass

    # Route through 3i-ATLAS
    routing = brain.atlas.route(
        user_id=r.user_id,
        message=r.message,
        mode=mode,
        domain=r.domain,
        demigod=r.demigod,
        historical_flavor=r.historical_flavor,
        custom_weights=r.custom_weights
    )

    brain.audit.log('ROUTE', agent, '3i-routing', 'SUCCESS', {
        'user_id': r.user_id,
        'demigod': routing['demigod']['name'],
        'pillar': routing['dominant_pillar']
    })

    return routing


@app.get('/demigods')
def list_demigods():
    """List all demigods"""
    return {
        name: {
            'name': d.name,
            'pillar': d.pillar.value,
            'domain': d.domain,
            'specialty': d.specialty,
            'symbol': d.symbol
        }
        for name, d in DEMIGODS.items()
    }


@app.get('/demigods/{name}')
def get_demigod(name: str):
    """Get a specific demigod"""
    if name not in DEMIGODS:
        raise HTTPException(404, f'Demigod not found: {name}')
    d = DEMIGODS[name]
    return {
        'name': d.name,
        'pillar': d.pillar.value,
        'domain': d.domain,
        'specialty': d.specialty,
        'voice': d.voice,
        'symbol': d.symbol,
        'default_weights': d.default_weights.to_dict()
    }


@app.get('/domains')
def list_domains():
    """List all life domains"""
    return {
        name: {
            'name': d.name,
            'icon': d.icon,
            'description': d.description,
            'suggested_demigods': d.suggested_demigods,
            'default_weights': d.default_weights.to_dict()
        }
        for name, d in DOMAINS.items()
    }


@app.get('/flavors')
def list_flavors():
    """List historical flavors"""
    return {
        name: {
            'name': f.name,
            'essence': f.essence,
            'era': f.era,
            'weights': f.weights.to_dict()
        }
        for name, f in HISTORICAL_FLAVORS.items()
    }


@app.get('/modules')
def list_modules():
    """List all 9 AGI modules organized by pillar"""
    return {
        'pillars': {
            'nous': {
                'symbol': '☿',
                'name': 'Mercury - Intelligence',
                'color': '#00D4FF',
                'modules': [m.to_dict() for m in NOUS_MODULES]
            },
            'anima': {
                'symbol': '🜍',
                'name': 'Sulfur - Intuition',
                'color': '#8B5CF6',
                'modules': [m.to_dict() for m in ANIMA_MODULES]
            },
            'holos': {
                'symbol': '🜔',
                'name': 'Salt - Integration',
                'color': '#F59E0B',
                'modules': [m.to_dict() for m in HOLOS_MODULES]
            }
        },
        'total_modules': 9,
        'architecture': '3i-ATLAS',
        'axiom': '0r8 = Transmutation Engine'
    }


@app.get('/modules/{module_name}')
def get_module(module_name: str):
    """Get a specific AGI module"""
    if module_name not in AGI_MODULES:
        raise HTTPException(404, f'Module not found: {module_name}')
    return AGI_MODULES[module_name].to_dict()


@app.get('/harmony/{user_id}')
@limiter.limit('30/minute')
def get_harmony(user_id: str, request: Request, authorization: str = Header(None)):
    """Get a user's 3i harmony profile"""
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')

    harmony = brain.atlas.get_or_create_harmony(user_id)
    return harmony.to_dict()


@app.post('/compound')
@limiter.limit('10/minute')
def compound(request: Request, authorization: str = Header(None)):
    """Trigger performance compounding"""
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    return {'cycle': brain.cycles, 'performance': f'{brain.compound(agent):.4f}x'}


@app.get('/stats')
@limiter.limit('30/minute')
def stats(request: Request, authorization: str = Header(None)):
    """Get system statistics"""
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    return {
        'performance': f'{brain.performance:.4f}x',
        'cycles': brain.cycles,
        'agents': list(brain.agents.keys()),
        'budget': brain.costs.check_budget(),
        'user_count': len(brain.atlas.user_harmonies),
        'encryption_enabled': brain.encryption.enabled
    }


@app.get('/audit')
@limiter.limit('20/minute')
def get_audit(request: Request, limit: int = 100, authorization: str = Header(None)):
    """Get audit logs"""
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    logs = brain.audit.recent(limit)
    return {'logs': logs, 'count': len(logs)}


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('''
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║           ☿                                                                   ║
║            ╲                                                                  ║
║             ╲                                                                 ║
║        🜍 ═══ ☉ ═══ 🜔                                                        ║
║             ╱                                                                 ║
║            ╱                                                                  ║
║                                                                               ║
║                              0 r 8                                            ║
║                                                                               ║
║            THE OPERATING SYSTEM FOR HUMAN POTENTIAL                           ║
║                                                                               ║
║         Intelligence  ·  Intuition  ·  Integration                            ║
║                                                                               ║
║                         I₁ + I₂ = I₃                                          ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  PILLARS                                                                      ║
║  ────────────────────────────────────────────────────────────────────────     ║
║  ☿ NOUS   — The Mind   — Mercury  — Intelligence                              ║
║  🜍 ANIMA  — The Soul   — Sulfur   — Intuition                                 ║
║  🜔 HOLOS  — The Whole  — Salt     — Integration                               ║
║                                                                               ║
║  DEMIGODS                                                                     ║
║  ────────────────────────────────────────────────────────────────────────     ║
║  Athena · Mercury · Hephaestus · Apollo · Artemis · Hermes · Ares             ║
║                                                                               ║
║  DOMAINS                                                                      ║
║  ────────────────────────────────────────────────────────────────────────     ║
║  Work · School · Sports · Create · Spiritual · Social · Health · Life         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Built by one. Owned by all. Everybody eats.                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
''')
    print(f'🔒 Encryption: {"ENABLED" if brain.encryption.enabled else "DISABLED"}')
    print(f'💰 Daily Budget: ${brain.costs.daily_budget}')
    print()
    print('📊 http://127.0.0.1:3000')
    print('📖 http://127.0.0.1:3000/docs')
    print()
    uvicorn.run(app, host='0.0.0.0', port=3000)
