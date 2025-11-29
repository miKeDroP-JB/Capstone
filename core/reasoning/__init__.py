#!/usr/bin/env python3
"""
0RB REASONING ENGINE
Symbolic reasoning, logic engine, and planning system.

Components:
- Symbolic Rules: If-then rules for deterministic logic
- Logic Engine: Inference and deduction
- Planner: Goal-directed action planning

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class RuleCondition(Enum):
    """Types of rule conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN_LIST = "in_list"
    MATCHES = "matches"  # regex
    EXISTS = "exists"


@dataclass
class Rule:
    """A symbolic if-then rule"""
    id: str
    name: str
    description: str
    conditions: List[Tuple[str, RuleCondition, Any]]  # (variable, condition, value)
    actions: List[Dict[str, Any]]
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Check if all conditions are met"""
        for var, condition, value in self.conditions:
            actual = context.get(var)

            if condition == RuleCondition.EQUALS:
                if actual != value:
                    return False

            elif condition == RuleCondition.NOT_EQUALS:
                if actual == value:
                    return False

            elif condition == RuleCondition.CONTAINS:
                if not (actual and value in str(actual)):
                    return False

            elif condition == RuleCondition.GREATER_THAN:
                if not (actual and actual > value):
                    return False

            elif condition == RuleCondition.LESS_THAN:
                if not (actual and actual < value):
                    return False

            elif condition == RuleCondition.IN_LIST:
                if actual not in value:
                    return False

            elif condition == RuleCondition.MATCHES:
                if not (actual and re.match(value, str(actual))):
                    return False

            elif condition == RuleCondition.EXISTS:
                if (value and actual is None) or (not value and actual is not None):
                    return False

        return True


class SymbolicRules:
    """
    Rule-based reasoning system.
    Manages and executes symbolic if-then rules.
    """

    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.rule_categories: Dict[str, List[str]] = {}
        self._rule_counter = 0

        # Load default rules
        self._load_default_rules()

    def _load_default_rules(self):
        """Load built-in rules"""
        # Security rules
        self.add_rule(
            name="Block Dangerous Operations",
            description="Block potentially dangerous system operations",
            conditions=[
                ("action_type", RuleCondition.IN_LIST, ["delete_all", "format", "rm_rf", "shutdown"]),
                ("user_confirmed", RuleCondition.EQUALS, False)
            ],
            actions=[{"type": "block", "reason": "Dangerous operation requires confirmation"}],
            priority=100,
            category="security"
        )

        # Cost control rules
        self.add_rule(
            name="Budget Warning",
            description="Warn when approaching budget limit",
            conditions=[
                ("budget_percent", RuleCondition.GREATER_THAN, 80)
            ],
            actions=[{"type": "warn", "message": "Approaching budget limit"}],
            priority=50,
            category="cost"
        )

        # Quality rules
        self.add_rule(
            name="Require Tests",
            description="Require tests for production code",
            conditions=[
                ("target_env", RuleCondition.EQUALS, "production"),
                ("has_tests", RuleCondition.EQUALS, False)
            ],
            actions=[{"type": "block", "reason": "Production deployment requires tests"}],
            priority=80,
            category="quality"
        )

    def add_rule(
        self,
        name: str,
        description: str,
        conditions: List[Tuple[str, RuleCondition, Any]],
        actions: List[Dict[str, Any]],
        priority: int = 0,
        category: str = "general"
    ) -> str:
        """Add a new rule"""
        self._rule_counter += 1
        rule_id = f"rule_{self._rule_counter:04d}"

        rule = Rule(
            id=rule_id,
            name=name,
            description=description,
            conditions=conditions,
            actions=actions,
            priority=priority
        )

        self.rules[rule_id] = rule

        if category not in self.rule_categories:
            self.rule_categories[category] = []
        self.rule_categories[category].append(rule_id)

        return rule_id

    def evaluate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all rules against context.
        Returns list of triggered actions.
        """
        triggered = []

        # Sort by priority (higher first)
        sorted_rules = sorted(
            [r for r in self.rules.values() if r.enabled],
            key=lambda r: r.priority,
            reverse=True
        )

        for rule in sorted_rules:
            if rule.evaluate_conditions(context):
                for action in rule.actions:
                    triggered.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        **action
                    })

        return triggered

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID"""
        return self.rules.get(rule_id)

    def disable_rule(self, rule_id: str):
        """Disable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False

    def enable_rule(self, rule_id: str):
        """Enable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True


@dataclass
class Fact:
    """A logical fact"""
    predicate: str
    arguments: Tuple[str, ...]
    confidence: float = 1.0
    source: str = "asserted"
    timestamp: datetime = field(default_factory=datetime.now)

    def __hash__(self):
        return hash((self.predicate, self.arguments))

    def __eq__(self, other):
        return self.predicate == other.predicate and self.arguments == other.arguments

    def __str__(self):
        args = ", ".join(self.arguments)
        return f"{self.predicate}({args})"


@dataclass
class Inference:
    """An inference rule for logical deduction"""
    name: str
    premises: List[str]  # Pattern like "parent(X, Y)"
    conclusion: str      # Pattern like "ancestor(X, Y)"

    def match(self, facts: Set[Fact]) -> List[Dict[str, str]]:
        """Find all variable bindings that satisfy premises"""
        # Simple pattern matching
        bindings_list = [{}]

        for premise in self.premises:
            new_bindings_list = []
            pred, args_str = self._parse_pattern(premise)

            for bindings in bindings_list:
                for fact in facts:
                    if fact.predicate == pred:
                        new_bindings = self._try_match(args_str, fact.arguments, bindings)
                        if new_bindings is not None:
                            new_bindings_list.append(new_bindings)

            bindings_list = new_bindings_list

        return bindings_list

    def _parse_pattern(self, pattern: str) -> Tuple[str, List[str]]:
        """Parse pattern like 'predicate(arg1, arg2)'"""
        match = re.match(r'(\w+)\(([^)]*)\)', pattern)
        if match:
            pred = match.group(1)
            args = [a.strip() for a in match.group(2).split(',')]
            return pred, args
        return pattern, []

    def _try_match(self, pattern_args: List[str], fact_args: Tuple[str, ...],
                   bindings: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Try to match pattern args with fact args"""
        if len(pattern_args) != len(fact_args):
            return None

        new_bindings = bindings.copy()

        for p_arg, f_arg in zip(pattern_args, fact_args):
            if p_arg.isupper():  # Variable
                if p_arg in new_bindings:
                    if new_bindings[p_arg] != f_arg:
                        return None
                else:
                    new_bindings[p_arg] = f_arg
            else:  # Constant
                if p_arg != f_arg:
                    return None

        return new_bindings

    def apply(self, bindings: Dict[str, str]) -> Fact:
        """Apply bindings to generate conclusion fact"""
        pred, args = self._parse_pattern(self.conclusion)
        resolved_args = tuple(bindings.get(a, a) for a in args)
        return Fact(predicate=pred, arguments=resolved_args, source=f"inferred:{self.name}")


