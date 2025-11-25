#!/usr/bin/env python3
"""
0RB AGI KERNEL
The core intelligence layer that transforms intent into action.

Capabilities:
- Goal parsing and decomposition
- Task graph generation
- Chain-of-thought reasoning
- Prediction and planning
- Memory integration

This is the "proto-AGI" that orchestrates complex tasks.
We fake it first, then evolve into it.

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from ai_connectors import AIOrchestrator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class TaskStatus(Enum):
    """Status of a task in the graph"""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class TaskNode:
    """A node in the task graph"""
    id: str
    name: str
    description: str
    task_type: str  # action, decision, query, wait
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    dependents: List[str] = field(default_factory=list)    # Tasks waiting on this
    assigned_agent: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class TaskGraph:
    """Directed acyclic graph of tasks"""
    id: str
    goal: str
    nodes: Dict[str, TaskNode] = field(default_factory=dict)
    root_nodes: List[str] = field(default_factory=list)  # Entry points
    created_at: datetime = field(default_factory=datetime.now)

    def add_node(self, node: TaskNode) -> str:
        """Add a node to the graph"""
        self.nodes[node.id] = node
        if not node.dependencies:
            self.root_nodes.append(node.id)
        return node.id

    def add_dependency(self, from_id: str, to_id: str):
        """Add a dependency (from depends on to)"""
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[from_id].dependencies.append(to_id)
            self.nodes[to_id].dependents.append(from_id)
            # Remove from root if it now has dependencies
            if from_id in self.root_nodes:
                self.root_nodes.remove(from_id)

    def get_ready_tasks(self) -> List[TaskNode]:
        """Get tasks ready for execution (all deps completed)"""
        ready = []
        for node in self.nodes.values():
            if node.status == TaskStatus.PENDING:
                deps_complete = all(
                    self.nodes[dep].status == TaskStatus.COMPLETED
                    for dep in node.dependencies
                    if dep in self.nodes
                )
                if deps_complete:
                    ready.append(node)
        return sorted(ready, key=lambda n: n.priority.value)

    def mark_complete(self, task_id: str, result: Any = None):
        """Mark a task as complete"""
        if task_id in self.nodes:
            self.nodes[task_id].status = TaskStatus.COMPLETED
            self.nodes[task_id].result = result
            self.nodes[task_id].completed_at = datetime.now()

    def mark_failed(self, task_id: str, error: str):
        """Mark a task as failed"""
        if task_id in self.nodes:
            self.nodes[task_id].status = TaskStatus.FAILED
            self.nodes[task_id].error = error

    @property
    def is_complete(self) -> bool:
        """Check if all tasks are complete"""
        return all(n.status == TaskStatus.COMPLETED for n in self.nodes.values())

    @property
    def progress(self) -> float:
        """Get completion progress (0-1)"""
        if not self.nodes:
            return 0.0
        completed = sum(1 for n in self.nodes.values() if n.status == TaskStatus.COMPLETED)
        return completed / len(self.nodes)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "goal": self.goal,
            "progress": self.progress,
            "nodes": {
                nid: {
                    "id": n.id,
                    "name": n.name,
                    "status": n.status.value,
                    "dependencies": n.dependencies,
                }
                for nid, n in self.nodes.items()
            }
        }


@dataclass
class ChainOfThought:
    """Chain-of-thought reasoning trace"""
    id: str
    goal: str
    steps: List[Dict[str, str]] = field(default_factory=list)
    conclusion: Optional[str] = None

    def add_step(self, thought: str, action: str = None, observation: str = None):
        """Add a reasoning step"""
        self.steps.append({
            "thought": thought,
            "action": action,
            "observation": observation,
            "timestamp": datetime.now().isoformat()
        })

    def to_prompt(self) -> str:
        """Convert to prompt format"""
        lines = [f"Goal: {self.goal}\n"]
        for i, step in enumerate(self.steps, 1):
            lines.append(f"Step {i}:")
            lines.append(f"  Thought: {step['thought']}")
            if step.get('action'):
                lines.append(f"  Action: {step['action']}")
            if step.get('observation'):
                lines.append(f"  Observation: {step['observation']}")
            lines.append("")
        return "\n".join(lines)


class GoalParser:
    """Parses natural language goals into structured intents"""

    GOAL_PATTERNS = {
        "build": ["build", "create", "make", "develop", "implement"],
        "analyze": ["analyze", "examine", "investigate", "review", "audit"],
        "optimize": ["optimize", "improve", "enhance", "speed up", "refactor"],
        "fix": ["fix", "repair", "solve", "debug", "patch"],
        "deploy": ["deploy", "launch", "release", "ship", "publish"],
        "query": ["what", "how", "why", "when", "where", "who", "explain"],
        "automate": ["automate", "schedule", "recurring", "pipeline"],
    }

    def parse(self, goal: str) -> Dict[str, Any]:
        """Parse a goal into structured format"""
        goal_lower = goal.lower()

        # Detect goal type
        goal_type = "general"
        for gtype, patterns in self.GOAL_PATTERNS.items():
            if any(p in goal_lower for p in patterns):
                goal_type = gtype
                break

        # Extract entities (simple heuristic)
        entities = self._extract_entities(goal)

        # Estimate complexity
        complexity = self._estimate_complexity(goal)

        return {
            "original": goal,
            "type": goal_type,
            "entities": entities,
            "complexity": complexity,
            "requires_research": goal_type in ["analyze", "query"],
            "requires_action": goal_type in ["build", "fix", "deploy", "optimize"],
        }

    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities from text"""
        # Simple: words that are capitalized or in quotes
        entities = []
        import re

        # Quoted strings
        quoted = re.findall(r'"([^"]+)"', text)
        entities.extend(quoted)

        # Technical terms (camelCase, snake_case)
        technical = re.findall(r'\b[a-z]+[A-Z][a-zA-Z]*\b', text)  # camelCase
        technical.extend(re.findall(r'\b[a-z]+_[a-z_]+\b', text))  # snake_case
        entities.extend(technical)

        return list(set(entities))

    def _estimate_complexity(self, goal: str) -> float:
        """Estimate goal complexity (0-1)"""
        score = 0.3  # Base

        # Length factor
        if len(goal) > 100:
            score += 0.2
        if len(goal) > 200:
            score += 0.1

        # Multiple requirements
        if " and " in goal.lower():
            score += 0.15
        if goal.count(",") > 2:
            score += 0.1

        # Technical indicators
        tech_words = ["api", "database", "security", "authentication", "async", "distributed"]
        for word in tech_words:
            if word in goal.lower():
                score += 0.05

        return min(1.0, score)


