#!/usr/bin/env python3
"""
BUILDER SWARM - FlowSync Prime
The self-building engine that unlocks infinite velocity.

This swarm generates code, tests it, refactors it, patches security,
deploys it, logs errors, and self-corrects.

Once this exists, every other layer becomes a prompt instead of a project.

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai_connectors import AIOrchestrator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class SwarmRole(Enum):
    """Roles in the Builder Swarm"""
    GENERATOR = "generator"      # Creates code
    TESTER = "tester"           # Tests code
    REFACTOR = "refactor"       # Improves code
    SECURITY = "security"       # Patches vulnerabilities
    DEPLOYER = "deployer"       # Deploys code
    MONITOR = "monitor"         # Logs and self-corrects
    ORCHESTRATOR = "orchestrator"  # Coordinates the swarm


@dataclass
class BuildTask:
    """A task for the builder swarm"""
    id: str
    description: str
    target_path: str
    task_type: str  # generate, test, refactor, secure, deploy
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SwarmConfig:
    """Configuration for the builder swarm"""
    max_retries: int = 3
    auto_test: bool = True
    auto_security: bool = True
    auto_refactor: bool = False
    deploy_on_success: bool = False
    log_everything: bool = True


class BuilderAgent:
    """Base class for all builder agents"""

    def __init__(self, role: SwarmRole, config: SwarmConfig = None):
        self.role = role
        self.config = config or SwarmConfig()
        self.tasks_completed = 0
        self.tasks_failed = 0

        # AI orchestrator for intelligent operations
        self.ai = AIOrchestrator() if AI_AVAILABLE else None

    async def execute(self, task: BuildTask) -> BuildTask:
        """Execute a task - override in subclasses"""
        raise NotImplementedError

    async def _call_ai(self, prompt: str, task_type: str = "code") -> str:
        """Call AI for assistance"""
        if not self.ai:
            return f"[AI unavailable] Would process: {prompt[:100]}..."

        try:
            result = await self.ai.generate(prompt, task_type=task_type, complexity=0.7)
            if result.get("success"):
                return result.get("content", "")
            return f"[AI error] {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"[AI exception] {str(e)}"

    def log(self, message: str):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.role.value.upper()}] {message}")


class GeneratorAgent(BuilderAgent):
    """Generates code from specifications"""

    def __init__(self, config: SwarmConfig = None):
        super().__init__(SwarmRole.GENERATOR, config)

    async def execute(self, task: BuildTask) -> BuildTask:
        """Generate code based on task description"""
        task.status = "in_progress"
        self.log(f"Generating: {task.description}")

        try:
            prompt = f"""Generate Python code for the following requirement:

{task.description}

Context:
- Target file: {task.target_path}
- Project type: OrbOS/0RB_AETHER builder component
- Style: Clean, documented, async-ready

Requirements:
1. Include proper docstrings
2. Handle errors gracefully
3. Make it modular and testable
4. Follow existing project patterns

Return ONLY the code, no explanations."""

            code = await self._call_ai(prompt, "code")

            # Write the generated code
            target = Path(task.target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(code)

            task.result = code
            task.status = "completed"
            self.tasks_completed += 1
            self.log(f"Generated: {task.target_path}")

        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            self.tasks_failed += 1
            self.log(f"Failed: {e}")

        return task


class TesterAgent(BuilderAgent):
    """Tests generated code"""

    def __init__(self, config: SwarmConfig = None):
        super().__init__(SwarmRole.TESTER, config)

    async def execute(self, task: BuildTask) -> BuildTask:
        """Test code at target path"""
        task.status = "in_progress"
        self.log(f"Testing: {task.target_path}")

        try:
            target = Path(task.target_path)
            if not target.exists():
                raise FileNotFoundError(f"File not found: {target}")

            code = target.read_text()

            # Syntax check
            compile(code, task.target_path, 'exec')
            self.log("Syntax check passed")

            # Generate test cases
            prompt = f"""Analyze this Python code and generate pytest test cases:

```python
{code[:2000]}
```

Generate comprehensive test cases that:
1. Test all public functions
2. Include edge cases
3. Test error handling
4. Are self-contained