class LogicEngine:
    """
    Logic engine for inference and deduction.
    Forward-chaining reasoning.
    """

    def __init__(self):
        self.facts: Set[Fact] = set()
        self.inferences: List[Inference] = []
        self._load_default_inferences()

    def _load_default_inferences(self):
        """Load default inference rules"""
        # Transitivity
        self.add_inference(
            name="transitivity",
            premises=["parent(X, Y)", "parent(Y, Z)"],
            conclusion="grandparent(X, Z)"
        )

        # Symmetry
        self.add_inference(
            name="similarity_symmetry",
            premises=["similar(X, Y)"],
            conclusion="similar(Y, X)"
        )

    def add_fact(self, predicate: str, *args, confidence: float = 1.0):
        """Add a fact to the knowledge base"""
        fact = Fact(predicate=predicate, arguments=args, confidence=confidence)
        self.facts.add(fact)

    def add_inference(self, name: str, premises: List[str], conclusion: str):
        """Add an inference rule"""
        self.inferences.append(Inference(name=name, premises=premises, conclusion=conclusion))

    def query(self, predicate: str, *args) -> List[Fact]:
        """Query facts matching predicate and arguments"""
        results = []
        for fact in self.facts:
            if fact.predicate != predicate:
                continue
            if len(args) != len(fact.arguments):
                continue

            match = True
            for q_arg, f_arg in zip(args, fact.arguments):
                if q_arg != "_" and q_arg != f_arg:  # "_" is wildcard
                    match = False
                    break

            if match:
                results.append(fact)

        return results

    def infer(self, max_iterations: int = 10) -> int:
        """Run forward chaining inference. Returns number of new facts."""
        new_facts_total = 0

        for _ in range(max_iterations):
            new_facts = []

            for inference in self.inferences:
                bindings_list = inference.match(self.facts)
                for bindings in bindings_list:
                    new_fact = inference.apply(bindings)
                    if new_fact not in self.facts:
                        new_facts.append(new_fact)

            if not new_facts:
                break

            for fact in new_facts:
                self.facts.add(fact)
            new_facts_total += len(new_facts)

        return new_facts_total

    def explain(self, fact: Fact) -> List[str]:
        """Explain how a fact was derived"""
        explanations = []

        if fact.source == "asserted":
            explanations.append(f"{fact} was directly asserted")
        elif fact.source.startswith("inferred:"):
            rule_name = fact.source.split(":")[1]
            explanations.append(f"{fact} was inferred by rule '{rule_name}'")

        return explanations


