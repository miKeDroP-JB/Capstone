#!/usr/bin/env python3
"""
0RB_AETHER Quick Launcher
Bypasses optional dependencies for fast startup.

Love - Loyalty - Honor - Everybody Eats
"""
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Banner
BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██████╗ ██████╗ ██████╗      █████╗ ███████╗████████╗    ║
║    ██╔═████╗██╔══██╗██╔══██╗    ██╔══██╗██╔════╝╚══██╔══╝    ║
║    ██║██╔██║██████╔╝██████╔╝    ███████║█████╗     ██║       ║
║    ████╔╝██║██╔══██╗██╔══██╗    ██╔══██║██╔══╝     ██║       ║
║    ╚██████╔╝██║  ██║██████╔╝    ██║  ██║███████╗   ██║       ║
║     ╚═════╝ ╚═╝  ╚═╝╚═════╝     ╚═╝  ╚═╝╚══════╝   ╚═╝       ║
║                                                               ║
║            USB-Bootable RAM-Only Encrypted Meta-OS            ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
"""

class QuickLauncher:
    """Minimal launcher for 0RB_AETHER"""

    def __init__(self):
        self.started = datetime.now()
        self.services = {}

    async def start_api(self):
        """Start FastAPI server"""
        try:
            import uvicorn
            from fastapi import FastAPI

            app = FastAPI(
                title="0RB_AETHER API",
                version="1.0.0",
                description="Love - Loyalty - Honor - Everybody Eats"
            )

            @app.get("/")
            async def root():
                return {
                    "name": "0RB_AETHER",
                    "status": "online",
                    "uptime": str(datetime.now() - self.started),
                    "philosophy": "Love - Loyalty - Honor - Everybody Eats"
                }

            @app.get("/health")
            async def health():
                return {"status": "healthy", "services": self.services}

            @app.get("/stats")
            async def stats():
                return {
                    "started": self.started.isoformat(),
                    "uptime_seconds": (datetime.now() - self.started).total_seconds(),
                    "services": self.services
                }

            # Load modules
            await self.load_modules()

            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8080,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()

        except Exception as e:
            print(f"[!] API Error: {e}")
            raise

    async def load_modules(self):
        """Load 0RB_AETHER modules"""
        modules = [
            ("FlowSync SDK", "flowsync", "FlowSync"),
            ("Marketplace", "marketplace", "NodeMarketplace"),
            ("Edge Network", "edge", "EdgeNetwork"),
            ("UI Framework", "ui", "Application"),
            ("Builder Swarm", "builder.swarm", "BuilderSwarm"),
            ("Reasoning Engine", "core.reasoning", "ReasoningEngine"),
        ]

        for name, module, cls in modules:
            try:
                mod = __import__(module, fromlist=[cls])
                self.services[name] = "loaded"
                print(f"  [✓] {name}")
            except Exception as e:
                self.services[name] = f"error: {str(e)[:50]}"
                print(f"  [✗] {name}: {e}")

    def print_status(self):
        """Print service status"""
        print("\n" + "="*55)
        print("  SERVICE STATUS")
        print("="*55)

        loaded = sum(1 for v in self.services.values() if v == "loaded")
        total = len(self.services)

        for name, status in self.services.items():
            icon = "✓" if status == "loaded" else "✗"
            print(f"  [{icon}] {name}: {status}")

        print("="*55)
        print(f"  Loaded: {loaded}/{total} services")
        print("="*55 + "\n")


async def main():
    print(BANNER)
    print(f"  Starting 0RB_AETHER at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    launcher = QuickLauncher()

    print("  [*] Loading modules...")
    await launcher.load_modules()
    launcher.print_status()

    print("  [*] Starting API server on http://0.0.0.0:8080")
    print("  [*] Press Ctrl+C to stop\n")

    await launcher.start_api()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n  [*] Shutdown complete")
        print("      Love - Loyalty - Honor - Everybody Eats\n")