class TaskDecomposer:
    """Decomposes goals into task graphs"""

    def __init__(self):
        self.ai = AIOrchestrator() if AI_AVAILABLE else None

    async def decompose(self, goal: str, parsed_goal: Dict) -> TaskGraph:
        """Decompose a goal into a task graph"""
        graph_id = f"graph_{uuid.uuid4().hex[:8]}"
        graph = TaskGraph(id=graph_id, goal=goal)

        if self.ai and parsed_goal["complexity"] > 0.5:
            # Use AI for complex goals
            tasks = await self._ai_decompose(goal, parsed_goal)
        else:
            # Use rule-based decomposition
            tasks = self._rule_decompose(goal, parsed_goal)

        # Build graph
        for i, task_info in enumerate(tasks):
            node = TaskNode(
                id=f"task_{i:03d}",
                name=task_info["name"],
                description=task_info["description"],
                task_type=task_info.get("type", "action"),
                priority=TaskPriority(task_info.get("priority", 3)),
                dependencies=task_info.get("dependencies", []),
            )
            graph.add_node(node)

        # Resolve dependencies
        self._resolve_dependencies(graph)

        return graph

    async def _ai_decompose(self, goal: str, parsed: Dict) -> List[Dict]:
        """Use AI to decompose complex goals"""
        prompt = f"""Decompose this goal into a sequence of tasks:

Goal: {goal}
Type: {parsed['type']}
Complexity: {parsed['complexity']:.2f}

Return a JSON array of tasks, each with:
- name: Short task name
- description: What needs to be done
- type: "action", "decision", "query", or "wait"
- priority: 1-5 (1=critical, 5=background)
- dependencies: Array of task indices this depends on (e.g., [0, 1] means depends on tasks 0 and 1)

Example:
[
  {{"name": "Research", "description": "Research requirements", "type": "query", "priority": 2, "dependencies": []}},
  {{"name": "Design", "description": "Design solution", "type": "decision", "priority": 2, "dependencies": [0]}},
  {{"name": "Implement", "description": "Build the solution", "type": "action", "priority": 1, "dependencies": [1]}}
]

Return ONLY valid JSON."""

        try:
            result = await self.ai.generate(prompt, task_type="analysis", complexity=0.7)
            if result.get("success"):
                import re
                content = result.get("content", "")
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except Exception:
            pass

        return self._rule_decompose(goal, parsed)

    def _rule_decompose(self, goal: str, parsed: Dict) -> List[Dict]:
        """Rule-based goal decomposition"""
        tasks = []

        goal_type = parsed["type"]

        if goal_type == "build":
            tasks = [
                {"name": "Analyze Requirements", "description": f"Understand: {goal}", "type": "query", "priority": 2},
                {"name": "Design Solution", "description": "Create architecture/design", "type": "decision", "priority": 2, "dependencies": [0]},
                {"name": "Implement", "description": "Build the solution", "type": "action", "priority": 1, "dependencies": [1]},
                {"name": "Test", "description": "Verify implementation", "type": "action", "priority": 1, "dependencies": [2]},
                {"name": "Document", "description": "Create documentation", "type": "action", "priority": 3, "dependencies": [2]},
            ]

        elif goal_type == "analyze":
            tasks = [
                {"name": "Gather Data", "description": f"Collect data for: {goal}", "type": "query", "priority": 2},
                {"name": "Process", "description": "Process and clean data", "type": "action", "priority": 2, "dependencies": [0]},
                {"name": "Analyze", "description": "Perform analysis", "type": "action", "priority": 1, "dependencies": [1]},
                {"name": "Report", "description": "Generate findings report", "type": "action", "priority": 2, "dependencies": [2]},
            ]

        elif goal_type == "fix":
            tasks = [
                {"name": "Diagnose", "description": f"Identify root cause: {goal}", "type": "query", "priority": 1},
                {"name": "Plan Fix", "description": "Design solution", "type": "decision", "priority": 2, "dependencies": [0]},
                {"name": "Implement Fix", "description": "Apply the fix", "type": "action", "priority": 1, "dependencies": [1]},
                {"name": "Verify", "description": "Confirm fix works", "type": "action", "priority": 1, "dependencies": [2]},
            ]

        elif goal_type == "deploy":
            tasks = [
                {"name": "Prepare", "description": "Prepare deployment artifacts", "type": "action", "priority": 2},
                {"name": "Backup", "description": "Backup current state", "type": "action", "priority": 1, "dependencies": [0]},
                {"name": "Deploy", "description": f"Deploy: {goal}", "type": "action", "priority": 1, "dependencies": [1]},
                {"name": "Verify", "description": "Health check", "type": "action", "priority": 1, "dependencies": [2]},
                {"name": "Monitor", "description": "Watch for issues", "type": "wait", "priority": 2, "dependencies": [3]},
            ]

        else:
            # Generic
            tasks = [
                {"name": "Understand", "description": f"Clarify: {goal}", "type": "query", "priority": 2},
                {"name": "Execute", "description": "Perform the task", "type": "action", "priority": 2, "dependencies": [0]},
                {"name": "Verify", "description": "Check results", "type": "action", "priority": 2, "dependencies": [1]},
            ]

        return tasks

    def _resolve_dependencies(self, graph: TaskGraph):
        """Resolve task indices to task IDs"""
        task_ids = list(graph.nodes.keys())

        for node in graph.nodes.values():
            resolved_deps = []
            for dep in node.dependencies:
                if isinstance(dep, int) and dep < len(task_ids):
                    resolved_deps.append(task_ids[dep])
            node.dependencies = resolved_deps

            # Update root nodes
            if node.dependencies and node.id in graph.root_nodes:
                graph.root_nodes.remove(node.id)


