#!/usr/bin/env python3
"""
ARCHITECT FORGE DEMO - The Impossibility Compiler in Action
═══════════════════════════════════════════════════════════════
Demonstration of the self-authoring meta-system that generates
curricula, trains architect-agents, and compiles them into
deployable apprentices.

"Some patterns can't be unseen. Some systems can't be unbuilt."
═══════════════════════════════════════════════════════════════
"""

import asyncio
import json
from pathlib import Path

from architect_forge import Forge
from architect_forge.curriculum import Task, TaskType, Difficulty, CurriculumGenerator
from architect_forge.orb_integration import OrbEmpireForge, Avatar, create_empire_forge


async def demo_basic_forge():
    """Demonstrate basic Forge functionality"""
    print("\n" + "═" * 60)
    print("  DEMO 1: BASIC FORGE OPERATION")
    print("═" * 60 + "\n")

    # Create and ignite the Forge
    forge = Forge()
    await forge.ignite()

    # Create a simple task
    task = Task(
        task_id="demo_task_1",
        task_type=TaskType.CODE.value,
        objective="Create an AI agent that can analyze code and suggest improvements",
        constraints=[
            "Must process code in under 5 seconds",
            "Must provide actionable suggestions",
            "Must explain reasoning"
        ],
        success_criteria="Agent produces useful, accurate code analysis",
        difficulty=Difficulty.MEDIUM
    )

    print(f"  Task: {task.objective}")
    print(f"  Constraints: {len(task.constraints)}")
    print(f"  Difficulty: {task.difficulty.name}\n")

    # Run tournament
    result = await forge.run_tournament(task, rounds=3)

    print(f"\n  Results:")
    print(f"    Winner: {result.winner.name}")
    print(f"    Peak Score: {result.metrics['peak_score']:.2f}")
    print(f"    Blueprints Generated: {len(result.blueprints)}")

    # Compile an apprentice
    if result.blueprints:
        apprentice = await forge.compile_apprentice(result.blueprints[0])
        print(f"\n  Apprentice Compiled: {apprentice.apprentice_id}")
        print(f"    Blueprint: {apprentice.blueprint.name}")
        print(f"    Certification: {apprentice.blueprint.certification_level}")

    await forge.shutdown()
    return result


async def demo_curriculum_generation():
    """Demonstrate curriculum generation"""
    print("\n" + "═" * 60)
    print("  DEMO 2: CURRICULUM GENERATION")
    print("═" * 60 + "\n")

    curriculum = CurriculumGenerator()

    # Generate tasks of increasing difficulty
    tasks = []
    for difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        task = curriculum.generate_task(
            task_type=TaskType.CODE,
            difficulty=difficulty
        )
        tasks.append(task)
        print(f"  [{difficulty.name}] {task.objective[:60]}...")
        print(f"    Constraints: {len(task.constraints)}")
        print(f"    Time Limit: {task.time_limit_seconds}s\n")

    print(f"  Total tasks generated: {curriculum.generated_count}")
    return tasks


async def demo_constraint_mutation():
    """Demonstrate constraint mutation (anti-framework)"""
    print("\n" + "═" * 60)
    print("  DEMO 3: CONSTRAINT MUTATION (ANTI-FRAMEWORK)")
    print("═" * 60 + "\n")

    from architect_forge.constraints import ConstraintMutator

    mutator = ConstraintMutator(mutation_rate=1.0)  # Force mutation

    # Create original task
    original = Task(
        task_id="mutation_demo",
        task_type=TaskType.CODE.value,
        objective="Build a REST API",
        constraints=["Must be fast", "Must be secure"],
        success_criteria="Working API",
        difficulty=Difficulty.MEDIUM,
        time_limit_seconds=300,
        resources_available=["documentation", "examples", "tools"]
    )

    print(f"  Original Task:")
    print(f"    Objective: {original.objective}")
    print(f"    Constraints: {original.constraints}")
    print(f"    Time Limit: {original.time_limit_seconds}s\n")

    # Apply mutations
    mutated = original
    for i in range(3):
        mutated = mutator.mutate(mutated)
        print(f"  After Mutation {i + 1}:")
        print(f"    Objective: {mutated.objective[:50]}...")
        print(f"    Constraints: {len(mutated.constraints)}")
        print(f"    Time Limit: {mutated.time_limit_seconds}s\n")

    stats = mutator.get_mutation_statistics()
    print(f"  Mutations Applied: {stats['total_mutations']}")
    print(f"  Types: {list(stats['mutations_by_type'].keys())}")

    return mutated


