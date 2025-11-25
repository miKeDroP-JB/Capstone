"""
CONSTRAINT MUTATOR - The Anti-Framework Engine
═══════════════════════════════════════════════════════════════
Constantly changing rules, removing capabilities, flipping objectives.
This is FORCED EVOLUTION. We don't wait for emergence—we DEMAND it.

"Here's a system that BREAKS frameworks to force pattern discovery."
- Constraint mutation
- Objective inversion
- Tool occlusion
- Cross-domain transfer
═══════════════════════════════════════════════════════════════
"""

import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class MutationType(Enum):
    """Types of mutations that can be applied"""
    ADD_CONSTRAINT = "add_constraint"           # Add new constraint
    REMOVE_CONSTRAINT = "remove_constraint"     # Remove existing constraint
    MODIFY_CONSTRAINT = "modify_constraint"     # Change constraint parameters
    INVERT_OBJECTIVE = "invert_objective"       # Flip the goal
    OCCLUDE_TOOL = "occlude_tool"               # Remove a capability
    ADD_RESOURCE = "add_resource"               # Provide new resource
    TIME_PRESSURE = "time_pressure"             # Reduce time limit
    SCOPE_EXPANSION = "scope_expansion"         # Increase scope
    DOMAIN_SHIFT = "domain_shift"               # Change problem domain
    ADVERSARIAL_INJECTION = "adversarial"       # Add adversarial element


@dataclass
class Mutation:
    """Record of a mutation applied to a task"""
    mutation_id: str
    mutation_type: MutationType
    description: str
    before: Dict[str, Any]
    after: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "type": self.mutation_type.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat()
        }


