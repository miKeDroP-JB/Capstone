#!/usr/bin/env python3
"""
0RB_AETHER Brain Bridge
Connects Python Brain OS to Rust Brain Orchestrator via Unix socket.

Provides:
- Async communication with Rust brain
- Fallback to Python-only operation
- Intent parsing and routing
- Health monitoring

Love - Loyalty - Honor - Everybody Eats
"""
import os
import json
import socket
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class IntentCategory(Enum):
    """Intent categories matching Rust brain"""
    SYSTEM = "system"
    NETWORK = "network"
    AGENT = "agent"
    DEVELOPER = "developer"
    SECURITY = "security"
    QUERY = "query"
    BUILD = "build"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """Parsed intent result"""
    category: IntentCategory
    action: str
    confidence: float
    parameters: Dict[str, Any]
    raw_text: str
    provider_hint: Optional[str] = None


class PythonIntentParser:
    """
    Fallback Python-based intent parser.
    Mirrors Rust implementation for consistency.
    """

    def __init__(self):
        self.patterns = {
            IntentCategory.SYSTEM: [
                (r'\b(status|health|check|running)\b', 'status', 0.85),
                (r'\b(shutdown|stop|halt|exit)\b', 'shutdown', 0.90),
                (r'\b(restart|reboot|reload)\b', 'restart', 0.88),
                (r'\b(config|settings|configure)\b', 'configure', 0.82),
            ],
            IntentCategory.NETWORK: [
                (r'\b(fetch|download|request|get url)\b', 'fetch', 0.80),
                (r'\b(connect|network|online)\b', 'connect', 0.75),
                (r'\b(disconnect|offline|block)\b', 'disconnect', 0.85),
            ],
            IntentCategory.AGENT: [
                (r'\b(spawn|create|new) (agent|assistant|bot)\b', 'spawn', 0.88),
                (r'\b(list|show) agents?\b', 'list', 0.85),
                (r'\b(kill|terminate|stop) agent\b', 'terminate', 0.90),
            ],
            IntentCategory.DEVELOPER: [
                (r'\b(build|compile|make)\b', 'build', 0.82),
                (r'\b(test|run tests?)\b', 'test', 0.85),
                (r'\b(debug|trace|profile)\b', 'debug', 0.80),
                (r'\b(deploy|release|publish)\b', 'deploy', 0.83),
            ],
            IntentCategory.SECURITY: [
                (r'\b(encrypt|secure|protect)\b', 'encrypt', 0.85),
                (r'\b(decrypt|unlock|access)\b', 'decrypt', 0.85),
                (r'\b(audit|scan|check security)\b', 'audit', 0.88),
                (r'\b(wipe|erase|destroy)\b', 'wipe', 0.95),
            ],
            IntentCategory.BUILD: [
                (r'\b(build|create|make) .*?(app|system|project|solution)\b', 'build', 0.85),
                (r'\b(enterprise|corporate|b2b)\b', 'enterprise_build', 0.82),
                (r'\b(game|playground|consumer|b2c)\b', 'consumer_build', 0.82),
            ],
            IntentCategory.QUERY: [
                (r'\b(what|how|why|when|where|who|explain)\b', 'query', 0.70),
                (r'\b(analyze|research|investigate)\b', 'analyze', 0.78),
                (r'\b(summarize|brief|tldr)\b', 'summarize', 0.80),
            ],
        }

        # Provider hints based on task type
        self.provider_hints = {
            'build': 'claude',
            'enterprise_build': 'claude',
            'consumer_build': 'claude',
            'analyze': 'gemini',
            'research': 'gemini',
            'query': 'gpt',
            'summarize': 'gpt',
        }

    def parse(self, text: str) -> ParsedIntent:
        """Parse text into intent"""
        text_lower = text.lower()
        best_match = None
        best_confidence = 0.0

        for category, patterns in self.patterns.items():
            for pattern, action, base_confidence in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Adjust confidence based on match quality
                    confidence = base_confidence
                    if match.group(0) == text_lower.strip():
                        confidence = min(0.98, confidence + 0.1)

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = (category, action, confidence)

        if best_match:
            category, action, confidence = best_match
            return ParsedIntent(
                category=category,
                action=action,
                confidence=confidence,
                parameters=self._extract_params(text, category),
                raw_text=text,
                provider_hint=self.provider_hints.get(action)
            )

        # Default to query
        return ParsedIntent(
            category=IntentCategory.QUERY,
            action="query",
            confidence=0.50,
            parameters={},
            raw_text=text,
            provider_hint="gpt"
        )

    def _extract_params(self, text: str, category: IntentCategory) -> Dict[str, Any]:
        """Extract parameters from text based on category"""
        params = {}

        # Extract quoted strings
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            params["quoted_values"] = quoted

        # Extract URLs
        urls = re.findall(r'https?://\S+', text)
        if urls:
            params["urls"] = urls

        # Extract file paths
        paths = re.findall(r'[./]\S+\.\w+', text)
        if paths:
            params["paths"] = paths

        return params