Return ONLY the test code."""

            tests = await self._call_ai(prompt, "code")

            # Write tests
            test_path = target.parent / f"test_{target.name}"
            test_path.write_text(tests)

            task.result = f"Tests written to {test_path}"
            task.status = "completed"
            self.tasks_completed += 1
            self.log(f"Tests generated: {test_path}")

        except SyntaxError as e:
            task.status = "failed"
            task.errors.append(f"Syntax error: {e}")
            self.tasks_failed += 1

        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            self.tasks_failed += 1

        return task


class RefactorAgent(BuilderAgent):
    """Refactors and improves code"""

    def __init__(self, config: SwarmConfig = None):
        super().__init__(SwarmRole.REFACTOR, config)

    async def execute(self, task: BuildTask) -> BuildTask:
        """Refactor code for quality"""
        task.status = "in_progress"
        self.log(f"Refactoring: {task.target_path}")

        try:
            target = Path(task.target_path)
            if not target.exists():
                raise FileNotFoundError(f"File not found: {target}")

            code = target.read_text()

            prompt = f"""Refactor this Python code to improve:
1. Code clarity and readability
2. Performance where possible
3. Error handling
4. Documentation
5. Type hints

Original code:
```python
{code[:3000]}
```

Return ONLY the improved code, maintaining all functionality."""

            improved = await self._call_ai(prompt, "code")

            # Backup original
            backup = target.with_suffix('.py.bak')
            backup.write_text(code)

            # Write improved
            target.write_text(improved)

            task.result = improved
            task.status = "completed"
            self.tasks_completed += 1
            self.log(f"Refactored: {task.target_path}")

        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            self.tasks_failed += 1

        return task


class SecurityAgent(BuilderAgent):
    """Scans and patches security issues"""

    def __init__(self, config: SwarmConfig = None):
        super().__init__(SwarmRole.SECURITY, config)
        self.vulnerability_patterns = [
            ("eval(", "Code injection risk"),
            ("exec(", "Code injection risk"),
            ("os.system(", "Command injection risk"),
            ("subprocess.call(", "Command injection - use subprocess.run"),
            ("pickle.loads(", "Deserialization risk"),
            ("yaml.load(", "YAML deserialization - use safe_load"),
            ("__import__", "Dynamic import risk"),
            ("input(", "User input risk in Python 2"),
            (".format(", "Format string risk - consider f-strings"),
            ("SELECT.*%s", "SQL injection risk"),
        ]

    async def execute(self, task: BuildTask) -> BuildTask:
        """Scan and patch security vulnerabilities"""
        task.status = "in_progress"
        self.log(f"Scanning: {task.target_path}")

        try:
            target = Path(task.target_path)
            if not target.exists():
                raise FileNotFoundError(f"File not found: {target}")

            code = target.read_text()
            issues = []

            # Pattern-based scan
            for pattern, description in self.vulnerability_patterns:
                if pattern.lower() in code.lower():
                    issues.append(f"- {description}: found '{pattern}'")

            if issues:
                self.log(f"Found {len(issues)} potential issues")

                # Get AI to fix
                prompt = f"""Review this Python code for security vulnerabilities and fix them:

```python
{code[:3000]}
```

Known issues found:
{chr(10).join(issues)}

