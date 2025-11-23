#!/usr/bin/env python3
"""
CREATE - THE ONE COMMAND

Voice → Working System in Minutes

Usage:
    python CREATE.py "Build HVAC sales agent"
    python CREATE.py "Create learning game for kids"
    python CREATE.py "Build anything with love"

Love is the real currency.
"""
import asyncio
import sys
from the_instant_creator import instant_create


async def main():
    if len(sys.argv) < 2:
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                       CREATE                                  ║
║                                                               ║
║  The tool that creates tools instantly.                      ║
║  Measured in love, protected by GCODE.                       ║
║                                                               ║
║  Usage:                                                      ║
║    python CREATE.py "your idea here"                         ║
║                                                               ║
║  Examples:                                                   ║
║    python CREATE.py "Build HVAC sales agent"                 ║
║    python CREATE.py "Create learning game"                   ║
║    python CREATE.py "Build voice AI elder care"              ║
║                                                               ║
║  Love is the real currency. 💝                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
        return

    # Get voice input from command line
    voice_input = " ".join(sys.argv[1:])

    # CREATE
    result = await instant_create(voice_input)

    if result["success"]:
        print(f"\n✅ CREATED: {result['system_name']}")
        print(f"💝 Love Score: {result['love_score']:.0%}")
        print(f"📁 File: {result['code_file']}")
        print(f"\n{result['message']}")
    else:
        print(f"\n❌ BLOCKED: {result['reason']}")


if __name__ == "__main__":
    asyncio.run(main())