class BrainBridge:
    """
    Bridge connecting Python Brain OS to Rust Brain Orchestrator.
    Falls back to Python-only processing if Rust brain unavailable.
    """

    def __init__(
        self,
        socket_path: str = "/run/0rb/brain.sock",
        timeout: float = 5.0
    ):
        self.socket_path = socket_path
        self.timeout = timeout
        self._socket: Optional[socket.socket] = None
        self._connected = False
        self._request_id = 0
        self._fallback_parser = PythonIntentParser()

        # Stats
        self.stats = {
            "rust_requests": 0,
            "rust_successes": 0,
            "fallback_uses": 0,
            "total_intents": 0,
        }

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> bool:
        """Connect to Rust brain via Unix socket"""
        try:
            if self._socket:
                self._socket.close()

            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.setblocking(False)
            self._socket.settimeout(self.timeout)

            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.sock_connect(self._socket, self.socket_path),
                timeout=self.timeout
            )

            self._connected = True
            return True

        except (FileNotFoundError, ConnectionRefusedError):
            self._connected = False
            return False
        except asyncio.TimeoutError:
            self._connected = False
            return False
        except Exception as e:
            print(f"[BrainBridge] Connection error: {e}")
            self._connected = False
            return False

    async def disconnect(self):
        """Disconnect from Rust brain"""
        if self._socket:
            self._socket.close()
            self._socket = None
        self._connected = False

    async def _send_rpc(self, method: str, params: Dict = None) -> Dict:
        """Send JSON-RPC request to Rust brain"""
        if not self._connected:
            return {"error": "Not connected"}

        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {}
        }

        try:
            loop = asyncio.get_event_loop()
            message = json.dumps(request).encode() + b'\n'

            await asyncio.wait_for(
                loop.sock_sendall(self._socket, message),
                timeout=self.timeout
            )

            data = await asyncio.wait_for(
                loop.sock_recv(self._socket, 65536),
                timeout=self.timeout
            )

            self.stats["rust_requests"] += 1
            response = json.loads(data.decode())

            if "result" in response:
                self.stats["rust_successes"] += 1

            return response

        except asyncio.TimeoutError:
            return {"error": "Request timeout"}
        except Exception as e:
            return {"error": str(e)}

    async def parse_intent(self, text: str) -> Tuple[ParsedIntent, str]:
        """
        Parse intent - uses Rust brain if connected, falls back to Python.
        Returns (ParsedIntent, source) where source is 'rust' or 'python'.
        """
        self.stats["total_intents"] += 1

        # Try Rust brain first
        if self._connected:
            result = await self._send_rpc("parseIntent", {"text": text})
            if "result" in result:
                data = result["result"]
                return ParsedIntent(
                    category=IntentCategory(data.get("category", "unknown")),
                    action=data.get("action", "unknown"),
                    confidence=data.get("confidence", 0.0),
                    parameters=data.get("parameters", {}),
                    raw_text=text,
                    provider_hint=data.get("provider_hint")
                ), "rust"

        # Fallback to Python parser
        self.stats["fallback_uses"] += 1
        return self._fallback_parser.parse(text), "python"

    async def route_task(self, intent: ParsedIntent) -> Dict[str, Any]:
        """
        Route task to appropriate AI provider.
        Uses Rust brain if connected, falls back to Python logic.
        """
        # Try Rust brain
        if self._connected:
            result = await self._send_rpc("routeTask", {
                "category": intent.category.value,
                "action": intent.action,
                "confidence": intent.confidence,
            })
            if "result" in result:
                return result["result"]

        # Python fallback routing
        complexity = 0.5 if intent.confidence > 0.7 else 0.8

        if intent.action in ["build", "enterprise_build", "consumer_build"]:
            return {"provider": "claude", "reason": "Complex build task"}
        elif intent.action in ["analyze", "research"]:
            return {"provider": "gemini", "reason": "Research/analysis task"}
        elif intent.confidence > 0.9:
            return {"provider": "gpt", "reason": "High-confidence simple task"}
        else:
            return {"provider": "claude", "reason": "Default for uncertain intent"}

    async def get_status(self) -> Dict[str, Any]:
        """Get status from Rust brain"""
        if self._connected:
            result = await self._send_rpc("getStatus")
            if "result" in result:
                return {
                    "rust_brain": result["result"],
                    "bridge": self.stats,
                    "connected": True
                }

        return {
            "rust_brain": None,
            "bridge": self.stats,
            "connected": False,
            "fallback_active": True
        }

    async def authorize(self, token: str) -> Tuple[bool, str]:
        """Authorize a request via Rust brain"""
        if self._connected:
            result = await self._send_rpc("authorize", {"token": token})
            if "result" in result:
                return result["result"].get("authorized", False), result["result"].get("agent", "")

        # Python fallback - basic validation
        if token and len(token) > 20:
            return True, "fallback_agent"
        return False, ""

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        return {
            **self.stats,
            "connected": self._connected,
            "socket_path": self.socket_path,
            "rust_success_rate": (
                self.stats["rust_successes"] / max(1, self.stats["rust_requests"])
            ),
            "fallback_rate": (
                self.stats["fallback_uses"] / max(1, self.stats["total_intents"])
            ),
        }


