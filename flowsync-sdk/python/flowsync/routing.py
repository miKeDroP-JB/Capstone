"""
FlowSync Router — High-level routing utilities
"""

from typing import Dict, List, Optional
from .types import (
    ProcessingMode,
    ThreeIWeights,
    Pillar,
    RouteResponse,
)
from .client import FlowSync


class Router:
    """
    High-level router for common use cases.

    Provides convenient methods for different routing scenarios
    without needing to specify all parameters.
    """

    def __init__(self, client: FlowSync):
        self.client = client

    def analyze(self, user_id: str, message: str) -> RouteResponse:
        """Route for analysis tasks (high NOUS)"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="analyst",
            demigod="athena"
        )

    def create(self, user_id: str, message: str) -> RouteResponse:
        """Route for creative tasks (high ANIMA)"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="creator",
            demigod="apollo"
        )

    def execute(self, user_id: str, message: str) -> RouteResponse:
        """Route for execution tasks (high HOLOS)"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="executor",
            demigod="hermes"
        )

    def code(self, user_id: str, message: str) -> RouteResponse:
        """Route for coding tasks"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="analyst",
            domain="work",
            demigod="hephaestus"
        )

    def strategy(self, user_id: str, message: str) -> RouteResponse:
        """Route for strategic planning"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="analyst",
            domain="work",
            demigod="athena",
            historical_flavor="sun_tzu"
        )

    def innovate(self, user_id: str, message: str) -> RouteResponse:
        """Route for innovation and invention"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="creator",
            demigod="apollo",
            historical_flavor="tesla"
        )

    def integrate(self, user_id: str, message: str) -> RouteResponse:
        """Route for integration and synthesis"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="sage",
            demigod="hermes",
            historical_flavor="leonardo"
        )

    def challenge(self, user_id: str, message: str) -> RouteResponse:
        """Route for competitive challenges"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="executor",
            domain="sports",
            demigod="ares"
        )

    def focus(self, user_id: str, message: str) -> RouteResponse:
        """Route for focused, precision work"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="executor",
            demigod="artemis"
        )

    def communicate(self, user_id: str, message: str) -> RouteResponse:
        """Route for quick communication tasks"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="executor",
            demigod="mercury"
        )

    def transcend(self, user_id: str, message: str) -> RouteResponse:
        """Route with all pillars at maximum (transcendent mode)"""
        return self.client.route(
            user_id=user_id,
            message=message,
            mode="transcendent"
        )

    def for_domain(self, user_id: str, message: str, domain: str) -> RouteResponse:
        """Route optimized for a specific life domain"""
        return self.client.route(
            user_id=user_id,
            message=message,
            domain=domain
        )

    def with_weights(
        self,
        user_id: str,
        message: str,
        nous: float = 0.33,
        anima: float = 0.33,
        holos: float = 0.34
    ) -> RouteResponse:
        """Route with custom 3i weights"""
        return self.client.route(
            user_id=user_id,
            message=message,
            custom_weights={"nous": nous, "anima": anima, "holos": holos}
        )


class DomainRouter:
    """
    Domain-specific routing shortcuts.
    """

    def __init__(self, client: FlowSync, user_id: str):
        self.client = client
        self.user_id = user_id

    def work(self, message: str) -> RouteResponse:
        """Route for work domain"""
        return self.client.route(self.user_id, message, domain="work")

    def school(self, message: str) -> RouteResponse:
        """Route for school/learning domain"""
        return self.client.route(self.user_id, message, domain="school")

    def sports(self, message: str) -> RouteResponse:
        """Route for sports/fitness domain"""
        return self.client.route(self.user_id, message, domain="sports")

    def create(self, message: str) -> RouteResponse:
        """Route for creative domain"""
        return self.client.route(self.user_id, message, domain="create")

    def spiritual(self, message: str) -> RouteResponse:
        """Route for spiritual domain"""
        return self.client.route(self.user_id, message, domain="spiritual")

    def social(self, message: str) -> RouteResponse:
        """Route for social domain"""
        return self.client.route(self.user_id, message, domain="social")

    def health(self, message: str) -> RouteResponse:
        """Route for health domain"""
        return self.client.route(self.user_id, message, domain="health")

    def life(self, message: str) -> RouteResponse:
        """Route for general life domain"""
        return self.client.route(self.user_id, message, domain="life")