@dataclass
class PlanAction:
    """An action in a plan"""
    name: str
    preconditions: Set[str]  # Required state
    effects: Set[str]        # State changes (add)
    delete_effects: Set[str] = field(default_factory=set)  # State changes (remove)
    cost: float = 1.0
    duration: float = 1.0


@dataclass
class Plan:
    """A sequence of actions to achieve a goal"""
    goal: str
    actions: List[PlanAction]
    total_cost: float
    total_duration: float
    achieves_goal: bool


class Planner:
    """
    Goal-directed action planner.
    Uses simple state-space search.
    """

    def __init__(self):
        self.actions: Dict[str, PlanAction] = {}
        self._load_default_actions()

    def _load_default_actions(self):
        """Load default actions"""
        self.add_action(
            name="research",
            preconditions=set(),
            effects={"has_information"},
            cost=1.0,
            duration=2.0
        )

        self.add_action(
            name="design",
            preconditions={"has_information"},
            effects={"has_design"},
            cost=2.0,
            duration=3.0
        )

        self.add_action(
            name="implement",
            preconditions={"has_design"},
            effects={"has_implementation"},
            cost=5.0,
            duration=10.0
        )

        self.add_action(
            name="test",
            preconditions={"has_implementation"},
            effects={"is_tested"},
            cost=2.0,
            duration=3.0
        )

        self.add_action(
            name="deploy",
            preconditions={"is_tested"},
            effects={"is_deployed"},
            cost=1.0,
            duration=1.0
        )

    def add_action(
        self,
        name: str,
        preconditions: Set[str],
        effects: Set[str],
        delete_effects: Set[str] = None,
        cost: float = 1.0,
        duration: float = 1.0
    ):
        """Add an action to the planner"""
        self.actions[name] = PlanAction(
            name=name,
            preconditions=preconditions,
            effects=effects,
            delete_effects=delete_effects or set(),
            cost=cost,
            duration=duration
        )

    def plan(self, initial_state: Set[str], goal_state: Set[str], max_depth: int = 20) -> Optional[Plan]:
        """
        Find a plan to achieve goal state from initial state.
        Uses breadth-first search.
        """
        # State: (current_state, actions_taken, cost, duration)
        queue = deque([(initial_state, [], 0.0, 0.0)])
        visited = {frozenset(initial_state)}

        while queue and max_depth > 0:
            max_depth -= 1
            state, actions, cost, duration = queue.popleft()

            # Check if goal achieved
            if goal_state.issubset(state):
                return Plan(
                    goal=str(goal_state),
                    actions=actions,
                    total_cost=cost,
                    total_duration=duration,
                    achieves_goal=True
                )

            # Try all applicable actions
            for action in self.actions.values():
                if action.preconditions.issubset(state):
                    # Apply action
                    new_state = (state | action.effects) - action.delete_effects
                    state_key = frozenset(new_state)

                    if state_key not in visited:
                        visited.add(state_key)
                        queue.append((
                            new_state,
                            actions + [action],
                            cost + action.cost,
                            duration + action.duration
                        ))

        return None

    def explain_plan(self, plan: Plan) -> str:
        """Generate human-readable plan explanation"""
        if not plan or not plan.achieves_goal:
            return "No plan found"

        lines = [f"Plan to achieve: {plan.goal}", ""]

        for i, action in enumerate(plan.actions, 1):
            lines.append(f"Step {i}: {action.name}")
            lines.append(f"  Requires: {action.preconditions or 'nothing'}")
            lines.append(f"  Achieves: {action.effects}")
            lines.append(f"  Cost: {action.cost}, Duration: {action.duration}")
            lines.append("")

        lines.append(f"Total Cost: {plan.total_cost}")
        lines.append(f"Total Duration: {plan.total_duration}")

        return "\n".join(lines)


