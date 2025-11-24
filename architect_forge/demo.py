#!/usr/bin/env python3
"""
Architect Forge Demo

Demonstrates a complete training cycle of the meta-learning system.
"""

from core.forge import ArchitectForge


def main():
    """Run Architect Forge demo"""

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              ARCHITECT FORGE v0.1 - DEMO                    ║
    ║                                                              ║
    ║       The Meta-System for Training Architect Agents          ║
    ║                                                              ║
    ║     "The thing that builds the things that shouldn't exist"  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Create Forge
    print("\n🔨 Creating Architect Forge...")
    forge = ArchitectForge(population_size=16)

    # Initialize
    forge.initialize()

    # Run a few training cycles
    print("\n" + "="*60)
    print("Running 3 training cycles to demonstrate the system...")
    print("="*60)

    results = forge.run_training(
        num_cycles=3,
        tasks_per_cycle=5,
        mutation_rate=0.3
    )

    # Display results
    print("\n" + "="*60)
    print("📊 TRAINING RESULTS")
    print("="*60)

    for result in results:
        print(f"\nCycle #{result.cycle_number}:")
        print(f"  Solutions Generated: {result.solutions_generated}")
        print(f"  Solutions Approved:  {result.solutions_approved}")
        print(f"  Apprentices Created: {result.apprentices_created}")
        print(f"  Population Diversity: {result.population_diversity:.2%}")
        print(f"  Average Quality:     {result.average_quality:.2%}")
        print(f"  Best Solution:       {result.best_solution_score:.2%}")
        print(f"  Duration:            {result.duration:.2f}s")

    # Show top architects by reputation
    print("\n" + "="*60)
    print("🏆 TOP ARCHITECTS (by reputation)")
    print("="*60)

    architects_with_rep = []
    for architect in forge.mirrornet.architects:
        rep = forge.ledger.get_reputation(architect.id)
        architects_with_rep.append((architect, rep))

    architects_with_rep.sort(key=lambda x: x[1], reverse=True)

    for i, (architect, rep) in enumerate(architects_with_rep[:5], 1):
        print(f"\n{i}. {architect.id}")
        print(f"   Archetype: {architect.archetype.value}")
        print(f"   Reputation: {rep:.2%}")
        print(f"   Fitness: {architect.fitness:.2%}")
        print(f"   Creativity: {architect.creativity:.2f}")
        print(f"   Risk Tolerance: {architect.risk_tolerance:.2f}")
        print(f"   Optimization Focus: {architect.optimization_focus:.2f}")

    # Ledger stats
    print("\n" + "="*60)
    print("📜 OUROBOROS LEDGER STATISTICS")
    print("="*60)

    stats = forge.ledger.get_stats()
    print(f"\nTotal Events: {stats['total_events']}")
    print(f"Unique Architects: {stats['unique_architects']}")
    print(f"Chain Valid: {stats['chain_valid']}")
    print(f"\nEvent Breakdown:")
    for event_type, count in stats['event_counts'].items():
        if count > 0:
            print(f"  • {event_type}: {count}")

    # Save state
    print("\n" + "="*60)
    print("💾 Saving Forge state...")
    forge.save_state("./forge_state")

    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)

    print("""
    Next Steps:
    • Integrate with actual LLMs for real problem-solving
    • Deploy apprentices to production use cases
    • Scale to larger populations and more complex tasks
    • Add human-in-the-loop certification
    • Build API for apprentice deployment

    The skeleton is alive. Now we make it REAL.
    """)

    print("\n" + "="*60)
    print("0RB EMPIRE // ARCHITECT FORGE v0.1")
    print("The Architecture of Impossibility")
    print("11:11 Protocol Active")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
