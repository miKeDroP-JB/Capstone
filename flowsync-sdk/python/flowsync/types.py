"""
FlowSync Type Definitions
The 0r8 3i Architecture type system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from enum import Enum


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


class CompetenceLevel(Enum):
    """Agent competence levels"""
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    MASTER = "master"


class RiskLevel(Enum):
    """Risk classification for actions"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThreeIWeights:
    """3i Weight Configuration"""
    nous: float = 0.33      # I₁ — Intelligence
    anima: float = 0.33     # I₂ — Intuition
    holos: float = 0.34     # I₃ — Integration

    def to_dict(self) -> Dict:
        return {"nous": self.nous, "anima": self.anima, "holos": self.holos}

    @classmethod
    def from_dict(cls, data: Dict) -> 'ThreeIWeights':
        return cls(
            nous=data.get("nous", 0.33),
            anima=data.get("anima", 0.33),
            holos=data.get("holos", 0.34)
        )

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


@dataclass
class Demigod:
    """A Demigod persona"""
    id: str
    name: str
    pillar: Pillar
    domain: str
    specialty: str
    voice: str
    symbol: str
    default_weights: ThreeIWeights

    @classmethod
    def from_dict(cls, data: Dict) -> 'Demigod':
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            pillar=Pillar(data.get("pillar", "nous")),
            domain=data.get("domain", ""),
            specialty=data.get("specialty", ""),
            voice=data.get("voice", ""),
            symbol=data.get("symbol", ""),
            default_weights=ThreeIWeights.from_dict(data.get("default_weights", {}))
        )


@dataclass
class Domain:
    """A life domain"""
    id: str
    name: str
    icon: str
    description: str
    default_weights: ThreeIWeights
    suggested_demigods: List[str]

    @classmethod
    def from_dict(cls, data: Dict) -> 'Domain':
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            icon=data.get("icon", ""),
            description=data.get("description", ""),
            default_weights=ThreeIWeights.from_dict(data.get("default_weights", {})),
            suggested_demigods=data.get("suggested_demigods", [])
        )


@dataclass
class RouteRequest:
    """Request to route through 3i-ATLAS"""
    user_id: str
    message: str
    mode: Optional[str] = None
    domain: Optional[str] = None
    demigod: Optional[str] = None
    historical_flavor: Optional[str] = None
    custom_weights: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "message": self.message,
            "mode": self.mode,
            "domain": self.domain,
            "demigod": self.demigod,
            "historical_flavor": self.historical_flavor,
            "custom_weights": self.custom_weights
        }


@dataclass
class TransmutationStage:
    """A stage in the Transmutation Cascade"""
    stage: int
    name: str
    description: str
    processor: str
    intensity: Optional[float] = None
    status: str = "complete"


@dataclass
class RouteResponse:
    """Response from 3i-ATLAS routing"""
    weights: ThreeIWeights
    dominant_pillar: str
    demigod: Dict
    historical_flavor: Optional[str]
    temperature: float
    model_tier: str
    user_harmony: Dict
    domain_context: Optional[str]
    active_modules: Dict
    transmutation: Dict
    community: Dict

    @classmethod
    def from_dict(cls, data: Dict) -> 'RouteResponse':
        return cls(
            weights=ThreeIWeights.from_dict(data.get("weights", {})),
            dominant_pillar=data.get("dominant_pillar", ""),
            demigod=data.get("demigod", {}),
            historical_flavor=data.get("historical_flavor"),
            temperature=data.get("temperature", 0.7),
            model_tier=data.get("model_tier", "standard"),
            user_harmony=data.get("user_harmony", {}),
            domain_context=data.get("domain_context"),
            active_modules=data.get("active_modules", {}),
            transmutation=data.get("transmutation", {}),
            community=data.get("community", {})
        )


@dataclass
class AgentFingerprint:
    """Agent alignment fingerprint"""
    agent_id: str
    name: str
    alignment_score: float
    competence_level: str
    risk_score: float
    autonomy_ceiling: float
    success_rate: float
    total_actions: int
    flagged_actions: int
    certifications: List[str]
    created_at: str
    last_action: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentFingerprint':
        return cls(
            agent_id=data.get("agent_id", ""),
            name=data.get("name", ""),
            alignment_score=data.get("alignment_score", 0.95),
            competence_level=data.get("competence_level", "novice"),
            risk_score=data.get("risk_score", 0.1),
            autonomy_ceiling=data.get("autonomy_ceiling", 0.5),
            success_rate=data.get("success_rate", 1.0),
            total_actions=data.get("total_actions", 0),
            flagged_actions=data.get("flagged_actions", 0),
            certifications=data.get("certifications", []),
            created_at=data.get("created_at", ""),
            last_action=data.get("last_action")
        )


@dataclass
class GovernanceStatus:
    """Governance system status"""
    total_keys: int
    active_keys: int
    total_agents: int
    pending_votes: int
    executed_actions: int
    keys_by_type: Dict[str, int]

    @classmethod
    def from_dict(cls, data: Dict) -> 'GovernanceStatus':
        return cls(
            total_keys=data.get("total_keys", 0),
            active_keys=data.get("active_keys", 0),
            total_agents=data.get("total_agents", 0),
            pending_votes=data.get("pending_votes", 0),
            executed_actions=data.get("executed_actions", 0),
            keys_by_type=data.get("keys_by_type", {})
        )
