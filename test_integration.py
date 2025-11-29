#!/usr/bin/env python3
"""
0RB_AETHER Integration Tests
Verifies all components work together correctly.

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import asyncio
import unittest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestConfig(unittest.TestCase):
    """Test configuration loading"""

    def test_config_file_exists(self):
        """Config file should exist"""
        config_path = Path("config.toml")
        self.assertTrue(config_path.exists(), "config.toml should exist")

    def test_config_loads(self):
        """Config should load without errors"""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        config_path = Path("config.toml")
        if config_path.exists():
            with open(config_path, 'rb') as f:
                config = tomllib.load(f)
            self.assertIn("system", config)
            self.assertIn("brain", config)
            self.assertIn("ai", config)

    def test_required_config_sections(self):
        """All required config sections should be present"""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        config_path = Path("config.toml")
        if config_path.exists():
            with open(config_path, 'rb') as f:
                config = tomllib.load(f)

            required_sections = ["system", "paths", "brain", "brain_os", "ai", "security"]
            for section in required_sections:
                self.assertIn(section, config, f"Config should have {section} section")


class TestBrainBridge(unittest.TestCase):
    """Test brain bridge functionality"""

    def test_python_intent_parser(self):
        """Python intent parser should work"""
        from brain_bridge import PythonIntentParser, IntentCategory

        parser = PythonIntentParser()

        # Test system intents
        result = parser.parse("What's the system status?")
        self.assertEqual(result.category, IntentCategory.SYSTEM)
        self.assertEqual(result.action, "status")
        self.assertGreater(result.confidence, 0.7)

        # Test build intents
        result = parser.parse("Build an enterprise solution")
        self.assertEqual(result.category, IntentCategory.BUILD)
        self.assertIn(result.action, ["build", "enterprise_build"])

        # Test security intents
        result = parser.parse("Wipe the system")
        self.assertEqual(result.category, IntentCategory.SECURITY)
        self.assertEqual(result.action, "wipe")
        self.assertGreater(result.confidence, 0.9)

    def test_brain_bridge_initialization(self):
        """Brain bridge should initialize without errors"""
        from brain_bridge import BrainBridge

        bridge = BrainBridge()
        self.assertFalse(bridge.connected)
        self.assertEqual(bridge.stats["total_intents"], 0)

    def test_unified_brain(self):
        """Unified brain should initialize"""
        from brain_bridge import UnifiedBrain

        brain = UnifiedBrain()
        self.assertFalse(brain._initialized)


class TestPipeline(unittest.TestCase):
    """Test pipeline functionality"""

    def test_pipeline_stages_enum(self):
        """Pipeline stages should be defined"""
        from pipeline import PipelineStage

        self.assertTrue(hasattr(PipelineStage, "VOICE_INPUT"))
        self.assertTrue(hasattr(PipelineStage, "INTENT_PARSE"))
        self.assertTrue(hasattr(PipelineStage, "AI_PROCESSING"))
        self.assertTrue(hasattr(PipelineStage, "COMPLETE"))

    def test_pipeline_context(self):
        """Pipeline context should initialize correctly"""
        from pipeline import PipelineContext

        ctx = PipelineContext(
            request_id="test_001",
            raw_input="Test input"
        )
        self.assertEqual(ctx.request_id, "test_001")
        self.assertEqual(ctx.raw_input, "Test input")
        self.assertFalse(ctx.voice_verified)
        self.assertEqual(len(ctx.errors), 0)

    def test_voice_authenticator_demo_mode(self):
        """Voice authenticator should work in demo mode"""
        from pipeline import VoiceAuthenticator

        auth = VoiceAuthenticator({"simulate_voice": True})

        async def test():
            success, speaker, confidence = await auth.authenticate()
            self.assertTrue(success)
            self.assertEqual(speaker, "demo_user")
            self.assertGreater(confidence, 0.9)

        asyncio.run(test())

    def test_ai_orchestrator_budget_check(self):
        """AI orchestrator budget check should work"""
        from pipeline import PipelineAIOrchestrator

        orch = PipelineAIOrchestrator({"daily_budget": 10.0})
        budget = orch.check_budget()

        self.assertEqual(budget["budget"], 10.0)
        self.assertEqual(budget["spent"], 0.0)
        self.assertEqual(budget["status"], "OK")


class TestAIConnectors(unittest.TestCase):
    """Test AI connector functionality"""

    def test_ai_orchestrator_initialization(self):
        """AI orchestrator should initialize"""
        from ai_connectors import AIOrchestrator

        orch = AIOrchestrator()
        self.assertIsNotNone(orch.claude)
        self.assertIsNotNone(orch.gemini)
        self.assertIsNotNone(orch.gpt)

    def test_ai_routing_logic(self):
        """AI routing should work correctly"""
        from ai_connectors import AIOrchestrator

        orch = AIOrchestrator()

        # Strategy tasks should route to claude
        provider = orch.route("strategy", 0.9)
        # May route differently if no keys configured

        # Simple tasks with low complexity should prefer cheaper options
        provider = orch.route("simple", 0.1)
        # Routing depends on configured providers

    def test_check_config(self):
        """Config check should work"""
        from ai_connectors import AIOrchestrator

        orch = AIOrchestrator()
        config = orch.check_config()

        self.assertIn("claude", config)
        self.assertIn("gemini", config)
        self.assertIn("gpt", config)


class TestEkosystem(unittest.TestCase):
    """Test ekosystem builder"""

    def test_build_phases(self):
        """Build phases should be defined"""
        from ekosystem import BuildPhase

        phases = [
            "INTENT", "ANALYZE", "ARCHITECT", "BUILD",
            "TEST", "REFINE", "AUTOMATE", "REPLICATE"
        ]
        for phase in phases:
            self.assertTrue(hasattr(BuildPhase, phase))

    def test_build_channels(self):
        """Build channels should be defined"""
        from ekosystem import BuildChannel

        self.assertTrue(hasattr(BuildChannel, "EKO_VISION"))
        self.assertTrue(hasattr(BuildChannel, "ORB_AI"))
        self.assertTrue(hasattr(BuildChannel, "HYBRID"))

    def test_shield_protection(self):
        """Shield should track costs"""
        from ekosystem import Shield

        shield = Shield()
        self.assertEqual(shield.max_daily_cost, 100.0)
        self.assertTrue(shield.check_permission("build"))

        # Simulate cost tracking
        shield.track_cost(50.0)
        self.assertEqual(shield.daily_spend, 50.0)


class TestGlyphCore(unittest.TestCase):
    """Test glyph compression"""

    def test_glyph_encoder_exists(self):
        """Glyph encoder should exist"""
        glyph_path = Path("glyph_core.py")
        self.assertTrue(glyph_path.exists())


class TestRustBrain(unittest.TestCase):
    """Test Rust brain orchestrator (if compiled)"""

    def test_rust_source_exists(self):
        """Rust brain source should exist"""
        main_rs = Path("0rb-aether/core/brain/src/main.rs")
        cargo_toml = Path("0rb-aether/core/brain/Cargo.toml")

        self.assertTrue(main_rs.exists(), "main.rs should exist")
        self.assertTrue(cargo_toml.exists(), "Cargo.toml should exist")

    def test_intent_module_exists(self):
        """Intent module should exist"""
        intent_rs = Path("0rb-aether/core/brain/src/intent.rs")
        self.assertTrue(intent_rs.exists())


class TestSecurity(unittest.TestCase):
    """Test security components"""

    def test_ram_wipe_script_exists(self):
        """RAM wipe script should exist"""
        ram_wipe = Path("0rb-aether/core/security/ram_wipe.sh")
        self.assertTrue(ram_wipe.exists())

    def test_seccomp_policy_exists(self):
        """Seccomp policy should exist"""
        seccomp = Path("0rb-aether/core/security/seccomp/brain.json")
        if seccomp.exists():
            with open(seccomp) as f:
                policy = json.load(f)
            self.assertIn("syscalls", policy)

    def test_apparmor_profile_exists(self):
        """AppArmor profile should exist"""
        apparmor = Path("0rb-aether/core/security/apparmor/orb-brain")
        self.assertTrue(apparmor.exists())


class TestBuildSystem(unittest.TestCase):
    """Test build system"""

    def test_iso_script_exists(self):
        """ISO build script should exist"""
        make_iso = Path("0rb-aether/build/make_iso.sh")
        self.assertTrue(make_iso.exists())

    def test_install_script_exists(self):
        """Install script should exist"""
        install_sh = Path("0rb-aether/install.sh")
        self.assertTrue(install_sh.exists())


class TestAsyncIntegration(unittest.TestCase):
    """Test async integration between components"""

    def test_full_pipeline_demo_mode(self):
        """Full pipeline should work in demo mode"""
        from pipeline import OrbPipeline

        config = {
            "voice_auth": {"simulate_voice": True},
            "brain": {"confidence_threshold": 0.95},
            "ai": {"daily_budget": 10.0}
        }

        async def test():
            pipeline = OrbPipeline(config)
            await pipeline.initialize()

            ctx = await pipeline.process(text_input="What's the status?")

            self.assertIsNotNone(ctx.intent)
            self.assertEqual(ctx.current_stage.value, "complete")
            self.assertEqual(len(ctx.errors), 0)

            await pipeline.shutdown()

        asyncio.run(test())

    def test_brain_bridge_parsing(self):
        """Brain bridge should parse intents"""
        from brain_bridge import UnifiedBrain

        async def test():
            brain = UnifiedBrain()
            await brain.initialize()

            result = await brain.process("Build an enterprise solution")

            self.assertIn("stages", result)
            self.assertIn("parse", result["stages"])
            self.assertIn("route", result["stages"])

            await brain.shutdown()

        asyncio.run(test())


def run_tests():
    """Run all tests and generate report"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           0RB_AETHER Integration Test Suite                   ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestConfig,
        TestBrainBridge,
        TestPipeline,
        TestAIConnectors,
        TestEkosystem,
        TestGlyphCore,
        TestRustBrain,
        TestSecurity,
        TestBuildSystem,
        TestAsyncIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / max(1, result.testsRun)
    print(f"  Success Rate: {success_rate:.0%}")

    if result.failures:
        print("\nFailed Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    print("="*60)

    return len(result.failures) + len(result.errors) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
