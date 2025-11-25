#!/usr/bin/env python3
"""
0RB_AETHER Unified Launcher
Main orchestrator connecting all system components.

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import signal
import asyncio
import socket
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

try:
    import tomllib
except ImportError:
    import tomli as tomllib

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


@dataclass
class ServiceStatus:
    """Status of a managed service"""
    name: str
    running: bool = False
    pid: Optional[int] = None
    port: Optional[int] = None
    socket_path: Optional[str] = None
    started_at: Optional[datetime] = None
    errors: list = field(default_factory=list)


class RustBrainBridge:
    """Bridge to communicate with Rust Brain Orchestrator via Unix socket"""

    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.connected = False
        self._socket: Optional[socket.socket] = None

    async def connect(self) -> bool:
        """Connect to Rust brain's Unix socket"""
        try:
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.setblocking(False)

            loop = asyncio.get_event_loop()
            await loop.sock_connect(self._socket, self.socket_path)
            self.connected = True
            return True
        except FileNotFoundError:
            return False
        except ConnectionRefusedError:
            return False
        except Exception as e:
            print(f"  [!] Bridge error: {e}")
            return False

    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict:
        """Send JSON-RPC request to Rust brain"""
        if not self.connected:
            return {"error": "Not connected to Rust brain"}

        request = {
            "jsonrpc": "2.0",
            "id": int(datetime.now().timestamp() * 1000),
            "method": method,
            "params": params or {}
        }

        try:
            loop = asyncio.get_event_loop()
            message = json.dumps(request).encode() + b'\n'
            await loop.sock_sendall(self._socket, message)

            # Read response
            data = await loop.sock_recv(self._socket, 65536)
            return json.loads(data.decode())
        except Exception as e:
            return {"error": str(e)}

    async def parse_intent(self, text: str) -> Dict:
        """Send intent parsing request"""
        return await self.send_request("parseIntent", {"text": text})

    async def get_status(self) -> Dict:
        """Get brain status"""
        return await self.send_request("getStatus")

    async def route_task(self, intent: str, complexity: float = 0.5) -> Dict:
        """Route task to appropriate AI provider"""
        return await self.send_request("routeTask", {
            "intent": intent,
            "complexity": complexity
        })

    def close(self):
        """Close connection"""
        if self._socket:
            self._socket.close()
            self.connected = False