class ConstraintMutator:
    """
    The Constraint Mutator - forces adaptation through continuous change.

    The anti-framework philosophy:
    - Traditional: Follow rules → Learn patterns → Apply patterns
    - Forge: Break rules → Discover meta-patterns → Generate new rules

    Mutation strategies:
    - Gradual escalation (slowly increase difficulty)
    - Shock therapy (sudden dramatic change)
    - Oscillation (alternate between states)
    - Inversion (flip assumptions)
    """

    # New constraints that can be added
    INJECTABLE_CONSTRAINTS = [
        "Must work offline",
        "Must be reversible",
        "Must complete in half the time",
        "Must use no external dependencies",
        "Must handle 10x the expected load",
        "Must work with corrupted input",
        "Must produce human-readable output",
        "Must be explainable",
        "Must maintain backward compatibility",
        "Must support real-time updates",
        "Must work across time zones",
        "Must handle concurrent modifications",
        "Must be idempotent",
        "Must support rollback",
        "Must log all operations",
    ]

    # Constraint modifiers
    CONSTRAINT_MODIFIERS = [
        ("time", lambda x: f"{x} in half the time"),
        ("scale", lambda x: f"{x} at 10x scale"),
        ("quality", lambda x: f"{x} with 99.9% accuracy"),
        ("cost", lambda x: f"{x} at 50% cost"),
        ("security", lambda x: f"{x} with end-to-end encryption"),
    ]

    # Objective inversions
    INVERSION_PATTERNS = [
        ("maximize", "minimize"),
        ("increase", "decrease"),
        ("add", "remove"),
        ("build", "deconstruct"),
        ("simplify", "elaborate"),
        ("speed up", "ensure correctness"),
        ("reduce cost", "maximize value"),
    ]

    # Tools that can be occluded
    OCCLUDABLE_TOOLS = [
        "documentation",
        "examples",
        "external APIs",
        "caching",
        "logging",
        "testing framework",
        "type checking",
        "IDE support",
        "version control",
        "deployment tools",
    ]

    def __init__(self, mutation_rate: float = 0.15):
        self.mutation_rate = mutation_rate
        self.mutation_history: List[Mutation] = []
        self.mutation_count = 0

    def mutate(self, task: 'Task') -> 'Task':
        """
        Mutate a task to force adaptation.

        Returns a new task with mutations applied.
        """
        if random.random() > self.mutation_rate:
            return task  # No mutation this time

        # Select mutation type
        mutation_type = self._select_mutation_type(task)

        # Apply mutation
        mutated_task, mutation = self._apply_mutation(task, mutation_type)

        # Record mutation
        self.mutation_history.append(mutation)
        self.mutation_count += 1

        return mutated_task

    def _select_mutation_type(self, task: 'Task') -> MutationType:
        """Select appropriate mutation type based on task state"""
        # Weight selection based on task characteristics
        weights = {
            MutationType.ADD_CONSTRAINT: 3,
            MutationType.MODIFY_CONSTRAINT: 2 if task.constraints else 0,
            MutationType.REMOVE_CONSTRAINT: 1 if len(task.constraints) > 1 else 0,
            MutationType.INVERT_OBJECTIVE: 1,
            MutationType.OCCLUDE_TOOL: 2 if task.resources_available else 0,
            MutationType.TIME_PRESSURE: 2 if task.time_limit_seconds and task.time_limit_seconds > 60 else 0,
            MutationType.SCOPE_EXPANSION: 1,
            MutationType.ADVERSARIAL_INJECTION: 2,
        }

        # Filter to non-zero weights
        options = [(t, w) for t, w in weights.items() if w > 0]
        total = sum(w for _, w in options)

        if total == 0:
            return MutationType.ADD_CONSTRAINT

        # Weighted random selection
        r = random.random() * total
        cumulative = 0
        for mutation_type, weight in options:
            cumulative += weight
            if r <= cumulative:
                return mutation_type

        return MutationType.ADD_CONSTRAINT

    def _apply_mutation(
        self,
        task: 'Task',
        mutation_type: MutationType
    ) -> tuple['Task', Mutation]:
        """Apply a specific mutation to the task"""
        from .curriculum import Task, Difficulty  # Import here to avoid circular

        before_state = task.to_dict()

        # Create modified task
        new_constraints = list(task.constraints)
        new_objective = task.objective
        new_time_limit = task.time_limit_seconds
        new_resources = list(task.resources_available) if task.resources_available else []
        new_difficulty = task.difficulty
        description = ""

        if mutation_type == MutationType.ADD_CONSTRAINT:
            new_constraint = random.choice(self.INJECTABLE_CONSTRAINTS)
            new_constraints.append(new_constraint)
            description = f"Added constraint: {new_constraint}"

        elif mutation_type == MutationType.REMOVE_CONSTRAINT:
            if new_constraints:
                removed = new_constraints.pop(random.randint(0, len(new_constraints) - 1))
                description = f"Removed constraint: {removed}"

        elif mutation_type == MutationType.MODIFY_CONSTRAINT:
            if new_constraints:
                idx = random.randint(0, len(new_constraints) - 1)
                modifier_name, modifier_fn = random.choice(self.CONSTRAINT_MODIFIERS)
                new_constraints[idx] = modifier_fn(new_constraints[idx])
                description = f"Modified constraint with {modifier_name}"

        elif mutation_type == MutationType.INVERT_OBJECTIVE:
            for old, new in self.INVERSION_PATTERNS:
                if old in new_objective.lower():
                    new_objective = new_objective.lower().replace(old, new)
                    description = f"Inverted objective: {old} → {new}"
                    break
            else:
                new_objective = f"[INVERTED] {new_objective}"
                description = "Inverted objective direction"

        elif mutation_type == MutationType.OCCLUDE_TOOL:
            if new_resources:
                occluded = new_resources.pop(random.randint(0, len(new_resources) - 1))
                description = f"Occluded tool: {occluded}"
            else:
                occluded = random.choice(self.OCCLUDABLE_TOOLS)
                new_constraints.append(f"Cannot use {occluded}")
                description = f"Blocked tool: {occluded}"

        elif mutation_type == MutationType.TIME_PRESSURE:
            if new_time_limit:
                new_time_limit = max(30, new_time_limit // 2)
                description = f"Time pressure: reduced to {new_time_limit}s"

        elif mutation_type == MutationType.SCOPE_EXPANSION:
            new_objective = f"{new_objective} AND handle edge cases"
            new_constraints.append("Must document all assumptions")
            description = "Expanded scope with edge case handling"

        elif mutation_type == MutationType.ADVERSARIAL_INJECTION:
            adversarial_constraints = [
                "Must handle malicious input",
                "Must survive Byzantine failures",
                "Must work under resource starvation",
                "Must handle network partitions",
            ]
            new_constraint = random.choice(adversarial_constraints)
            new_constraints.append(new_constraint)
            description = f"Adversarial injection: {new_constraint}"

        # Potentially increase difficulty
        if mutation_type in [MutationType.ADVERSARIAL_INJECTION, MutationType.TIME_PRESSURE]:
            new_difficulty = Difficulty(min(6, task.difficulty.value + 1))

        # Create mutated task
        mutated_task = Task(
            task_id=f"{task.task_id}_mut{self.mutation_count}",
            task_type=task.task_type,
            objective=new_objective,
            constraints=new_constraints,
            success_criteria=task.success_criteria,
            difficulty=new_difficulty,
            context={**task.context, "mutation_applied": mutation_type.value},
            time_limit_seconds=new_time_limit,
            resources_available=new_resources
        )

        after_state = mutated_task.to_dict()

        mutation = Mutation(
            mutation_id=f"mut_{uuid4().hex[:8]}",
            mutation_type=mutation_type,
            description=description,
            before=before_state,
            after=after_state,
            timestamp=datetime.utcnow()
        )

        return mutated_task, mutation

    def shock_therapy(self, task: 'Task') -> 'Task':
        """Apply multiple mutations at once for dramatic change"""
        mutated = task
        for _ in range(3):
            self.mutation_rate = 1.0  # Force mutation
            mutated = self.mutate(mutated)
        self.mutation_rate = 0.15  # Reset
        return mutated

    def invert_everything(self, task: 'Task') -> 'Task':
        """Completely invert a task - the ultimate anti-framework move"""
        from .curriculum import Task, Difficulty

        inverted_objective = f"[TOTAL INVERSION] Do the OPPOSITE of: {task.objective}"

        # Invert constraints
        inverted_constraints = [f"MUST NOT: {c}" for c in task.constraints]

        # Invert success criteria
        inverted_criteria = f"Succeed by doing the opposite: {task.success_criteria}"

        return Task(
            task_id=f"{task.task_id}_inverted",
            task_type=task.task_type,
            objective=inverted_objective,
            constraints=inverted_constraints,
            success_criteria=inverted_criteria,
            difficulty=Difficulty.IMPOSSIBLE,
            context={"original_task_id": task.task_id, "totally_inverted": True}
        )

    def get_mutation_statistics(self) -> Dict[str, Any]:
        """Get statistics about mutations applied"""
        type_counts = {}
        for mutation in self.mutation_history:
            t = mutation.mutation_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total_mutations": self.mutation_count,
            "mutation_rate": self.mutation_rate,
            "mutations_by_type": type_counts,
            "recent_mutations": [m.to_dict() for m in self.mutation_history[-5:]]
        }
