"""
FlowSync Client — The main interface to 0r8 Brain
"""

import json
from typing import Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .types import (
    RouteRequest,
    RouteResponse,
    Demigod,
    Domain,
    GovernanceStatus,
    AgentFingerprint,
    ThreeIWeights,
)


class FlowSyncError(Exception):
    """Base exception for FlowSync SDK"""
    pass


class AuthenticationError(FlowSyncError):
    """Authentication failed"""
    pass


class RateLimitError(FlowSyncError):
    """Rate limit exceeded"""
    pass


class FlowSync:
    """
    FlowSync SDK Client

    The main interface to the 0r8 Brain API.
    Route messages through 3i-ATLAS, summon Demigods, and harness the power
    of Intelligence, Intuition, and Integration.

    Usage:
        client = FlowSync(api_key="your-api-key")
        response = client.route(
            user_id="user-123",
            message="Help me analyze this data",
            mode="analyst",
            demigod="athena"
        )
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://127.0.0.1:3000",
        timeout: int = 30
    ):
        """
        Initialize the FlowSync client.

        Args:
            api_key: Your 0r8 API key (agent token)
            base_url: The 0r8 Brain API URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """Make an authenticated request to the API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        body = json.dumps(data).encode("utf-8") if data else None
        req = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 403:
                raise AuthenticationError(f"Authentication failed: {e.reason}")
            elif e.code == 429:
                raise RateLimitError(f"Rate limit exceeded: {e.reason}")
            else:
                raise FlowSyncError(f"API error ({e.code}): {e.reason}")
        except URLError as e:
            raise FlowSyncError(f"Connection error: {e.reason}")

    def _get(self, endpoint: str) -> Dict:
        """GET request"""
        return self._request("GET", endpoint)

    def _post(self, endpoint: str, data: Dict) -> Dict:
        """POST request"""
        return self._request("POST", endpoint, data)

    # ═══════════════════════════════════════════════════════════════
    # CORE ROUTING
    # ═══════════════════════════════════════════════════════════════

    def route(
        self,
        user_id: str,
        message: str,
        mode: Optional[str] = None,
        domain: Optional[str] = None,
        demigod: Optional[str] = None,
        historical_flavor: Optional[str] = None,
        custom_weights: Optional[Dict] = None
    ) -> RouteResponse:
        """
        Route a message through 3i-ATLAS.

        This is the core method for interacting with 0r8. It determines:
        - Which Demigod should handle the request
        - What 3i weights to apply
        - What temperature and model tier to use
        - Which AGI modules to activate

        Args:
            user_id: Unique user identifier
            message: The message to route
            mode: Processing mode (analyst, creator, executor, sage, transcendent)
            domain: Life domain (work, school, sports, create, spiritual, social, health, life)
            demigod: Specific demigod to use (athena, mercury, hephaestus, apollo, artemis, hermes, ares)
            historical_flavor: Historical figure flavor (leonardo, tesla, jobs, sun_tzu, rumi, etc.)
            custom_weights: Custom 3i weights dict (nous, anima, holos)

        Returns:
            RouteResponse with routing configuration
        """
        request = RouteRequest(
            user_id=user_id,
            message=message,
            mode=mode,
            domain=domain,
            demigod=demigod,
            historical_flavor=historical_flavor,
            custom_weights=custom_weights
        )

        response = self._post("/route", request.to_dict())
        return RouteResponse.from_dict(response)

    def quick_route(self, message: str, mode: str = "sage") -> RouteResponse:
        """
        Quick routing for simple use cases.
        Uses a default user ID and specified mode.
        """
        return self.route(
            user_id="quick-user",
            message=message,
            mode=mode
        )

    # ═══════════════════════════════════════════════════════════════
    # DEMIGODS
    # ═══════════════════════════════════════════════════════════════

    def list_demigods(self) -> Dict[str, Dict]:
        """List all available Demigods"""
        return self._get("/demigods")

    def get_demigod(self, name: str) -> Dict:
        """Get details for a specific Demigod"""
        return self._get(f"/demigods/{name}")

    # ═══════════════════════════════════════════════════════════════
    # DOMAINS
    # ═══════════════════════════════════════════════════════════════

    def list_domains(self) -> Dict[str, Dict]:
        """List all life domains"""
        return self._get("/domains")

    # ═══════════════════════════════════════════════════════════════
    # AGI MODULES
    # ═══════════════════════════════════════════════════════════════

    def list_modules(self) -> Dict:
        """List all 9 AGI modules organized by pillar"""
        return self._get("/modules")

    def get_module(self, name: str) -> Dict:
        """Get details for a specific AGI module"""
        return self._get(f"/modules/{name}")

    # ═══════════════════════════════════════════════════════════════
    # HISTORICAL FLAVORS
    # ═══════════════════════════════════════════════════════════════

    def list_flavors(self) -> Dict[str, Dict]:
        """List all historical flavors"""
        return self._get("/flavors")

    # ═══════════════════════════════════════════════════════════════
    # USER HARMONY
    # ═══════════════════════════════════════════════════════════════

    def get_harmony(self, user_id: str) -> Dict:
        """Get a user's 3i harmony profile"""
        return self._get(f"/harmony/{user_id}")

    # ═══════════════════════════════════════════════════════════════
    # GOVERNANCE
    # ═══════════════════════════════════════════════════════════════

    def governance_status(self) -> GovernanceStatus:
        """Get governance system status"""
        response = self._get("/governance")
        return GovernanceStatus.from_dict(response)

    def register_agent(self, agent_id: str, name: str) -> AgentFingerprint:
        """Register a new agent with fingerprint"""
        response = self._post("/governance/agents", {
            "agent_id": agent_id,
            "name": name
        })
        return AgentFingerprint.from_dict(response.get("fingerprint", {}))

    def get_agent_fingerprint(self, agent_id: str) -> AgentFingerprint:
        """Get an agent's fingerprint"""
        response = self._get(f"/governance/agents/{agent_id}")
        return AgentFingerprint.from_dict(response)

    def request_authorization(
        self,
        action_id: str,
        action_type: str,
        risk_level: str,
        agent_id: str
    ) -> Dict:
        """Request authorization for an action"""
        return self._post("/governance/authorize", {
            "action_id": action_id,
            "action_type": action_type,
            "risk_level": risk_level,
            "agent_id": agent_id
        })

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get agent leaderboard by alignment score"""
        response = self._get(f"/governance/leaderboard?limit={limit}")
        return response.get("leaderboard", [])

    # ═══════════════════════════════════════════════════════════════
    # SYSTEM
    # ═══════════════════════════════════════════════════════════════

    def status(self) -> Dict:
        """Get system status (no auth required)"""
        url = f"{self.base_url}/"
        req = Request(url)
        try:
            with urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            raise FlowSyncError(f"Failed to get status: {e}")

    def stats(self) -> Dict:
        """Get system statistics"""
        return self._get("/stats")