async def demo_orb_empire_integration():
    """Demonstrate 0RB Empire integration"""
    print("\n" + "═" * 60)
    print("  DEMO 4: 0RB EMPIRE INTEGRATION")
    print("═" * 60 + "\n")

    # Create empire forge (all 7 avatars)
    empire = await create_empire_forge()

    # Generate a specialist for Apollo (Strategic Planning)
    print("\n  Generating Apollo Specialist...")
    apollo_apprentice = await empire.generate_specialist_for(
        Avatar.APOLLO,
        objective="Develop go-to-market strategy for AI-powered sales tool",
        constraints=["90-day timeline", "Under $50k budget", "Target enterprise market"]
    )
    print(f"    Apprentice: {apollo_apprentice.apprentice_id}")
    print(f"    Blueprint: {apollo_apprentice.blueprint.name}")

    # Generate a specialist for Hephaestus (Building)
    print("\n  Generating Hephaestus Specialist...")
    heph_apprentice = await empire.generate_specialist_for(
        Avatar.HEPHAESTUS,
        objective="Build voice agent that can handle enterprise sales calls",
        constraints=["Sub-second latency", "99.9% uptime", "Multi-language support"]
    )
    print(f"    Apprentice: {heph_apprentice.apprentice_id}")
    print(f"    Blueprint: {heph_apprentice.blueprint.name}")

    # Get empire statistics
    stats = empire.get_empire_statistics()
    print(f"\n  Empire Statistics:")
    print(f"    Active Avatars: {stats['avatars_active']}")
    for avatar, data in stats['avatar_stats'].items():
        print(f"    {avatar}: {data['blueprints_generated']} blueprints")

    return empire


async def demo_recursive_improvement():
    """Demonstrate recursive self-improvement"""
    print("\n" + "═" * 60)
    print("  DEMO 5: RECURSIVE SELF-IMPROVEMENT")
    print("═" * 60 + "\n")

    forge = Forge()
    await forge.ignite()

    # Meta-task: improve the architect's own training
    meta_task = Task(
        task_id="meta_improvement",
        task_type=TaskType.META.value,
        objective="Generate a better training curriculum for architect agents",
        constraints=[
            "Must increase win rate by 10%",
            "Must reduce training time",
            "Must maintain diversity"
        ],
        success_criteria="Measurable improvement in architect performance",
        difficulty=Difficulty.EXPERT
    )

    print(f"  Meta-Task: {meta_task.objective}")
    print(f"  Running recursive improvement (depth=3)...\n")

    # Run recursive improvement (limited depth for demo)
    results = await forge.run_recursive_improvement(meta_task, depth=3)

    print(f"\n  Recursive Results:")
    for i, result in enumerate(results):
        print(f"    Depth {i + 1}: Score {result.metrics['peak_score']:.2f}, "
              f"Emergence: {result.metrics['emergence_score']:.2f}")

    await forge.shutdown()
    return results


async def main():
    """Run all demos"""
    print("\n")
    print("═" * 60)
    print("  THE ARCHITECT FORGE v1.0")
    print("  The Impossibility Compiler")
    print("═" * 60)
    print("\n  'Some patterns can't be unseen.'")
    print("  'Some systems can't be unbuilt.'")
    print("  'And some impossibilities... become inevitable.'")

    # Run demos
    await demo_basic_forge()
    await demo_curriculum_generation()
    await demo_constraint_mutation()
    await demo_orb_empire_integration()
    await demo_recursive_improvement()

    print("\n" + "═" * 60)
    print("  ALL DEMOS COMPLETE")
    print("═" * 60)
    print("\n  The Forge is ready.")
    print("  What impossible thing shall we build next?")
    print("\n  ⚡ 11:11 Protocol Active ⚡\n")


if __name__ == "__main__":
    asyncio.run(main())
