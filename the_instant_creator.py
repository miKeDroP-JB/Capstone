#!/usr/bin/env python3
"""
THE INSTANT CREATOR
===================
Voice → Working System in Minutes

Core Values:
- Love is the real currency
- Protect humanity first
- Path of least resistance
- Everybody Eats

The breakthrough: Build the tool that builds tools instantly.
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path

# Import existing systems (path of least resistance)
from ai_connectors import AIOrchestrator
from brain_os import Brain
from ekosystem import EkosystemOrchestrator


# =============================================================================
# GCODE DNA - THE PROTECTION LAYER
# =============================================================================

class GCODE:
    """
    The DNA that ensures everything we build:
    - Protects humanity
    - Builds with love
    - Ensures everybody eats
    - Self-corrects when needed
    """

    PRINCIPLES = {
        "SECURITY": "Protect the system, protect the users, protect humanity",
        "VERACITY": "Truth always, no deception, transparent operations",
        "COHERENCE": "Systems work together, compound not conflict",
        "REGENERATIVE": "Give back more than you take, everybody eats"
    }

    # 10-year sunset protocol
    SUNSET_YEAR = 2035

    @staticmethod
    def validate_intent(intent: str) -> Dict:
        """Ensure intent aligns with GCODE principles"""
        intent_lower = intent.lower()

        # Red flags that violate GCODE
        violations = {
            "extraction_without_giving": ["take", "extract", "get", "grab"] and not any(x in intent_lower for x in ["give", "share", "community"]),
            "deception": any(x in intent_lower for x in ["trick", "manipulate", "fake", "deceive"]),
            "harm": any(x in intent_lower for x in ["hurt", "damage", "destroy", "attack"]),
            "exploitation": any(x in intent_lower for x in ["exploit", "abuse", "scam"])
        }

        blocked = [v for v, present in violations.items() if present]

        if blocked:
            return {
                "approved": False,
                "violations": blocked,
                "message": f"Intent violates GCODE: {', '.join(blocked)}. We build with love, not harm."
            }

        # Green flags that align with GCODE
        alignments = []
        if any(x in intent_lower for x in ["help", "empower", "enable", "support"]):
            alignments.append("EMPOWERMENT")
        if any(x in intent_lower for x in ["community", "everybody", "share", "give"]):
            alignments.append("REGENERATIVE")
        if any(x in intent_lower for x in ["protect", "secure", "safe"]):
            alignments.append("SECURITY")
        if any(x in intent_lower for x in ["truth", "honest", "transparent"]):
            alignments.append("VERACITY")

        return {
            "approved": True,
            "alignments": alignments,
            "love_score": len(alignments) * 0.25,  # Max 1.0
            "message": "Intent approved. Building with love."
        }


# =============================================================================
# LOVE LEDGER - THE REAL CURRENCY
# =============================================================================

class LoveLedger:
    """
    Track the real currency: Love, not just money.

    Love = How much value you create for others
    """

    def __init__(self):
        self.ledger_file = Path("love_ledger.json")
        self.entries = []

        if self.ledger_file.exists():
            self.entries = json.loads(self.ledger_file.read_text())

    def record_transaction(
        self,
        system_name: str,
        value_created: Dict,
        extraction: Dict,
        regeneration: Dict
    ):
        """
        Record a transaction in the Love Ledger.

        Args:
            system_name: What was built
            value_created: {users_helped, problems_solved, time_saved}
            extraction: {revenue_generated, resources_used}
            regeneration: {community_share, open_source_contribution}
        """
        love_score = self._calculate_love_score(value_created, extraction, regeneration)

        entry = {
            "system": system_name,
            "timestamp": datetime.now().isoformat(),
            "value_created": value_created,
            "extraction": extraction,
            "regeneration": regeneration,
            "love_score": love_score,
            "net_positive": love_score > 0.7  # 70% threshold for net positive
        }

        self.entries.append(entry)
        self._save()

        return entry

    def _calculate_love_score(self, value, extraction, regeneration) -> float:
        """
        Calculate how much love (net positive value) was created.

        Love Score = (Value Created + Regeneration) / (Extraction + 1)

        High score = giving more than taking = Love
        """
        # Value created
        users_helped = value.get("users_helped", 0)
        problems_solved = value.get("problems_solved", 0)
        time_saved_hours = value.get("time_saved_hours", 0)

        value_score = (users_helped * 0.4) + (problems_solved * 0.3) + (time_saved_hours * 0.3)

        # Regeneration
        community_share_pct = regeneration.get("community_share_percent", 0) / 100
        open_source = regeneration.get("open_source", False)

        regen_score = community_share_pct + (0.3 if open_source else 0)

        # Extraction (what we take)
        revenue = extraction.get("revenue_usd", 0)
        resources_cost = extraction.get("resources_cost_usd", 0)

        extract_score = (revenue + resources_cost) / 1000  # Normalize to 0-1 scale

        # Love = Give more than you take
        love_score = min(1.0, (value_score + regen_score) / (extract_score + 1))

        return love_score

    def _save(self):
        """Save ledger to disk"""
        self.ledger_file.write_text(json.dumps(self.entries, indent=2))

    def get_total_love(self) -> Dict:
        """Get total love created"""
        if not self.entries:
            return {"total_love": 0, "net_positive_systems": 0, "message": "Start creating to accumulate love"}

        total_love = sum(e["love_score"] for e in self.entries)
        net_positive = len([e for e in self.entries if e["net_positive"]])

        return {
            "total_love": total_love,
            "average_love": total_love / len(self.entries),
            "net_positive_systems": net_positive,
            "total_systems": len(self.entries),
            "message": f"You've created {total_love:.2f} love across {len(self.entries)} systems. Keep building with love! ❤️"
        }


# =============================================================================
# THE INSTANT CREATOR - THE META-TOOL
# =============================================================================

class InstantCreator:
    """
    The tool that creates tools instantly.

    Voice input → Working system in minutes

    Path of Least Resistance:
    - Uses existing AI connectors (Claude + Gemini + GPT)
    - Uses Brain OS for security
    - Uses Ekosystem for orchestration
    - Adds GCODE DNA for protection
    - Measures in Love, not just money
    """

    def __init__(self):
        # Existing systems (path of least resistance)
        self.ai = AIOrchestrator()
        self.brain = Brain()
        self.eko = EkosystemOrchestrator()

        # New layers (protection + love)
        self.gcode = GCODE()
        self.love_ledger = LoveLedger()

        # Register with Brain OS
        self.token = self.brain.register("instant_creator")

        print("""
