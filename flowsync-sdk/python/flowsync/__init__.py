"""
FlowSync SDK — The 0r8 Developer Interface
Route through the 3i-ATLAS. Summon Demigods. Build the future.

Usage:
    from flowsync import FlowSync

    client = FlowSync(api_key="your-api-key")
    response = client.route(
        message="Help me build a business plan",
        mode="analyst",
        domain="work",
        demigod="athena"
    )
"""

from .client import FlowSync
from .types import (
    Pillar,
    ProcessingMode,
    ThreeIWeights,
    Demigod,
    Domain,
    RouteRequest,
    RouteResponse,
    GovernanceStatus,
    AgentFingerprint,
)
from .routing import Router
from .demigods import DemigodSelector

__version__ = "0.1.0"
__all__ = [
    "FlowSync",
    "Router",
    "DemigodSelector",
    "Pillar",
    "ProcessingMode",
    "ThreeIWeights",
    "Demigod",
    "Domain",
    "RouteRequest",
    "RouteResponse",
    "GovernanceStatus",
    "AgentFingerprint",
]