class ReasoningEngine:
    """
    Unified reasoning engine combining all reasoning systems.
    """

    def __init__(self):
        self.rules = SymbolicRules()
        self.logic = LogicEngine()
        self.planner = Planner()

    def evaluate_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate symbolic rules"""
        return self.rules.evaluate(context)

    def infer(self) -> int:
        """Run logical inference"""
        return self.logic.infer()

    def plan(self, initial: Set[str], goal: Set[str]) -> Optional[Plan]:
        """Create a plan"""
        return self.planner.plan(initial, goal)

    def reason(self, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive reasoning about a goal.

        Returns reasoning results including rules, inferences, and plan.
        """
        context = context or {}
        results = {
            "goal": goal,
            "rules_triggered": [],
            "inferences_made": 0,
            "plan": None,
        }

        # Check rules
        results["rules_triggered"] = self.evaluate_rules(context)

        # Run inference
        results["inferences_made"] = self.infer()

        # Try to plan (if goal can be parsed as state)
        goal_words = set(goal.lower().split())
        goal_state = {w for w in goal_words if w in ["deployed", "tested", "implemented"]}
        if goal_state:
            initial_state = set()
            plan = self.plan(initial_state, goal_state)
            if plan:
                results["plan"] = self.planner.explain_plan(plan)

        return results


# Demo
def demo():
    """Demonstrate reasoning engine"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                   0RB REASONING ENGINE                        ║
║                                                               ║
║      Symbolic Rules + Logic Engine + Action Planner           ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    engine = ReasoningEngine()

    # Test rules
    print("[1] Testing Symbolic Rules...")
    context = {
        "action_type": "delete_all",
        "user_confirmed": False,
        "budget_percent": 85
    }
    triggered = engine.evaluate_rules(context)
    for action in triggered:
        print(f"  Rule: {action['rule_name']} -> {action['type']}: {action.get('reason', action.get('message', ''))}")

    # Test logic
    print("\n[2] Testing Logic Engine...")
    engine.logic.add_fact("parent", "alice", "bob")
    engine.logic.add_fact("parent", "bob", "charlie")
    new_facts = engine.infer()
    print(f"  Added {new_facts} inferred facts")

    grandparents = engine.logic.query("grandparent", "_", "_")
    for f in grandparents:
        print(f"  Inferred: {f}")

    # Test planner
    print("\n[3] Testing Planner...")
    initial = set()
    goal = {"is_deployed"}
    plan = engine.plan(initial, goal)
    if plan:
        print(engine.planner.explain_plan(plan))


if __name__ == "__main__":
    demo()
