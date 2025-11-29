#!/usr/bin/env python3
"""
0RB_AETHER Unified Pipeline
Complete flow: Voice Auth -> Brain -> AI Provider -> Response

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import asyncio
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from brain_bridge import UnifiedBrain, ParsedIntent, IntentCategory
from ai_connectors import AIOrchestrator as AIConnectorOrchestrator

# API Key check helpers
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GPT_API_KEY = os.getenv("OPENAI_API_KEY")


class PipelineStage(Enum):
    """Pipeline processing stages"""
    VOICE_INPUT = "voice_input"
    VOICE_AUTH = "voice_auth"
    INTENT_PARSE = "intent_parse"
    CONFIDENCE_CHECK = "confidence_check"
    AI_ROUTING = "ai_routing"
    AI_PROCESSING = "ai_processing"
    RESPONSE = "response"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class PipelineContext:
    """Context passed through pipeline stages"""
    request_id: str
    raw_input: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Authentication
    voice_verified: bool = False
    auth_token: Optional[str] = None
    agent_id: Optional[str] = None

    # Intent
    intent: Optional[ParsedIntent] = None
    intent_source: str = ""

    # Routing
    provider: str = ""
    requires_confirmation: bool = False

    # AI Response
    ai_response: str = ""
    ai_cost: float = 0.0
    tokens_used: int = 0

    # Meta
    current_stage: PipelineStage = PipelineStage.VOICE_INPUT
    errors: List[str] = field(default_factory=list)
    trace: List[Dict] = field(default_factory=list)

    def add_trace(self, stage: str, data: Dict):
        """Add trace entry"""
        self.trace.append({
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            **data
        })


class VoiceAuthenticator:
    """
    Voice authentication handler.
    In production, integrates with voice_auth.py module.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.similarity_threshold = config.get("speaker_similarity_threshold", 0.75)
        self._enrolled_speakers: Dict[str, Any] = {}
        self._demo_mode = config.get("simulate_voice", True)

    async def authenticate(self, audio_data: bytes = None) -> tuple[bool, str, float]:
        """
        Authenticate speaker from audio.
        Returns (success, speaker_id, confidence)
        """
        if self._demo_mode:
            # Demo mode - always succeed
            return True, "demo_user", 0.95

        # Real authentication would use voice_auth.py pipeline:
        # 1. VAD (Voice Activity Detection)
        # 2. ASR (Speech Recognition via Whisper)
        # 3. Speaker Verification (pyannote embeddings)

        try:
            # Import voice auth module
            voice_auth_path = Path("./0rb-aether/tools/asr/voice_auth.py")
            if voice_auth_path.exists():
                # In production: Use actual voice verification
                pass

            return False, "", 0.0

        except Exception as e:
            print(f"[VoiceAuth] Error: {e}")
            return False, "", 0.0

    async def verify_passphrase(self, transcription: str, expected_hash: str) -> bool:
        """Verify spoken passphrase matches expected"""
        spoken_hash = hashlib.sha256(transcription.lower().strip().encode()).hexdigest()
        return spoken_hash == expected_hash


class PipelineAIOrchestrator:
    """
    Orchestrates AI provider calls with cost tracking.
    Wraps AIConnectorOrchestrator for pipeline integration.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self._orchestrator = AIConnectorOrchestrator()
        self.daily_budget = config.get("daily_budget", 10.0)
        self.daily_spent = 0.0

    async def call_provider(
        self,
        provider: str,
        prompt: str,
        system_prompt: str = None
    ) -> tuple[str, float, int]:
        """
        Call AI provider and return response with cost.
        Returns (response, cost, tokens)
        """
        # Check if any providers are configured
        config_status = self._orchestrator.check_config()

        try:
            # Use the orchestrator's generate method
            task_type = self._infer_task_type(prompt)
            complexity = 0.5

            # Prepend system context if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"Context: {system_prompt}\n\nUser request: {prompt}"

            result = await self._orchestrator.generate(
                full_prompt,
                task_type=task_type,
                complexity=complexity,
                max_tokens=1024
            )

            if result.get("success"):
                content = result.get("content", "")
                cost = result.get("cost", 0.0)
                tokens = result.get("tokens_used", 0)
                self.daily_spent += cost
                return content, cost, tokens
            else:
                # API error or not configured
                return await self._fallback_response(prompt)

        except Exception as e:
            print(f"[PipelineAIOrchestrator] Error: {e}")
            return await self._fallback_response(prompt)

    def _infer_task_type(self, prompt: str) -> str:
        """Infer task type from prompt"""
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["build", "create", "develop"]):
            return "strategy"
        elif any(word in prompt_lower for word in ["code", "function", "script"]):
            return "code"
        elif any(word in prompt_lower for word in ["analyze", "research", "investigate"]):
            return "research"
        elif any(word in prompt_lower for word in ["summarize", "brief", "explain"]):
            return "simple"
        return "general"

    def _default_system_prompt(self) -> str:
        """Default system prompt for AI providers"""
        return """You are 0RB_AETHER, an AI assistant running in a secure, encrypted environment.
