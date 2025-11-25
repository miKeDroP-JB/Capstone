"""
FlowSync Demigod Selector — Intelligent Demigod selection utilities
"""

from typing import Dict, List, Optional, Tuple
from .types import Pillar, ProcessingMode, ThreeIWeights


# The 7 Demigods with their attributes
DEMIGODS = {
    # NOUS Pillar (☿ Mercury — Intelligence)
    "athena": {
        "name": "Athena",
        "pillar": Pillar.NOUS,
        "symbol": "🦉",
        "domain": "Strategy & Wisdom",
        "specialty": "Business planning, strategy, analysis, complex problem-solving",
        "keywords": ["strategy", "plan", "analyze", "business", "wisdom", "complex"],
        "default_weights": ThreeIWeights(nous=0.85, anima=0.40, holos=0.70),
    },
    "mercury": {
        "name": "Mercury",
        "pillar": Pillar.NOUS,
        "symbol": "⚡",
        "domain": "Speed & Communication",
        "specialty": "Quick tasks, messaging, efficiency, rapid iteration",
        "keywords": ["quick", "fast", "message", "communicate", "efficient", "rapid"],
        "default_weights": ThreeIWeights(nous=0.80, anima=0.50, holos=0.75),
    },
    "hephaestus": {
        "name": "Hephaestus",
        "pillar": Pillar.NOUS,
        "symbol": "🔨",
        "domain": "Building & Craft",
        "specialty": "Technical work, coding, engineering, systems design",
        "keywords": ["code", "build", "engineer", "technical", "craft", "system"],
        "default_weights": ThreeIWeights(nous=0.90, anima=0.35, holos=0.80),
    },

    # ANIMA Pillar (🜍 Sulfur — Intuition)
    "apollo": {
        "name": "Apollo",
        "pillar": Pillar.ANIMA,
        "symbol": "☀️",
        "domain": "Vision & Light",
        "specialty": "Creative direction, prophecy, arts, music, inspiration",
        "keywords": ["create", "art", "design", "music", "inspire", "vision", "creative"],
        "default_weights": ThreeIWeights(nous=0.50, anima=0.90, holos=0.60),
    },
    "artemis": {
        "name": "Artemis",
        "pillar": Pillar.ANIMA,
        "symbol": "🏹",
        "domain": "Precision & Wild",
        "specialty": "Focus, targeting, independent work, nature, instinct",
        "keywords": ["focus", "target", "hunt", "precise", "independent", "instinct"],
        "default_weights": ThreeIWeights(nous=0.60, anima=0.85, holos=0.55),
    },

    # HOLOS Pillar (🜔 Salt — Integration)
    "hermes": {
        "name": "Hermes",
        "pillar": Pillar.HOLOS,
        "symbol": "🪽",
        "domain": "Execution & Speed",
        "specialty": "Getting things done, delivery, bridging gaps, travel",
        "keywords": ["execute", "ship", "deliver", "done", "bridge", "move"],
        "default_weights": ThreeIWeights(nous=0.65, anima=0.55, holos=0.90),
    },
    "ares": {
        "name": "Ares",
        "pillar": Pillar.HOLOS,
        "symbol": "⚔️",
        "domain": "Action & Courage",
        "specialty": "Bold moves, competition, breakthroughs, challenges",
        "keywords": ["challenge", "compete", "bold", "fight", "breakthrough", "action"],
        "default_weights": ThreeIWeights(nous=0.55, anima=0.60, holos=0.95),
    },
}


class DemigodSelector:
    """
    Intelligent Demigod selection based on message content and context.
    """

    def __init__(self):
        self.demigods = DEMIGODS

    def select(
        self,
        message: str,
        preferred_pillar: Optional[Pillar] = None,
        weights: Optional[ThreeIWeights] = None
    ) -> Tuple[str, Dict]:
        """
        Select the best Demigod for a given message.

        Args:
            message: The message to analyze
            preferred_pillar: Prefer Demigods from this pillar
            weights: 3i weights to consider

        Returns:
            Tuple of (demigod_id, demigod_info)
        """
        message_lower = message.lower()
        scores = {}

        for demigod_id, info in self.demigods.items():
            score = 0

            # Keyword matching
            for keyword in info["keywords"]:
                if keyword in message_lower:
                    score += 2

            # Pillar preference
            if preferred_pillar and info["pillar"] == preferred_pillar:
                score += 3

            # Weight alignment
            if weights:
                dw = info["default_weights"]
                alignment = 1 - (
                    abs(weights.nous - dw.nous) +
                    abs(weights.anima - dw.anima) +
                    abs(weights.holos - dw.holos)
                ) / 3
                score += alignment * 2

            scores[demigod_id] = score

        # Select highest scoring
        best_id = max(scores, key=scores.get)
        return best_id, self.demigods[best_id]

    def select_for_mode(self, mode: ProcessingMode) -> Tuple[str, Dict]:
        """Select best Demigod for a processing mode"""
        mode_demigods = {
            ProcessingMode.ANALYST: "athena",
            ProcessingMode.CREATOR: "apollo",
            ProcessingMode.EXECUTOR: "hermes",
            ProcessingMode.SAGE: "athena",  # Wisdom-focused
            ProcessingMode.TRANSCENDENT: "hermes",  # Integration-focused
        }
        demigod_id = mode_demigods.get(mode, "athena")
        return demigod_id, self.demigods[demigod_id]

    def select_for_task(self, task_type: str) -> Tuple[str, Dict]:
        """Select best Demigod for a task type"""
        task_mapping = {
            # Analysis tasks
            "analyze": "athena",
            "research": "athena",
            "strategy": "athena",
            "plan": "athena",

            # Technical tasks
            "code": "hephaestus",
            "build": "hephaestus",
            "engineer": "hephaestus",
            "debug": "hephaestus",

            # Creative tasks
            "create": "apollo",
            "design": "apollo",
            "art": "apollo",
            "write": "apollo",

            # Focus tasks
            "focus": "artemis",
            "target": "artemis",
            "hunt": "artemis",

            # Execution tasks
            "execute": "hermes",
            "ship": "hermes",
            "deliver": "hermes",

            # Challenge tasks
            "challenge": "ares",
            "compete": "ares",
            "fight": "ares",

            # Quick tasks
            "quick": "mercury",
            "fast": "mercury",
            "message": "mercury",
        }

        demigod_id = task_mapping.get(task_type.lower(), "athena")
        return demigod_id, self.demigods[demigod_id]

    def get_by_pillar(self, pillar: Pillar) -> List[Tuple[str, Dict]]:
        """Get all Demigods for a pillar"""
        return [
            (did, info) for did, info in self.demigods.items()
            if info["pillar"] == pillar
        ]

    def list_all(self) -> Dict[str, Dict]:
        """List all Demigods"""
        return self.demigods