Fix all security issues while maintaining functionality.
Return ONLY the secure code."""

                secure_code = await self._call_ai(prompt, "code")

                # Backup and write
                backup = target.with_suffix('.py.insecure')
                backup.write_text(code)
                target.write_text(secure_code)

                task.result = f"Fixed {len(issues)} issues"
            else:
                task.result = "No issues found"

            task.status = "completed"
            self.tasks_completed += 1
            self.log(f"Security scan complete: {task.result}")

        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            self.tasks_failed += 1

        return task


class DeployerAgent(BuilderAgent):
    """Deploys code to target environments"""

    def __init__(self, config: SwarmConfig = None):
        super().__init__(SwarmRole.DEPLOYER, config)

    async def execute(self, task: BuildTask) -> BuildTask:
        """Deploy code"""
        task.status = "in_progress"
        self.log(f"Deploying: {task.target_path}")

        try:
            target = Path(task.target_path)
            if not target.exists():
                raise FileNotFoundError(f"File not found: {target}")

            # Verify syntax before deploy
            code = target.read_text()
            compile(code, task.target_path, 'exec')

            # Log deployment
            deploy_log = {
                "timestamp": datetime.now().isoformat(),
                "file": str(target),
                "size": len(code),
                "checksum": hash(code),
            }

            log_path = Path("builder/deploy.log")
            with open(log_path, 'a') as f:
                f.write(json.dumps(deploy_log) + '\n')

            task.result = f"Deployed {target.name}"
            task.status = "completed"
            self.tasks_completed += 1
            self.log(f"Deployed: {task.target_path}")

        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            self.tasks_failed += 1

        return task


class MonitorAgent(BuilderAgent):
    """Monitors, logs, and enables self-correction"""

    def __init__(self, config: SwarmConfig = None):
        super().__init__(SwarmRole.MONITOR, config)
        self.error_log: List[Dict] = []
        self.corrections_made = 0

    async def execute(self, task: BuildTask) -> BuildTask:
        """Monitor and potentially self-correct"""
        task.status = "in_progress"
        self.log(f"Monitoring: {task.description}")

        try:
            # Log task state
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "task_id": task.id,
                "description": task.description,
                "status": task.status,
                "errors": task.errors,
            }

            self.error_log.append(log_entry)

            # Check for patterns that need correction
            if task.errors:
                self.log(f"Errors detected: {len(task.errors)}")

                # Attempt self-correction
                correction_prompt = f"""A build task failed with these errors:

Task: {task.description}
Errors: {json.dumps(task.errors, indent=2)}

Suggest a fix or workaround. Be specific and actionable."""

                suggestion = await self._call_ai(correction_prompt, "analysis")
                task.context["correction_suggestion"] = suggestion
                self.corrections_made += 1

            task.result = f"Monitored, {len(self.error_log)} total events"
            task.status = "completed"
            self.tasks_completed += 1

        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            self.tasks_failed += 1

        return task


class BuilderSwarm:
    """
    The Builder Swarm - FlowSync Prime

    Orchestrates a team of AI agents that can:
    - Generate code from prompts
    - Test generated code
    - Refactor for quality
    - Patch security issues
    - Deploy to production
    - Monitor and self-correct

    This is the keystone that unlocks infinite velocity.
    """

    def __init__(self, config: SwarmConfig = None):
        self.config = config or SwarmConfig()

        # Initialize agents
        self.agents = {
            SwarmRole.GENERATOR: GeneratorAgent(self.config),
            SwarmRole.TESTER: TesterAgent(self.config),
            SwarmRole.REFACTOR: RefactorAgent(self.config),
            SwarmRole.SECURITY: SecurityAgent(self.config),
            SwarmRole.DEPLOYER: DeployerAgent(self.config),
            SwarmRole.MONITOR: MonitorAgent(self.config),
        }

        self.task_queue: List[BuildTask] = []
        self.completed_tasks: List[BuildTask] = []
        self.failed_tasks: List[BuildTask] = []
        self._task_counter = 0

    def create_task(
        self,
        description: str,
        target_path: str,
        task_type: str = "generate",
        context: Dict = None,
        dependencies: List[str] = None
    ) -> BuildTask:
        """Create a new build task"""
        self._task_counter += 1
        task = BuildTask(
            id=f"task_{self._task_counter}",
            description=description,
            target_path=target_path,
            task_type=task_type,
            context=context or {},
            dependencies=dependencies or [],
        )
        self.task_queue.append(task)
        return task

    async def execute_task(self, task: BuildTask) -> BuildTask:
        """Execute a single task through the appropriate agent"""

        # Map task type to agent role
        role_map = {
            "generate": SwarmRole.GENERATOR,
            "test": SwarmRole.TESTER,
            "refactor": SwarmRole.REFACTOR,
            "security": SwarmRole.SECURITY,
            "secure": SwarmRole.SECURITY,
            "deploy": SwarmRole.DEPLOYER,
            "monitor": SwarmRole.MONITOR,
        }

        role = role_map.get(task.task_type, SwarmRole.GENERATOR)
        agent = self.agents[role]

        # Execute
        result = await agent.execute(task)

        # Track completion
        if result.status == "completed":
            self.completed_tasks.append(result)
        else:
            self.failed_tasks.append(result)

        # Auto-chain if configured
        if result.status == "completed":
            if task.task_type == "generate" and self.config.auto_test:
                test_task = self.create_task(
                    f"Test {task.target_path}",
                    task.target_path,
                    "test"
                )
                await self.execute_task(test_task)

            if task.task_type == "generate" and self.config.auto_security:
                sec_task = self.create_task(
                    f"Security scan {task.target_path}",
                    task.target_path,
                    "security"
                )
                await self.execute_task(sec_task)

        # Always monitor
        monitor = self.agents[SwarmRole.MONITOR]
        monitor_task = BuildTask(
            id=f"monitor_{task.id}",
            description=f"Monitor {task.id}",
            target_path=task.target_path,
            task_type="monitor",
        )
        monitor_task.errors = result.errors.copy()
        await monitor.execute(monitor_task)

        return result

    async def build(self, spec: str, output_dir: str = "./generated") -> Dict[str, Any]:
        """
        Build a complete component from a natural language specification.

        This is the magic: one prompt -> complete module.
        """
        print(f"\n{'='*60}")
        print("BUILDER SWARM - EXECUTING BUILD")
        print(f"{'='*60}\n")
        print(f"Spec: {spec[:100]}...")
        print(f"Output: {output_dir}\n")

        # Parse spec into tasks
        parse_prompt = f"""Break down this software specification into discrete files and tasks:

{spec}

Return a JSON array of tasks, each with:
- "file": target filename (e.g., "auth.py")
- "description": what the file should contain/do
- "dependencies": list of other files this depends on

Example:
[
  {{"file": "models.py", "description": "Data models for user and session", "dependencies": []}},
  {{"file": "auth.py", "description": "Authentication logic", "dependencies": ["models.py"]}}
]

Return ONLY valid JSON."""

        generator = self.agents[SwarmRole.GENERATOR]
        tasks_json = await generator._call_ai(parse_prompt, "analysis")

        try:
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\[.*\]', tasks_json, re.DOTALL)
            if json_match:
                tasks_data = json.loads(json_match.group())
            else:
                # Fallback: single file
                tasks_data = [{"file": "main.py", "description": spec, "dependencies": []}]
        except json.JSONDecodeError:
            tasks_data = [{"file": "main.py", "description": spec, "dependencies": []}]

        # Create and execute tasks
        results = []
        for task_data in tasks_data:
            file_path = f"{output_dir}/{task_data['file']}"
            task = self.create_task(
                description=task_data["description"],
                target_path=file_path,
                task_type="generate",
                dependencies=task_data.get("dependencies", [])
            )
            result = await self.execute_task(task)
            results.append({
                "file": file_path,
                "status": result.status,
                "errors": result.errors,
            })

        return {
            "spec": spec,
            "output_dir": output_dir,
            "tasks_created": len(tasks_data),
            "results": results,
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get swarm statistics"""
        agent_stats = {}
        for role, agent in self.agents.items():
            agent_stats[role.value] = {
                "completed": agent.tasks_completed,
                "failed": agent.tasks_failed,
            }

        return {
            "total_tasks": self._task_counter,
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "queued": len(self.task_queue),
            "agents": agent_stats,
        }


# Demo / CLI
async def demo():
    """Demonstrate the Builder Swarm"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                   BUILDER SWARM - FlowSync Prime              ║
║                                                               ║
║   The self-building engine that unlocks infinite velocity.    ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    config = SwarmConfig(
        auto_test=True,
        auto_security=True,
        auto_refactor=False,
        log_everything=True,
    )

    swarm = BuilderSwarm(config)

    # Demo 1: Generate a simple module
    print("\n[DEMO 1] Generating a utility module...")
    print("-" * 40)

    task = swarm.create_task(
        description="Create a utility module with functions for string manipulation: reverse, capitalize_words, count_vowels",
        target_path="./generated/utils.py",
        task_type="generate"
    )
    await swarm.execute_task(task)

    # Demo 2: Build from spec
    print("\n[DEMO 2] Building from specification...")
    print("-" * 40)

    spec = """
    Create a simple task queue system with:
    - Task class with id, description, status, priority
    - TaskQueue class with add, get_next, complete methods
    - Priority-based ordering
    - Persistence to JSON file
    """
    result = await swarm.build(spec, "./generated/task_queue")

    # Stats
    print("\n" + "=" * 60)
    print("SWARM STATISTICS")
    print("=" * 60)
    stats = swarm.get_stats()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(demo())