class OrbAetherLauncher:
    """Main orchestrator for 0RB_AETHER system"""

    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        self.config: Dict = {}
        self.services: Dict[str, ServiceStatus] = {}
        self.brain_bridge: Optional[RustBrainBridge] = None
        self.running = False
        self._processes: Dict[str, subprocess.Popen] = {}

        # Load configuration
        self._load_config()

        # Initialize service statuses
        self.services = {
            "rust_brain": ServiceStatus(name="Rust Brain Orchestrator"),
            "brain_os": ServiceStatus(name="Python Brain OS"),
            "compositor": ServiceStatus(name="Wayland Compositor"),
            "voice_auth": ServiceStatus(name="Voice Authentication"),
        }

    def _load_config(self):
        """Load configuration from TOML file"""
        if self.config_path.exists():
            with open(self.config_path, 'rb') as f:
                self.config = tomllib.load(f)
            print(f"  [+] Loaded config from {self.config_path}")
        else:
            print(f"  [!] Config not found at {self.config_path}, using defaults")
            self.config = self._default_config()

    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "system": {"mode": "development", "log_level": "info"},
            "paths": {"socket": "/run/0rb/brain.sock"},
            "brain_os": {"host": "127.0.0.1", "port": 3000},
            "voice_auth": {"enabled": True},
            "demo": {"simulate_voice": True},
        }

    async def initialize(self):
        """Initialize the launcher and check prerequisites"""
        print("\n  [*] Initializing 0RB_AETHER...")

        # Ensure required directories exist
        paths = self.config.get("paths", {})
        for key in ["audit_logs", "backups"]:
            path = Path(paths.get(key, f"./{key}"))
            path.mkdir(parents=True, exist_ok=True)
            print(f"  [+] Directory ready: {path}")

        # Check socket directory
        socket_path = paths.get("socket", "/run/0rb/brain.sock")
        socket_dir = Path(socket_path).parent
        if not socket_dir.exists():
            try:
                socket_dir.mkdir(parents=True, exist_ok=True)
                print(f"  [+] Created socket directory: {socket_dir}")
            except PermissionError:
                print(f"  [!] Cannot create {socket_dir} - run with elevated permissions")

        return True

    async def start_rust_brain(self) -> bool:
        """Start the Rust Brain Orchestrator"""
        service = self.services["rust_brain"]
        rust_binary = Path("./0rb-aether/core/brain/target/release/orb-brain")
        rust_dev_binary = Path("./0rb-aether/core/brain/target/debug/orb-brain")

        # Check if binary exists
        binary = rust_binary if rust_binary.exists() else rust_dev_binary
        if not binary.exists():
            print("  [!] Rust brain not compiled. Attempting cargo build...")
            cargo_dir = Path("./0rb-aether/core/brain")
            if cargo_dir.exists():
                try:
                    result = subprocess.run(
                        ["cargo", "build", "--release"],
                        cwd=cargo_dir,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print("  [+] Rust brain compiled successfully")
                        binary = rust_binary
                    else:
                        print(f"  [!] Cargo build failed: {result.stderr}")
                        service.errors.append("Compilation failed")
                        return False
                except FileNotFoundError:
                    print("  [!] Cargo not found - Rust brain unavailable")
                    service.errors.append("Cargo not installed")
                    return False
            else:
                print(f"  [!] Rust brain source not found at {cargo_dir}")
                return False

        # Start the process
        try:
            env = os.environ.copy()
            env["ORB_SOCKET"] = self.config.get("paths", {}).get("socket", "/run/0rb/brain.sock")
            env["ORB_DB"] = self.config.get("paths", {}).get("database", "/run/0rb/brain.db")

            process = subprocess.Popen(
                [str(binary)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self._processes["rust_brain"] = process
            service.running = True
            service.pid = process.pid
            service.socket_path = env["ORB_SOCKET"]
            service.started_at = datetime.now()

            # Give it a moment to start
            await asyncio.sleep(0.5)

            # Connect bridge
            self.brain_bridge = RustBrainBridge(env["ORB_SOCKET"])
            if await self.brain_bridge.connect():
                print(f"  [+] Rust Brain started (PID: {process.pid})")
                print(f"      Socket: {env['ORB_SOCKET']}")
                return True
            else:
                print(f"  [!] Rust Brain started but socket not ready")
                return True  # Process started, socket may come up later

        except Exception as e:
            service.errors.append(str(e))
            print(f"  [!] Failed to start Rust brain: {e}")
            return False

    async def start_brain_os(self) -> bool:
        """Start the Python Brain OS FastAPI server"""
        service = self.services["brain_os"]
        brain_os_path = Path("./brain_os.py")

        if not brain_os_path.exists():
            print("  [!] brain_os.py not found")
            service.errors.append("brain_os.py not found")
            return False

        try:
            host = self.config.get("brain_os", {}).get("host", "127.0.0.1")
            port = self.config.get("brain_os", {}).get("port", 3000)

            process = subprocess.Popen(
                [sys.executable, str(brain_os_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self._processes["brain_os"] = process
            service.running = True
            service.pid = process.pid
            service.port = port
            service.started_at = datetime.now()

            # Give it a moment to start
            await asyncio.sleep(1)

            print(f"  [+] Brain OS started (PID: {process.pid})")
            print(f"      API: http://{host}:{port}")
            print(f"      Docs: http://{host}:{port}/docs")
            return True

        except Exception as e:
            service.errors.append(str(e))
            print(f"  [!] Failed to start Brain OS: {e}")
            return False

    async def start_voice_auth(self) -> bool:
        """Initialize voice authentication system"""
        service = self.services["voice_auth"]

        if not self.config.get("voice_auth", {}).get("enabled", True):
            print("  [-] Voice auth disabled in config")
            return True

        voice_auth_path = Path("./0rb-aether/tools/asr/voice_auth.py")
        if not voice_auth_path.exists():
            print("  [!] Voice auth module not found")
            service.errors.append("voice_auth.py not found")
            return False

        # Voice auth is imported/used as needed, not a daemon
        service.running = True
        service.started_at = datetime.now()
        print("  [+] Voice auth initialized (on-demand)")
        return True

    async def start_all_services(self):
        """Start all services in correct order"""
        print("\n  [*] Starting services...")

        # Start in dependency order
        await self.start_rust_brain()
        await asyncio.sleep(0.5)

        await self.start_brain_os()
        await asyncio.sleep(0.5)

        await self.start_voice_auth()

        # Print status summary
        self._print_status()

    def _print_status(self):
        """Print current service status"""
        print("\n  " + "="*55)
        print("  SERVICE STATUS")
        print("  " + "="*55)

        for name, service in self.services.items():
            status = "[RUNNING]" if service.running else "[STOPPED]"
            status_color = status
            info = ""

            if service.port:
                info = f"port:{service.port}"
            elif service.socket_path:
                info = f"socket:{Path(service.socket_path).name}"

            if service.pid:
                info = f"PID:{service.pid} " + info

            print(f"  {status:10} {service.name:25} {info}")

        print("  " + "="*55)

    async def process_intent(self, text: str) -> Dict[str, Any]:
        """Process user intent through the full pipeline"""
        result = {
            "input": text,
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }

        # Stage 1: Parse intent via Rust brain (if connected)
        if self.brain_bridge and self.brain_bridge.connected:
            intent_result = await self.brain_bridge.parse_intent(text)
            result["stages"]["intent_parse"] = intent_result

            # Stage 2: Route to AI provider
            if "result" in intent_result:
                route_result = await self.brain_bridge.route_task(
                    intent_result.get("result", {}).get("category", "general"),
                    intent_result.get("result", {}).get("confidence", 0.5)
                )
                result["stages"]["routing"] = route_result
        else:
            # Fallback: Use Python-based routing
            result["stages"]["fallback"] = "Using Python brain (Rust unavailable)"

        return result

    async def interactive_loop(self):
        """Run interactive command loop"""
        print("\n  [*] Interactive mode started")
        print("  [*] Commands: 'status', 'intent <text>', 'quit'")
        print()

        self.running = True

        while self.running:
            try:
                cmd = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input("0RB> ").strip()
                )

                if not cmd:
                    continue

                if cmd.lower() == "quit" or cmd.lower() == "exit":
                    break

                elif cmd.lower() == "status":
                    self._print_status()

                elif cmd.lower().startswith("intent "):
                    text = cmd[7:]
                    result = await self.process_intent(text)
                    print(json.dumps(result, indent=2))

                elif cmd.lower() == "help":
                    print("""
  Commands:
    status          - Show service status
    intent <text>   - Process an intent
    demo            - Run demo cycle
    quit/exit       - Shutdown and exit
                    """)

                elif cmd.lower() == "demo":
                    await self.run_demo()

                else:
                    print(f"  [?] Unknown command: {cmd}")
                    print("  [*] Type 'help' for available commands")

            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n  [*] Interrupted")
                break

    async def run_demo(self):
        """Run a demonstration of the system"""
        print("\n  " + "="*55)
        print("  0RB_AETHER DEMO")
        print("  " + "="*55)

        demo_intents = [
            "What's the system status?",
            "Build an enterprise voice AI solution",
            "Create a learning game for kids",
            "Analyze this code for security issues",
        ]

        for i, intent in enumerate(demo_intents, 1):
            print(f"\n  [{i}] Processing: \"{intent}\"")
            result = await self.process_intent(intent)
            print(f"      Result: {json.dumps(result.get('stages', {}), indent=2)[:200]}...")
            await asyncio.sleep(0.5)

        print("\n  [*] Demo complete")

    async def shutdown(self):
        """Gracefully shutdown all services"""
        print("\n  [*] Initiating shutdown...")

        # Close brain bridge
        if self.brain_bridge:
            self.brain_bridge.close()

        # Terminate all processes
        for name, process in self._processes.items():
            if process.poll() is None:  # Still running
                print(f"  [*] Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

        # Update service statuses
        for service in self.services.values():
            service.running = False

        # RAM wipe in production mode
        if self.config.get("system", {}).get("mode") == "production":
            print("  [*] Executing secure RAM wipe...")
            ram_wipe = Path("./0rb-aether/core/security/ram_wipe.sh")
            if ram_wipe.exists():
                subprocess.run(["bash", str(ram_wipe)], check=False)

        print("  [+] Shutdown complete")
        print("\n      Love - Loyalty - Honor - Everybody Eats\n")


async def main():
    """Main entry point"""
    print(BANNER)

    launcher = OrbAetherLauncher()

    # Handle signals
    def signal_handler(sig, frame):
        print("\n  [!] Signal received, shutting down...")
        asyncio.create_task(launcher.shutdown())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize
        await launcher.initialize()

        # Start services
        await launcher.start_all_services()

        # Interactive loop
        await launcher.interactive_loop()

    finally:
        await launcher.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
