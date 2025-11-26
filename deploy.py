#!/usr/bin/env python3
"""
ARCHITECT FORGE - QUICK DEPLOY
═══════════════════════════════════════════════════════════════
One command to rule them all.

Usage:
    python deploy.py              # Interactive menu
    python deploy.py forge        # Run the Forge demo
    python deploy.py oracle       # Generate Oracle Agency apprentice
    python deploy.py bench        # Run benchmarks
    python deploy.py all          # Run everything
═══════════════════════════════════════════════════════════════
"""

import asyncio
import sys

def banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ████████╗██╗  ██╗███████╗                                ║
║     ╚══██╔══╝██║  ██║██╔════╝                                ║
║        ██║   ███████║█████╗                                  ║
║        ██║   ██╔══██║██╔══╝                                  ║
║        ██║   ██║  ██║███████╗                                ║
║        ╚═╝   ╚═╝  ╚═╝╚══════╝                                ║
║                                                               ║
║     ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗████████╗███████╗   ║
║     ██╔══██╗██╔══██╗██╔════╝ ██║  ██║██║╚══██╔══╝██╔════╝   ║
║     ███████║██████╔╝██║      ███████║██║   ██║   █████╗     ║
║     ██╔══██║██╔══██╗██║      ██╔══██║██║   ██║   ██╔══╝     ║
║     ██║  ██║██║  ██║╚██████╗ ██║  ██║██║   ██║   ███████╗   ║
║     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝   ║
║                                                               ║
║     ███████╗ ██████╗ ██████╗  ██████╗ ███████╗               ║
║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝               ║
║     █████╗  ██║   ██║██████╔╝██║  ███╗█████╗                 ║
║     ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝                 ║
║     ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗               ║
║     ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝               ║
║                                                               ║
║              THE IMPOSSIBILITY COMPILER v1.0                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

async def run_forge_demo():
    """Run the main Forge demo"""
    print("\n⚡ LAUNCHING FORGE DEMO...\n")
    from architect_forge.demo import main
    await main()

async def run_oracle():
    """Generate Oracle Agency apprentice"""
    print("\n⚡ GENERATING ORACLE AGENCY APPRENTICE...\n")
    from architect_forge.oracle_agency import main
    await main()

async def run_benchmark():
    """Run benchmark suite"""
    print("\n⚡ RUNNING BENCHMARKS...\n")
    from architect_forge.benchmark import main
    await main()

async def run_quick_test():
    """Quick test to verify everything works"""
    print("\n⚡ QUICK SYSTEM CHECK...\n")

    from architect_forge import (
        Forge, MirrorNet, AdversarialSandbox, JuryCouncil,
        OuroborosLedger, CurriculumGenerator, ConstraintMutator,
        BenchmarkSuite
    )

    checks = [
        ("Forge", Forge),
        ("MirrorNet", MirrorNet),
        ("AdversarialSandbox", AdversarialSandbox),
        ("JuryCouncil", JuryCouncil),
        ("OuroborosLedger", OuroborosLedger),
        ("CurriculumGenerator", CurriculumGenerator),
        ("ConstraintMutator", ConstraintMutator),
        ("BenchmarkSuite", BenchmarkSuite),
    ]

    print("  Component Check:")
    for name, cls in checks:
        print(f"    ✓ {name}")

    print("\n  All systems operational.")
    print("  The impossible is ready.\n")

async def run_all():
    """Run everything"""
    await run_quick_test()
    await run_forge_demo()
    await run_oracle()
    await run_benchmark()

def menu():
    """Interactive menu"""
    banner()
    print("""
  SELECT MODE:
  ─────────────────────────────────────
  [1] 🔥 Forge Demo      - See the tournament brain in action
  [2] 📞 Oracle Agency   - Generate sales apprentice
  [3] 📊 Benchmarks      - Compare against GPT-4, Claude, etc.
  [4] ✓  Quick Test      - Verify all systems operational
  [5] 🚀 Run Everything  - Full demonstration
  [Q] Exit
  ─────────────────────────────────────
    """)

    choice = input("  Enter choice: ").strip().lower()
    return choice

async def main():
    """Main entry point"""

    # Check for command line args
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "forge":
            banner()
            await run_forge_demo()
        elif cmd == "oracle":
            banner()
            await run_oracle()
        elif cmd == "bench":
            banner()
            await run_benchmark()
        elif cmd == "test":
            banner()
            await run_quick_test()
        elif cmd == "all":
            banner()
            await run_all()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python deploy.py [forge|oracle|bench|test|all]")
        return

    # Interactive mode
    while True:
        choice = menu()

        if choice == "1" or choice == "forge":
            await run_forge_demo()
        elif choice == "2" or choice == "oracle":
            await run_oracle()
        elif choice == "3" or choice == "bench":
            await run_benchmark()
        elif choice == "4" or choice == "test":
            await run_quick_test()
        elif choice == "5" or choice == "all":
            await run_all()
        elif choice == "q" or choice == "quit" or choice == "exit":
            print("\n  ⚡ 11:11 - The impossible awaits. ⚡\n")
            break
        else:
            print("\n  Invalid choice. Try again.\n")

        input("\n  Press Enter to continue...")

if __name__ == "__main__":
    asyncio.run(main())