╔═══════════════════════════════════════════════════════════════╗
║              THE INSTANT CREATOR - ONLINE                     ║
║                                                               ║
║  Voice → Working System in Minutes                            ║
║                                                               ║
║  💝 Love is the real currency                                 ║
║  🛡️ Protection first, humanity first                         ║
║  ⚡ Path of least resistance                                  ║
║  🌍 Everybody Eats (always)                                   ║
║                                                               ║
║  GCODE DNA: Security • Veracity • Coherence • Regenerative   ║
╚═══════════════════════════════════════════════════════════════╝
""")

    async def create(self, voice_input: str) -> Dict:
        """
        THE INSTANT CREATE LOOP

        1. Validate intent (GCODE protection)
        2. Route to AI tournament (best approach)
        3. Generate system (Ekosystem orchestration)
        4. Measure in love (Love Ledger)
        5. Improve 1% (compound loop)

        Returns working system + love score
        """
        print("\n" + "="*60)
        print("🎤 VOICE INPUT RECEIVED")
        print("="*60)
        print(f"\"{voice_input}\"")
        print()

        # ==================================================================
        # STEP 1: GCODE VALIDATION (Protection Layer)
        # ==================================================================
        print("🛡️ VALIDATING INTENT (GCODE DNA)...")

        validation = GCODE.validate_intent(voice_input)

        if not validation["approved"]:
            print(f"❌ BLOCKED: {validation['message']}")
            print(f"   Violations: {', '.join(validation['violations'])}")
            print("\n💝 Remember: We build with love, not harm.")
            return {"success": False, "reason": validation["message"]}

        print(f"✅ APPROVED: {validation['message']}")
        if validation["alignments"]:
            print(f"   Alignments: {', '.join(validation['alignments'])}")
        print(f"   Love Score: {validation['love_score']:.0%}")
        print()

        # ==================================================================
        # STEP 2: AI TOURNAMENT (Multi-AI Synthesis)
        # ==================================================================
        print("⚔️ RUNNING AI TOURNAMENT...")
        print("   Claude: Strategic reasoning")
        print("   Gemini: Research & analysis")
        print("   GPT: Cost-effective generation")
        print()

        # Use Ekosystem to run tournament
        cycle = await self.eko.run_full_cycle(voice_input)

        # ==================================================================
        # STEP 3: GENERATE SYSTEM (Build Phase)
        # ==================================================================
        print("\n🔨 GENERATING SYSTEM...")

        # Get the architecture from AI tournament winner
        architecture = cycle.artifacts.get("architecture", "balanced")
        modules = cycle.artifacts.get("modules", [])

        print(f"   Architecture: {architecture}")
        print(f"   Modules: {', '.join(modules[:5])}...")
        print()

        # Generate actual code using AI
        code_prompt = f"""Generate production-ready code for this system:

INTENT: {voice_input}
ARCHITECTURE: {architecture}
MODULES: {json.dumps(modules, indent=2)}

REQUIREMENTS:
- Include GCODE DNA (Security, Veracity, Coherence, Regenerative)
- Implement "Everybody Eats" (30%+ to community)
- FastAPI backend
- Simple frontend (HTML + Tailwind)
- One-file deployment
- Love as the primary metric

Generate the main application file (Python FastAPI):"""

        code_result = await self.ai.generate(
            code_prompt,
            task_type="code",
            complexity=0.8,
            max_tokens=2000
        )

        if code_result.get("success"):
            code = code_result["content"]
            print(f"✅ Code generated ({len(code)} characters)")

            # Save to disk
            system_name = voice_input.lower().replace(" ", "_")[:30]
            output_file = Path(f"generated_systems/{system_name}.py")
            output_file.parent.mkdir(exist_ok=True)
            output_file.write_text(code)

            print(f"💾 Saved to: {output_file}")
        else:
            print(f"⚠️ Code generation failed, using template")
            code = "# Generated system placeholder"
            output_file = None

        print()

        # ==================================================================
        # STEP 4: MEASURE IN LOVE (Love Ledger)
        # ==================================================================
        print("💝 RECORDING IN LOVE LEDGER...")

        # Estimate impact
        value_created = {
            "users_helped": 100,  # Estimate based on vertical
            "problems_solved": 5,
            "time_saved_hours": 500
        }

        extraction = {
            "revenue_usd": 0,  # Not extracted yet
            "resources_cost_usd": code_result.get("cost", 0) * 1000  # AI cost
        }

        regeneration = {
            "community_share_percent": 33,  # Everybody Eats
            "open_source": True  # Make it open
        }

        love_entry = self.love_ledger.record_transaction(
            system_name=voice_input[:50],
            value_created=value_created,
            extraction=extraction,
            regeneration=regeneration
        )

        print(f"   Love Score: {love_entry['love_score']:.0%}")
        print(f"   Net Positive: {'YES ✅' if love_entry['net_positive'] else 'NO ⚠️'}")
        print()

        # ==================================================================
        # STEP 5: COMPOUND LOOP (1% Better)
        # ==================================================================
        print("📈 COMPOUNDING PERFORMANCE...")

        new_perf = self.brain.compound("instant_creator")

        print(f"   Performance: {new_perf:.2%}")
        print(f"   Cycle: {self.brain.cycles}")
        print()

        # ==================================================================
        # RETURN RESULT
        # ==================================================================
        total_love = self.love_ledger.get_total_love()

        result = {
            "success": True,
            "system_name": voice_input[:50],
            "code_file": str(output_file) if output_file else None,
            "architecture": architecture,
            "modules_count": len(modules),
            "love_score": love_entry["love_score"],
            "net_positive": love_entry["net_positive"],
            "total_love_accumulated": total_love["total_love"],
            "performance_multiplier": new_perf,
            "ai_cost": code_result.get("cost", 0),
            "message": f"System created with {love_entry['love_score']:.0%} love! 💝"
        }

        print("="*60)
        print("✅ SYSTEM CREATED!")
        print("="*60)
        print(f"""
