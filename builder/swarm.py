#!/usr/bin/env python3
"""
BUILDER SWARM - FlowSync Prime
The complete self-building engine.

This is the keystone that unlocks infinite velocity.
Once this exists, every other layer becomes a prompt instead of a project.

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import agents
from builder.generator import CodeGenerator, GenerationRequest
from builder.tester import CodeTester
from builder.refactor import CodeRefactorer, RefactorType
from builder.security import SecurityScanner
from builder.deployer import Deployer, DeployTarget, DeployConfig


@dataclass
class SwarmTask:
    """A task for the swarm"""
    id: str
    name: str
    spec: str
    output_dir: str
    status: str = "pending"
    files_created: List[str] = field(default_factory=list)
    tests_passed: int = 0
    security_issues: int = 0
    deployed: bool = False
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class SwarmConfig:
    """Configuration for the builder swarm"""
    auto_test: bool = True
    auto_security: bool = True
    auto_refactor: bool = False
    auto_deploy: bool = False
    deploy_target: DeployTarget = DeployTarget.LOCAL
    max_retries: int = 3
    log_dir: str = "./builder/logs"


class BuilderSwarm:
    """
    The Builder Swarm - FlowSync Prime

    A team of AI agents that work together to:
    1. Generate code from natural language specs
    2. Test the generated code
    3. Scan for security issues
    4. Refactor for quality
    5. Deploy to production
    6. Monitor and self-correct

    Usage:
        swarm = BuilderSwarm()
        result = await swarm.build("Create a REST API for user management")
    """

    BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ██╗   ██╗██╗██╗     ██████╗ ███████╗██████╗        ║
║   ██╔══██╗██║   ██║██║██║     ██╔══██╗██╔════╝██╔══██╗       ║
║   ██████╔╝██║   ██║██║██║     ██║  ██║█████╗  ██████╔╝       ║
║   ██╔══██╗██║   ██║██║██║     ██║  ██║██╔══╝  ██╔══██╗       ║
║   ██████╔╝╚██████╔╝██║███████╗██████╔╝███████╗██║  ██║       ║
║   ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝       ║
║                                                               ║
║   ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗              ║
║   ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║              ║
║   ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║              ║
║   ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║              ║
║   ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║              ║
║   ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝              ║
║                                                               ║
║              FlowSync Prime - Infinite Velocity               ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
"""

    def __init__(self, config: SwarmConfig = None):
        self.config = config or SwarmConfig()

        # Initialize agents
        self.generator = CodeGenerator()
        self.tester = CodeTester()
        self.refactorer = CodeRefactorer()
        self.security = SecurityScanner()
        self.deployer = Deployer(DeployConfig(target=self.config.deploy_target))

        # Task tracking
        self.tasks: List[SwarmTask] = []
        self._task_counter = 0

        # Ensure log directory
        Path(self.config.log_dir).mkdir(parents=True, exist_ok=True)

    def _create_task(self, name: str, spec: str, output_dir: str) -> SwarmTask:
        """Create a new swarm task"""
        self._task_counter += 1
        return SwarmTask(
            id=f"swarm_{self._task_counter:04d}",
            name=name,
            spec=spec,
            output_dir=output_dir
        )

    async def build(
        self,
        spec: str,
        output_dir: str = "./generated",
        name: str = None
    ) -> SwarmTask:
        """
        Build a complete component from a natural language specification.

        This is the magic: one prompt -> complete, tested, secure module.

        Args:
            spec: Natural language description of what to build
            output_dir: Where to put the generated files
            name: Optional name for the task

        Returns:
            SwarmTask with all results
        """
        print(self.BANNER)

        task = self._create_task(
            name=name or f"Build: {spec[:50]}...",
            spec=spec,
            output_dir=output_dir
        )
        task.started_at = datetime.now()
        self.tasks.append(task)

        print(f"\n[SWARM] Task: {task.id}")
        print(f"[SWARM] Spec: {spec[:100]}...")
        print(f"[SWARM] Output: {output_dir}\n")

        try:
            # PHASE 1: Generate
            print("=" * 50)
            print("PHASE 1: GENERATION")
            print("=" * 50)

            files = await self._generate_phase(task)
            task.files_created = files
            print(f"[SWARM] Generated {len(files)} files\n")

            # PHASE 2: Test
            if self.config.auto_test and files:
                print("=" * 50)
                print("PHASE 2: TESTING")
                print("=" * 50)

                passed, failed = await self._test_phase(task)
                task.tests_passed = passed
                print(f"[SWARM] Tests: {passed} passed, {failed} failed\n")

            # PHASE 3: Security
            if self.config.auto_security and files:
                print("=" * 50)
                print("PHASE 3: SECURITY SCAN")
                print("=" * 50)

                issues = await self._security_phase(task)
                task.security_issues = issues
                print(f"[SWARM] Security issues: {issues}\n")

            # PHASE 4: Refactor (optional)
            if self.config.auto_refactor and files:
                print("=" * 50)
                print("PHASE 4: REFACTORING")
                print("=" * 50)

                await self._refactor_phase(task)
                print("[SWARM] Refactoring complete\n")

            # PHASE 5: Deploy (optional)
            if self.config.auto_deploy and files:
                print("=" * 50)
                print("PHASE 5: DEPLOYMENT")
                print("=" * 50)

                deployed = await self._deploy_phase(task)
                task.deployed = deployed
                print(f"[SWARM] Deployed: {deployed}\n")

            task.status = "completed"

        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            print(f"[SWARM] ERROR: {e}")

        task.completed_at = datetime.now()

        # Save task log
        self._save_task_log(task)

        # Print summary
        self._print_summary(task)

        return task

    async def _generate_phase(self, task: SwarmTask) -> List[str]:
        """Generate code files from spec"""
        files_created = []

        # Parse spec into components
        components = await self._parse_spec(task.spec)

        for component in components:
            request = GenerationRequest(
                description=component["description"],
                target_path=f"{task.output_dir}/{component['file']}",
                language="python"
            )

            print(f"  Generating: {component['file']}")
            result = await self.generator.generate(request)

            if result.success:
                files_created.append(result.target_path)
                print(f"    -> SUCCESS")
            else:
                print(f"    -> FAILED: {result.errors}")
                task.errors.extend(result.errors or [])

        return files_created

    async def _parse_spec(self, spec: str) -> List[Dict[str, str]]:
        """Parse specification into file components"""
        # Simple heuristic parsing
        components = []

        # Check for explicit file mentions
        if "api" in spec.lower() or "endpoint" in spec.lower():
            components.append({
                "file": "api.py",
                "description": f"API endpoints: {spec}"
            })
        if "model" in spec.lower() or "data" in spec.lower():
            components.append({
                "file": "models.py",
                "description": f"Data models: {spec}"
            })
        if "util" in spec.lower() or "helper" in spec.lower():
            components.append({
                "file": "utils.py",
                "description": f"Utilities: {spec}"
            })

        # Default to main.py if no specific components
        if not components:
            components.append({
                "file": "main.py",
                "description": spec
            })

        return components

    async def _test_phase(self, task: SwarmTask) -> tuple[int, int]:
        """Test generated files"""
        total_passed = 0
        total_failed = 0

        for file_path in task.files_created:
            if file_path.endswith('.py'):
                print(f"  Testing: {file_path}")
                result = await self.tester.validate_and_test(file_path)
                total_passed += result.get("passed", 0)
                total_failed += result.get("failed", 0)

                if result.get("success"):
                    print(f"    -> PASSED")
                else:
                    print(f"    -> ISSUES: {result.get('errors', 0)} errors")

        return total_passed, total_failed

    async def _security_phase(self, task: SwarmTask) -> int:
        """Scan for security issues"""
        total_issues = 0

        for file_path in task.files_created:
            if file_path.endswith('.py'):
                print(f"  Scanning: {file_path}")
                report = await self.security.scan_file(file_path)
                total_issues += len(report.vulnerabilities)

                if report.vulnerabilities:
                    print(f"    -> {len(report.vulnerabilities)} issues (risk: {report.risk_score:.1f})")

                    # Auto-fix if critical
                    if report.critical_count > 0:
                        print(f"    -> Attempting auto-fix...")
                        _, fixed = await self.security.fix_vulnerabilities(file_path, report)
                        print(f"    -> Fixed: {fixed}")
                else:
                    print(f"    -> CLEAN")

        return total_issues

    async def _refactor_phase(self, task: SwarmTask):
        """Refactor for quality"""
        for file_path in task.files_created:
            if file_path.endswith('.py'):
                print(f"  Refactoring: {file_path}")
                result = await self.refactorer.refactor(file_path)
                if result.improvements:
                    print(f"    -> Improvements: {', '.join(result.improvements)}")
                else:
                    print(f"    -> No changes needed")

    async def _deploy_phase(self, task: SwarmTask) -> bool:
        """Deploy the generated code"""
        for file_path in task.files_created:
            print(f"  Deploying: {file_path}")
            record = await self.deployer.deploy(file_path)
            if record.status.value == "success":
                print(f"    -> Deployed: {record.version}")
                return True
            else:
                print(f"    -> Failed: {record.errors}")

        return False

    def _save_task_log(self, task: SwarmTask):
        """Save task to log file"""
        log_path = Path(self.config.log_dir) / f"{task.id}.json"
        log_data = {
            "id": task.id,
            "name": task.name,
            "spec": task.spec,
            "output_dir": task.output_dir,
            "status": task.status,
            "files_created": task.files_created,
            "tests_passed": task.tests_passed,
            "security_issues": task.security_issues,
            "deployed": task.deployed,
            "errors": task.errors,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
        log_path.write_text(json.dumps(log_data, indent=2))

    def _print_summary(self, task: SwarmTask):
        """Print task summary"""
        duration = (task.completed_at - task.started_at).total_seconds() if task.completed_at and task.started_at else 0

        print("\n" + "=" * 50)
        print("SWARM TASK COMPLETE")
        print("=" * 50)
        print(f"  ID: {task.id}")
        print(f"  Status: {task.status.upper()}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Files Created: {len(task.files_created)}")
        print(f"  Tests Passed: {task.tests_passed}")
        print(f"  Security Issues: {task.security_issues}")
        print(f"  Deployed: {task.deployed}")
        if task.errors:
            print(f"  Errors: {len(task.errors)}")
        print("=" * 50)

    def get_stats(self) -> Dict[str, Any]:
        """Get overall swarm statistics"""
        completed = len([t for t in self.tasks if t.status == "completed"])
        failed = len([t for t in self.tasks if t.status == "failed"])

        return {
            "total_tasks": len(self.tasks),
            "completed": completed,
            "failed": failed,
            "success_rate": completed / max(1, len(self.tasks)),
            "generator": self.generator.get_stats(),
            "tester": self.tester.get_stats(),
            "security": self.security.get_stats(),
            "deployer": self.deployer.get_stats(),
        }


# CLI
async def main():
    """CLI for the Builder Swarm"""
    import argparse

    parser = argparse.ArgumentParser(description="Builder Swarm - FlowSync Prime")
    parser.add_argument("spec", nargs="?", help="What to build")
    parser.add_argument("-o", "--output", default="./generated", help="Output directory")
    parser.add_argument("-n", "--name", help="Task name")
    parser.add_argument("--no-test", action="store_true", help="Skip testing")
    parser.add_argument("--no-security", action="store_true", help="Skip security scan")
    parser.add_argument("--refactor", action="store_true", help="Enable refactoring")
    parser.add_argument("--deploy", action="store_true", help="Enable deployment")
    parser.add_argument("--demo", action="store_true", help="Run demo")

    args = parser.parse_args()

    config = SwarmConfig(
        auto_test=not args.no_test,
        auto_security=not args.no_security,
        auto_refactor=args.refactor,
        auto_deploy=args.deploy,
    )

    swarm = BuilderSwarm(config)

    if args.demo:
        # Demo mode
        spec = """
        Create a simple task queue system with:
        - Task class with id, description, priority, status
        - TaskQueue class with add, get_next, complete, list methods
        - Priority-based ordering (higher priority first)
        - JSON persistence for saving/loading
        """
        await swarm.build(spec, "./generated/task_queue", "Task Queue Demo")

    elif args.spec:
        # Build from spec
        await swarm.build(args.spec, args.output, args.name)

    else:
        # Interactive mode
        print(swarm.BANNER)
        print("\nEnter your spec (or 'quit' to exit):\n")

        while True:
            try:
                spec = input("SWARM> ").strip()
                if spec.lower() in ['quit', 'exit', 'q']:
                    break
                if spec:
                    await swarm.build(spec, args.output)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nInterrupted")
                break


if __name__ == "__main__":
    asyncio.run(main())