class UnifiedBrain:
    """
    Unified brain interface that coordinates between:
    - Python Brain OS (FastAPI server)
    - Rust Brain Orchestrator (Unix socket)
    - Voice Authentication
    - AI Providers
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.bridge = BrainBridge(
            socket_path=self.config.get("paths", {}).get("socket", "/run/0rb/brain.sock")
        )
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the unified brain"""
        # Try to connect to Rust brain
        if await self.bridge.connect():
            print("[UnifiedBrain] Connected to Rust brain")
        else:
            print("[UnifiedBrain] Rust brain unavailable, using Python fallback")

        self._initialized = True
        return True

    async def process(self, text: str, auth_token: str = None) -> Dict[str, Any]:
        """
        Process input through the full pipeline:
        1. Authorize (if token provided)
        2. Parse intent
        3. Route to AI provider
        4. Return result
        """
        result = {
            "input": text,
            "timestamp": datetime.now().isoformat(),
            "authorized": True,
            "stages": {}
        }

        # Stage 1: Authorization
        if auth_token:
            authorized, agent = await self.bridge.authorize(auth_token)
            result["authorized"] = authorized
            result["agent"] = agent
            if not authorized:
                result["error"] = "Authorization failed"
                return result

        # Stage 2: Parse intent
        intent, source = await self.bridge.parse_intent(text)
        result["stages"]["parse"] = {
            "category": intent.category.value,
            "action": intent.action,
            "confidence": intent.confidence,
            "source": source,
        }

        # Stage 3: Route task
        routing = await self.bridge.route_task(intent)
        result["stages"]["route"] = routing
        result["provider"] = routing.get("provider", "unknown")

        # Stage 4: Confidence check
        threshold = self.config.get("brain", {}).get("confidence_threshold", 0.95)
        result["requires_confirmation"] = intent.confidence < threshold

        return result

    async def get_health(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            "initialized": self._initialized,
            "bridge": await self.bridge.get_status(),
            "timestamp": datetime.now().isoformat(),
        }

    async def shutdown(self):
        """Shutdown the unified brain"""
        await self.bridge.disconnect()
        self._initialized = False


# Demo / Test
async def demo():
    """Run a quick demo"""
    print("\n=== Brain Bridge Demo ===\n")

    brain = UnifiedBrain()
    await brain.initialize()

    test_inputs = [
        "What's the system status?",
        "Build an enterprise voice AI solution",
        "Create a fun learning game for kids",
        "Analyze this code for security vulnerabilities",
        "Shutdown the system",
    ]

    for text in test_inputs:
        result = await brain.process(text)
        print(f"Input: {text}")
        print(f"  Category: {result['stages']['parse']['category']}")
        print(f"  Action: {result['stages']['parse']['action']}")
        print(f"  Confidence: {result['stages']['parse']['confidence']:.0%}")
        print(f"  Provider: {result['provider']}")
        print(f"  Needs Confirm: {result['requires_confirmation']}")
        print()

    health = await brain.get_health()
    print(f"Health: {json.dumps(health, indent=2)}")

    await brain.shutdown()


if __name__ == "__main__":
    asyncio.run(demo())