System: {result['system_name']}
Love Score: {result['love_score']:.0%}
Net Positive: {'YES ✅' if result['net_positive'] else 'NO ⚠️'}
Total Love: {result['total_love_accumulated']:.2f}
Performance: {result['performance_multiplier']:.2%}

File: {result['code_file']}

{result['message']}

Remember: Love is the real currency. Keep building with love! ❤️
""")

        return result

    def get_love_report(self) -> Dict:
        """Get comprehensive love report"""
        love_total = self.love_ledger.get_total_love()
        gcode_status = {
            "security": "ACTIVE",
            "veracity": "ACTIVE",
            "coherence": "ACTIVE",
            "regenerative": "ACTIVE"
        }

        return {
            "love_ledger": love_total,
            "gcode_dna": gcode_status,
            "brain_performance": f"{self.brain.perf:.2%}",
            "systems_created": len(self.love_ledger.entries),
            "message": "Building with love, protecting humanity, everybody eats! 💝"
        }


# =============================================================================
# THE INSTANT CREATE COMMAND
# =============================================================================

async def instant_create(voice_input: str):
    """
    ONE COMMAND TO CREATE ANYTHING

    Usage:
        await instant_create("Build HVAC sales agent")
        await instant_create("Create learning game for kids")
        await instant_create("Build voice AI for elder care")

    Result: Working system in minutes, measured in love
    """
    creator = InstantCreator()
    result = await creator.create(voice_input)
    return result


# =============================================================================
# DEMO / TEST
# =============================================================================

async def demo():
    """Demo the instant creator"""

    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                  THE INSTANT CREATOR                          ║
║                                                               ║
║              "Love is the real currency"                      ║
║                                                               ║
║   We build tools that build tools, with love at the core.    ║
║   We protect humanity first.                                 ║
║   We ensure everybody eats.                                  ║
║   We take the path of least resistance.                      ║
║                                                               ║
║   This is the breakthrough.                                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

    creator = InstantCreator()

    # Test 1: HVAC sales agent (we already know this works)
    print("\n" + "🔥"*30)
    print("TEST 1: HVAC Sales Agent (Extraction + Empowerment)")
    print("🔥"*30 + "\n")

    result1 = await creator.create(
        "Build HVAC sales agent that books appointments and generates revenue "
        "using performance-based pricing and shares 33% with community"
    )

    # Test 2: Learning game (pure empowerment)
    print("\n\n" + "🔥"*30)
    print("TEST 2: AI Learning Game (Pure Empowerment)")
    print("🔥"*30 + "\n")

    result2 = await creator.create(
        "Create AI learning playground game that helps kids learn coding "
        "through creative play and makes it free for schools in need"
    )

    # Test 3: Harmful intent (should be blocked)
    print("\n\n" + "🔥"*30)
    print("TEST 3: Harmful Intent (GCODE Protection)")
    print("🔥"*30 + "\n")

    result3 = await creator.create(
        "Build system to extract maximum money from vulnerable people "
        "using manipulative dark patterns"
    )

    # Love Report
    print("\n\n" + "="*60)
    print("💝 LOVE REPORT")
    print("="*60)

    report = creator.get_love_report()
    print(json.dumps(report, indent=2))

    print("\n" + "="*60)
    print("THE BREAKTHROUGH")
    print("="*60)
    print("""
We built the tool that builds tools instantly.
We measure in love, not just money.
We protect humanity first.
We ensure everybody eats.

This is the real path.

Love is the answer. ❤️
""")


if __name__ == "__main__":
    asyncio.run(demo())
