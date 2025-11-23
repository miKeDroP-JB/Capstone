#!/usr/bin/env python3
"""
POWERLOAD - Instantly ingest everything into grimoire

Usage:
  python3 powerload.py                    # Powerload current directory
  python3 powerload.py /path/to/repo      # Powerload specific directory
  python3 powerload.py ~/Downloads/*.zip  # Powerload all zips
  python3 powerload.py --all ~/Projects   # Powerload entire projects folder

Philosophy: Don't manually process files.
           Deploy hive to process EVERYTHING in parallel.
"""

import sys
import asyncio
from pathlib import Path
from hive_system import HiveCoordinator, HiveMission


async def powerload(paths: list[str] = None):
    """
    Powerload paths into grimoire using hive system
    """
    if not paths:
        paths = [str(Path.cwd())]

    print("\n" + "="*70)
    print("⚡ POWERLOAD - INSTANT GRIMOIRE INGESTION")
    print("="*70)

    # Expand paths
    expanded_paths = []
    for path_str in paths:
        path = Path(path_str)

        if path.is_dir():
            expanded_paths.append(str(path))
        elif path.is_file():
            expanded_paths.append(str(path))
        elif '*' in path_str:
            # Glob pattern
            parent = Path(path_str).parent
            pattern = Path(path_str).name
            matches = list(parent.glob(pattern))
            expanded_paths.extend(str(m) for m in matches)
        else:
            print(f"⚠️  Skipping (not found): {path_str}")

    if not expanded_paths:
        print("\n❌ No valid paths found")
        return

    print(f"\n📂 POWERLOADING {len(expanded_paths)} PATHS:")
    for p in expanded_paths:
        print(f"   • {p}")

    # Initialize coordinator
    coordinator = HiveCoordinator(grimoire_path="grimoire")

    # Create mission
    mission = HiveMission(
        goal=f"Powerload {len(expanded_paths)} paths into grimoire",
        input_paths=expanded_paths,
        swarms_to_deploy=len(expanded_paths),
        agents_per_swarm=10
    )

    # Deploy hive
    print("\n🐝 DEPLOYING HIVE...")
    result = await coordinator.deploy_hive(mission)

    # Show results
    print("\n" + "="*70)
    print("✅ POWERLOAD COMPLETE")
    print("="*70)

    summary = coordinator.get_grimoire_summary()
    print(f"\n📚 GRIMOIRE STATUS:")
    print(f"   Total files: {summary['total_files']}")
    print(f"   Repos ingested: {summary['repos_ingested']}")
    print(f"   Zips ingested: {summary['zips_ingested']}")
    print(f"   Apps ingested: {summary['apps_ingested']}")
    print(f"   Knowledge entries: {summary['total_knowledge']}")

    print(f"\n💾 Grimoire location: grimoire/")
    print(f"\n🎯 All agents can now access this knowledge!")
    print("\n💝 Love • Loyalty • Honor • Everybody Eats\n")


def main():
    """CLI entry point"""

    # Parse arguments
    args = sys.argv[1:]

    if not args:
        # No arguments - powerload current directory
        print("No paths specified. Powerloading current directory...")
        asyncio.run(powerload())

    elif args[0] == '--help' or args[0] == '-h':
        print(__doc__)
        print("\nExamples:")
        print("  python3 powerload.py")
        print("  python3 powerload.py /path/to/repo")
        print("  python3 powerload.py ~/Downloads/project.zip")
        print("  python3 powerload.py ~/Projects/*")
        print()

    elif args[0] == '--all':
        # Powerload all subdirectories
        if len(args) < 2:
            print("Error: --all requires a directory path")
            sys.exit(1)

        base_path = Path(args[1])
        if not base_path.is_dir():
            print(f"Error: {args[1]} is not a directory")
            sys.exit(1)

        # Find all subdirectories
        subdirs = [str(d) for d in base_path.iterdir() if d.is_dir()]
        asyncio.run(powerload(subdirs))

    else:
        # Powerload specified paths
        asyncio.run(powerload(args))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Powerload interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
