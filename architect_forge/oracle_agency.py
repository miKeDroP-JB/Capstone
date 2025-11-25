#!/usr/bin/env python3
"""
ORACLE AGENCY - First Apprentice Generation
═══════════════════════════════════════════════════════════════
Generate a specialized sales architect for Oracle Agency's
enterprise voice agent deals.

"Voice cloning can't close enterprise deals." - Watch.
═══════════════════════════════════════════════════════════════
"""

import asyncio
from pathlib import Path

from architect_forge import (
    Forge, Task, TaskType, Difficulty,
    OrbEmpireForge, Avatar, create_empire_forge
)
from architect_forge.forge import ForgeConfig


async def generate_oracle_sales_architect():
    """Generate a sales architect specialized for Oracle Agency"""

    print("\n" + "═" * 60)
    print("  ORACLE AGENCY - APPRENTICE GENERATION")
    print("  'Voice agents closing enterprise deals at scale'")
    print("═" * 60 + "\n")

    # Initialize the Empire Forge
    empire = await create_empire_forge()

    # Define the Oracle Agency sales task
    oracle_task = Task(
        task_id="oracle_sales_architect_v1",
        task_type=TaskType.COMMUNICATION.value,
        objective="Create an AI sales agent that closes enterprise deals through voice interaction",
        constraints=[
            "Must handle objections in real-time",
            "Must qualify leads within first 60 seconds",
            "Must maintain natural conversation flow",
            "Must integrate with CRM for instant data access",
            "Must escalate appropriately to human when needed",
            "Must achieve >15% close rate on qualified leads",
            "Sub-500ms response latency"
        ],
        success_criteria="Confirmed enterprise contract signatures through autonomous voice negotiation",
        difficulty=Difficulty.EXPERT
    )

    print(f"  Task: {oracle_task.objective}\n")
    print(f"  Constraints:")
    for c in oracle_task.constraints:
        print(f"    • {c}")
    print(f"\n  Difficulty: {oracle_task.difficulty.name}")
    print(f"  Success: {oracle_task.success_criteria}\n")

    # Generate using Mercury (Communication) avatar
    print("  ⚡ Activating Mercury Forge (Communication Specialist)...\n")

    mercury_forge = await empire.get_forge(Avatar.MERCURY)
    result = await mercury_forge.forge.run_tournament(oracle_task, rounds=5)

    print(f"\n  Tournament Complete!")
    print(f"    Winner: {result.winner.name}")
    print(f"    Approach: {result.winner.bias.value} + {result.winner.specialization.value}")
    print(f"    Score: {result.metrics['peak_score']:.2f}")
    print(f"    Emergence: {result.metrics['emergence_score']:.2f}")

    # Compile the apprentice
    if result.blueprints:
        best_blueprint = result.blueprints[0]
        apprentice = await mercury_forge.forge.compile_apprentice(best_blueprint)

        print(f"\n  ✓ APPRENTICE COMPILED")
        print(f"    ID: {apprentice.apprentice_id}")
        print(f"    Blueprint: {apprentice.blueprint.name}")
        print(f"    Certification: {apprentice.blueprint.certification_level}")
        print(f"    Tests Embedded: {len(apprentice.blueprint.tests)}")
        print(f"    Proofs: {len(apprentice.blueprint.proofs)}")

        # Export blueprint
        output_path = Path("architect_forge/output")
        output_path.mkdir(exist_ok=True)

        blueprint_file = output_path / f"{apprentice.blueprint.blueprint_id}.json"
        with open(blueprint_file, "w") as f:
            f.write(apprentice.blueprint.to_json())

        print(f"\n  Blueprint exported: {blueprint_file}")

        # Run self-tests
        print(f"\n  Running self-tests...")
        test_results = await apprentice.run_self_tests()
        print(f"    Passed: {test_results['passed']}/{test_results['total']}")

        return apprentice

    return None


async def generate_cross_avatar_team():
    """Generate a full team across multiple avatars for Oracle Agency"""

    print("\n" + "═" * 60)
    print("  ORACLE AGENCY - FULL TEAM GENERATION")
    print("═" * 60 + "\n")

    empire = await create_empire_forge()
    team = {}

    # Define specialized tasks for each avatar
    tasks = {
        Avatar.MERCURY: Task(
            task_id="oracle_comms",
            task_type=TaskType.COMMUNICATION.value,
            objective="Handle all client communication with enterprise-grade persuasion",
            constraints=["Real-time response", "Objection handling", "Tone adaptation"],
            success_criteria="90%+ positive sentiment in client interactions",
            difficulty=Difficulty.HARD
        ),
        Avatar.APOLLO: Task(
            task_id="oracle_strategy",
            task_type=TaskType.STRATEGY.value,
            objective="Develop account strategies that maximize deal value",
            constraints=["Data-driven", "Competitive awareness", "Upsell identification"],
            success_criteria="Average deal size increase of 25%",
            difficulty=Difficulty.HARD
        ),
        Avatar.ATHENA: Task(
            task_id="oracle_analysis",
            task_type=TaskType.ANALYSIS.value,
            objective="Analyze prospect data to identify high-value opportunities",
            constraints=["Real-time scoring", "Pattern recognition", "Risk assessment"],
            success_criteria="Lead scoring accuracy >85%",
            difficulty=Difficulty.HARD
        ),
        Avatar.ARES: Task(
            task_id="oracle_execution",
            task_type=TaskType.SECURITY.value,
            objective="Execute deals with aggressive but compliant tactics",
            constraints=["Legal compliance", "Pressure calibration", "Close optimization"],
            success_criteria="Close rate >20% on qualified leads",
            difficulty=Difficulty.EXPERT
        )
    }

    for avatar, task in tasks.items():
        print(f"  Generating {avatar.value.upper()} specialist...")
        forge = await empire.get_forge(avatar)
        result = await forge.forge.run_tournament(task, rounds=3)

        if result.blueprints:
            apprentice = await forge.forge.compile_apprentice(result.blueprints[0])
            team[avatar.value] = {
                "apprentice_id": apprentice.apprentice_id,
                "blueprint": apprentice.blueprint.name,
                "score": result.metrics['peak_score']
            }
            print(f"    ✓ {apprentice.blueprint.name} (Score: {result.metrics['peak_score']:.2f})")

    print(f"\n  Team Generated: {len(team)} specialists")
    return team


async def main():
    """Run Oracle Agency apprentice generation"""

    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║            ORACLE AGENCY × ARCHITECT FORGE                ║")
    print("║         'The Voice That Closes Enterprise Deals'          ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    # Generate primary sales architect
    sales_apprentice = await generate_oracle_sales_architect()

    # Generate full team
    team = await generate_cross_avatar_team()

    print("\n" + "═" * 60)
    print("  ORACLE AGENCY ARCHITECTS READY")
    print("═" * 60)
    print("\n  Sales Apprentice: " + (sales_apprentice.apprentice_id if sales_apprentice else "N/A"))
    print(f"  Team Size: {len(team)} specialists")
    print("\n  The impossible is now operational.")
    print("  Deploy when ready.")
    print("\n  ⚡ 11:11 ⚡\n")


if __name__ == "__main__":
    asyncio.run(main())