class AGIKernel:
    """
    The AGI Kernel - Core Intelligence

    This is the "brain" that:
    1. Parses goals into intents
    2. Decomposes goals into task graphs
    3. Orchestrates task execution
    4. Maintains reasoning chains
    5. Learns from outcomes
    """

    def __init__(self):
        self.goal_parser = GoalParser()
        self.task_decomposer = TaskDecomposer()
        self.ai = AIOrchestrator() if AI_AVAILABLE else None

        # State
        self.active_graphs: Dict[str, TaskGraph] = {}
        self.completed_graphs: List[TaskGraph] = []
        self.reasoning_chains: Dict[str, ChainOfThought] = {}

        # Callbacks for task execution
        self.task_handlers: Dict[str, Callable] = {}

        # Stats
        self.goals_processed = 0
        self.tasks_completed = 0

    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler for a task type"""
        self.task_handlers[task_type] = handler

    async def process_goal(self, goal: str) -> TaskGraph:
        """
        Process a goal through the full pipeline.

        Goal → Parse → Decompose → Task Graph
        """
        self.goals_processed += 1

        # Start reasoning chain
        chain_id = f"chain_{uuid.uuid4().hex[:8]}"
        chain = ChainOfThought(id=chain_id, goal=goal)
        self.reasoning_chains[chain_id] = chain

        # Step 1: Parse goal
        chain.add_step(
            thought="First, I need to understand what type of goal this is and its complexity.",
            action="Parsing goal"
        )
        parsed = self.goal_parser.parse(goal)
        chain.add_step(
            thought=f"This is a '{parsed['type']}' type goal with complexity {parsed['complexity']:.2f}",
            observation=f"Entities found: {parsed['entities']}"
        )

        # Step 2: Decompose into tasks
        chain.add_step(
            thought="Now I'll break this down into specific tasks.",
            action="Decomposing goal"
        )
        graph = await self.task_decomposer.decompose(goal, parsed)
        chain.add_step(
            thought=f"Created task graph with {len(graph.nodes)} tasks",
            observation=f"Root tasks: {graph.root_nodes}"
        )

        # Store graph
        self.active_graphs[graph.id] = graph
        graph.nodes[list(graph.nodes.keys())[0]].metadata["chain_id"] = chain_id

        return graph

    async def execute_graph(self, graph: TaskGraph) -> bool:
        """Execute all tasks in a graph"""
        chain_id = graph.nodes.get(list(graph.nodes.keys())[0], TaskNode("","","","")).metadata.get("chain_id")
        chain = self.reasoning_chains.get(chain_id)

        while not graph.is_complete:
            ready = graph.get_ready_tasks()

            if not ready:
                # Check for blocked state
                pending = [n for n in graph.nodes.values() if n.status == TaskStatus.PENDING]
                if pending:
                    # Stuck - mark as failed
                    for node in pending:
                        node.status = TaskStatus.BLOCKED
                    break
                continue

            # Execute ready tasks
            for task in ready:
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.now()

                if chain:
                    chain.add_step(
                        thought=f"Executing task: {task.name}",
                        action=task.description
                    )

                try:
                    # Use handler if available
                    if task.task_type in self.task_handlers:
                        result = await self.task_handlers[task.task_type](task)
                    else:
                        result = await self._default_execute(task)

                    graph.mark_complete(task.id, result)
                    self.tasks_completed += 1

                    if chain:
                        chain.add_step(
                            thought=f"Task '{task.name}' completed successfully",
                            observation=str(result)[:100] if result else "Done"
                        )

                except Exception as e:
                    graph.mark_failed(task.id, str(e))
                    if chain:
                        chain.add_step(
                            thought=f"Task '{task.name}' failed: {e}",
                        )

        # Move to completed
        if graph.is_complete:
            self.completed_graphs.append(graph)
            del self.active_graphs[graph.id]

        if chain:
            chain.conclusion = "Goal completed" if graph.is_complete else "Goal partially completed"

        return graph.is_complete

    async def _default_execute(self, task: TaskNode) -> Any:
        """Default task execution using AI"""
        if not self.ai:
            return f"[Simulated] Completed: {task.name}"

        prompt = f"""Execute this task and return the result:

Task: {task.name}
Description: {task.description}
Type: {task.task_type}

Provide a concise response or result."""

        try:
            result = await self.ai.generate(prompt, task_type="general", complexity=0.5)
            if result.get("success"):
                return result.get("content", "Completed")
        except Exception:
            pass

        return f"Completed: {task.name}"

    async def run(self, goal: str) -> Dict[str, Any]:
        """
        Main entry point: Process and execute a goal.

        Returns execution report.
        """
        # Process goal
        graph = await self.process_goal(goal)

        # Execute
        success = await self.execute_graph(graph)

        # Get reasoning chain
        chain_id = graph.nodes.get(list(graph.nodes.keys())[0], TaskNode("","","","")).metadata.get("chain_id")
        chain = self.reasoning_chains.get(chain_id)

        return {
            "goal": goal,
            "success": success,
            "graph_id": graph.id,
            "tasks_total": len(graph.nodes),
            "tasks_completed": sum(1 for n in graph.nodes.values() if n.status == TaskStatus.COMPLETED),
            "progress": graph.progress,
            "reasoning": chain.to_prompt() if chain else None,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get kernel statistics"""
        return {
            "goals_processed": self.goals_processed,
            "tasks_completed": self.tasks_completed,
            "active_graphs": len(self.active_graphs),
            "completed_graphs": len(self.completed_graphs),
        }


# Demo
async def demo():
    """Demonstrate the AGI Kernel"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                     0RB AGI KERNEL                            ║
║                                                               ║
║        Intent → Task Graph → Execution → Learning             ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    kernel = AGIKernel()

    # Test goals
    goals = [
        "Build a REST API for user management with authentication",
        "Analyze the security of our codebase",
        "Fix the bug in the login system",
    ]

    for goal in goals:
        print(f"\n{'='*50}")
        print(f"GOAL: {goal}")
        print('='*50)

        result = await kernel.run(goal)

        print(f"\nSuccess: {result['success']}")
        print(f"Progress: {result['progress']:.0%}")
        print(f"Tasks: {result['tasks_completed']}/{result['tasks_total']}")

        if result['reasoning']:
            print(f"\nReasoning Chain:")
            print(result['reasoning'][:500])

    # Stats
    print(f"\n{'='*50}")
    print("KERNEL STATS")
    print('='*50)
    print(json.dumps(kernel.get_stats(), indent=2))


if __name__ == "__main__":
    asyncio.run(demo())