You help users with:
- Building enterprise solutions (B2B - eKo.vision)
- Creating consumer applications (B2C - 0r8.ai)
- Security analysis and auditing
- Code development and review

Core values: Love - Loyalty - Honor - Everybody Eats

Be concise, secure-minded, and helpful."""

    async def _fallback_response(self, prompt: str) -> tuple[str, float, int]:
        """Fallback response when no API keys available"""
        response = f"[Demo Mode] Processed intent: {prompt[:100]}..."
        return response, 0.0, 0

    def check_budget(self) -> Dict[str, Any]:
        """Check daily budget status"""
        remaining = self.daily_budget - self.daily_spent
        percent = (self.daily_spent / self.daily_budget) * 100 if self.daily_budget > 0 else 0

        if percent > 90:
            status = "CRITICAL"
        elif percent > 75:
            status = "WARNING"
        elif percent > 50:
            status = "CAUTION"
        else:
            status = "OK"

        return {
            "spent": self.daily_spent,
            "budget": self.daily_budget,
            "remaining": remaining,
            "percent": percent,
            "status": status,
            "providers_configured": self._orchestrator.check_config()
        }


class OrbPipeline:
    """
    Complete 0RB_AETHER processing pipeline.

    Flow:
    Voice/Text Input
        -> Voice Authentication (if voice)
        -> Intent Parsing (Brain Bridge)
        -> Confidence Check
        -> AI Routing
        -> AI Processing
        -> Response + Audit
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.brain = UnifiedBrain(config)
        self.voice_auth = VoiceAuthenticator(config.get("voice_auth", {}))
        self.ai_orchestrator = PipelineAIOrchestrator(config.get("ai", {}))
        self._request_counter = 0
        self._initialized = False

        # Callbacks for each stage
        self._stage_callbacks: Dict[PipelineStage, List[Callable]] = {
            stage: [] for stage in PipelineStage
        }

    async def initialize(self) -> bool:
        """Initialize all pipeline components"""
        await self.brain.initialize()
        self._initialized = True
        return True

    def on_stage(self, stage: PipelineStage, callback: Callable):
        """Register callback for pipeline stage"""
        self._stage_callbacks[stage].append(callback)

    async def _emit_stage(self, ctx: PipelineContext, stage: PipelineStage):
        """Emit stage event to callbacks"""
        ctx.current_stage = stage
        for callback in self._stage_callbacks[stage]:
            try:
                await callback(ctx)
            except Exception as e:
                ctx.errors.append(f"Callback error: {e}")

    async def process(
        self,
        text_input: str = None,
        audio_input: bytes = None,
        auth_token: str = None,
        require_voice_auth: bool = False
    ) -> PipelineContext:
        """
        Process input through complete pipeline.

        Args:
            text_input: Direct text input
            audio_input: Audio bytes for voice processing
            auth_token: Pre-existing auth token
            require_voice_auth: Whether to require voice authentication

        Returns:
            PipelineContext with full processing results
        """
        self._request_counter += 1
        request_id = f"req_{self._request_counter}_{int(time.time())}"

        ctx = PipelineContext(
            request_id=request_id,
            raw_input=text_input or "[audio]",
            auth_token=auth_token
        )

        try:
            # Stage 1: Voice Input / Text Input
            await self._emit_stage(ctx, PipelineStage.VOICE_INPUT)
            ctx.add_trace("input", {
                "type": "audio" if audio_input else "text",
                "length": len(audio_input) if audio_input else len(text_input or "")
            })

            # If audio, transcribe (placeholder - would use Whisper)
            if audio_input:
                text_input = await self._transcribe_audio(audio_input)
                ctx.raw_input = text_input

            if not text_input:
                ctx.errors.append("No input provided")
                ctx.current_stage = PipelineStage.ERROR
                return ctx

            # Stage 2: Voice Authentication
            await self._emit_stage(ctx, PipelineStage.VOICE_AUTH)

            if require_voice_auth or audio_input:
                success, speaker_id, confidence = await self.voice_auth.authenticate(audio_input)
                ctx.voice_verified = success
                ctx.agent_id = speaker_id
                ctx.add_trace("voice_auth", {
                    "verified": success,
                    "speaker": speaker_id,
                    "confidence": confidence
                })

                if not success:
                    ctx.errors.append("Voice authentication failed")
                    ctx.current_stage = PipelineStage.ERROR
                    return ctx
            else:
                ctx.voice_verified = True  # Text input doesn't require voice auth

            # Stage 3: Intent Parsing
            await self._emit_stage(ctx, PipelineStage.INTENT_PARSE)

            intent, source = await self.brain.bridge.parse_intent(text_input)
            ctx.intent = intent
            ctx.intent_source = source
            ctx.add_trace("intent", {
                "category": intent.category.value,
                "action": intent.action,
                "confidence": intent.confidence,
                "source": source
            })

            # Stage 4: Confidence Check
            await self._emit_stage(ctx, PipelineStage.CONFIDENCE_CHECK)

            threshold = self.config.get("brain", {}).get("confidence_threshold", 0.95)
            ctx.requires_confirmation = intent.confidence < threshold
            ctx.add_trace("confidence", {
                "threshold": threshold,
                "intent_confidence": intent.confidence,
                "requires_confirmation": ctx.requires_confirmation
            })

            # Stage 5: AI Routing
            await self._emit_stage(ctx, PipelineStage.AI_ROUTING)

            routing = await self.brain.bridge.route_task(intent)
            ctx.provider = routing.get("provider", "gpt")
            ctx.add_trace("routing", {
                "provider": ctx.provider,
                "reason": routing.get("reason", "default")
            })

            # Stage 6: AI Processing
            await self._emit_stage(ctx, PipelineStage.AI_PROCESSING)

            # Check budget before calling AI
            budget = self.ai_orchestrator.check_budget()
            if budget["status"] == "CRITICAL":
                ctx.errors.append("Daily budget exceeded")
                ctx.ai_response = "Budget limit reached. Please try again tomorrow."
            else:
                response, cost, tokens = await self.ai_orchestrator.call_provider(
                    ctx.provider,
                    text_input
                )
                ctx.ai_response = response
                ctx.ai_cost = cost
                ctx.tokens_used = tokens

            ctx.add_trace("ai_processing", {
                "provider": ctx.provider,
                "cost": ctx.ai_cost,
                "tokens": ctx.tokens_used,
                "response_length": len(ctx.ai_response)
            })

            # Stage 7: Response
            await self._emit_stage(ctx, PipelineStage.RESPONSE)
            ctx.current_stage = PipelineStage.COMPLETE

            return ctx

        except Exception as e:
            ctx.errors.append(str(e))
            ctx.current_stage = PipelineStage.ERROR
            return ctx

    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio to text (placeholder)"""
        # In production, this would use Whisper
        return "[transcribed audio]"

    async def shutdown(self):
        """Shutdown pipeline"""
        await self.brain.shutdown()
        self._initialized = False

    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        return {
            "initialized": self._initialized,
            "requests_processed": self._request_counter,
            "budget": self.ai_orchestrator.check_budget(),
            "brain_connected": self.brain.bridge.connected,
        }


class PipelineMonitor:
    """Monitor pipeline execution and log events"""

    def __init__(self, log_dir: str = "./audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.events: List[Dict] = []

    async def on_stage(self, ctx: PipelineContext):
        """Handle stage events"""
        event = {
            "request_id": ctx.request_id,
            "stage": ctx.current_stage.value,
            "timestamp": datetime.now().isoformat(),
            "errors": ctx.errors,
        }
        self.events.append(event)

        # Log to file
        log_file = self.log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')


# Demo / Test
async def demo():
    """Run pipeline demo"""
    print("\n" + "="*60)
    print("0RB_AETHER Pipeline Demo")
    print("="*60 + "\n")

    # Load config
    config = {
        "voice_auth": {"simulate_voice": True},
        "brain": {"confidence_threshold": 0.95},
        "ai": {"daily_budget": 10.0}
    }

    pipeline = OrbPipeline(config)
    monitor = PipelineMonitor()

    # Register monitor callbacks
    for stage in PipelineStage:
        pipeline.on_stage(stage, monitor.on_stage)

    await pipeline.initialize()

    # Test inputs
    test_cases = [
        "What's the system status?",
        "Build an enterprise voice AI agency solution",
        "Create a fun educational game for kids",
        "Analyze this code for security vulnerabilities",
    ]

    for text in test_cases:
        print(f"\nInput: {text}")
        print("-" * 40)

        ctx = await pipeline.process(text_input=text)

        print(f"  Stage: {ctx.current_stage.value}")
        print(f"  Intent: {ctx.intent.category.value if ctx.intent else 'N/A'}")
        print(f"  Action: {ctx.intent.action if ctx.intent else 'N/A'}")
        print(f"  Confidence: {ctx.intent.confidence:.0%}" if ctx.intent else "N/A")
        print(f"  Provider: {ctx.provider}")
        print(f"  Cost: ${ctx.ai_cost:.6f}")
        print(f"  Response: {ctx.ai_response[:100]}...")

        if ctx.errors:
            print(f"  Errors: {ctx.errors}")

    # Final status
    print("\n" + "="*60)
    print("Pipeline Status")
    print("="*60)
    status = pipeline.get_status()
    print(json.dumps(status, indent=2))

    await pipeline.shutdown()


if __name__ == "__main__":
    asyncio.run(demo())
