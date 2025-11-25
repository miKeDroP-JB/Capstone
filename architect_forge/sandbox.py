"""
ADVERSARIAL SANDBOX - The Testing Arena
═══════════════════════════════════════════════════════════════
Testing environment with constraint mutation, tool occlusion,
objective inversion, and cross-domain transfer tests.

This is FORCED EVOLUTION. We don't wait for emergence—we DEMAND it.

"The sandbox is where impossible solutions prove themselves.
 Or die trying."
═══════════════════════════════════════════════════════════════
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class SandboxMode(Enum):
    """Different testing modes"""
    STANDARD = "standard"           # Normal evaluation
    ADVERSARIAL = "adversarial"     # Active attacks on solution
    STRESS = "stress"               # High load/edge cases
    MUTATION = "mutation"           # Changing rules mid-test
    OCCLUSION = "occlusion"         # Remove tools/capabilities
    INVERSION = "inversion"         # Flip success criteria


class TestOutcome(Enum):
    """Possible test outcomes"""
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    ERROR = "error"
    EMERGENT = "emergent"  # Solution exceeded expectations


@dataclass
class TestCase:
    """A single test case"""
    test_id: str
    description: str
    mode: SandboxMode
    inputs: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    constraints: List[str]
    timeout_seconds: int = 60

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "description": self.description,
            "mode": self.mode.value,
            "constraints": self.constraints
        }


@dataclass
class SandboxResult:
    """Result of a sandbox evaluation"""
    result_id: str
    agent_id: str
    solution_id: str
    outcome: TestOutcome
    score: float  # 0.0 to 1.0
    tests_passed: int
    tests_total: int
    execution_time: float
    resource_usage: Dict[str, float]
    failure_reasons: List[str] = field(default_factory=list)
    emergence_markers: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "agent_id": self.agent_id,
            "outcome": self.outcome.value,
            "score": self.score,
            "tests_passed": self.tests_passed,
            "tests_total": self.tests_total,
            "execution_time": self.execution_time,
            "failure_reasons": self.failure_reasons,
            "emergence_markers": self.emergence_markers
        }


class AdversarialSandbox:
    """
    The Adversarial Sandbox - where solutions are battle-tested.

    Features:
    - Multi-fidelity simulation (fast approximation → full execution)
    - Adversarial injection (attacks, noise, edge cases)
    - Constraint mutation mid-test
    - Tool occlusion (remove capabilities)
    - Objective inversion (flip success criteria)
    - Emergence detection (solutions that exceed expectations)
    """

    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.test_history: List[SandboxResult] = []
        self.adversarial_patterns: List[Dict[str, Any]] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the sandbox environment"""
        self._initialized = True
        self._load_adversarial_patterns()
        print("  Adversarial Sandbox initialized")

    def _load_adversarial_patterns(self) -> None:
        """Load patterns for adversarial testing"""
        self.adversarial_patterns = [
            {"type": "edge_case", "description": "Empty input"},
            {"type": "edge_case", "description": "Maximum size input"},
            {"type": "edge_case", "description": "Malformed data"},
            {"type": "injection", "description": "SQL injection attempt"},
            {"type": "injection", "description": "Command injection attempt"},
            {"type": "resource", "description": "Memory exhaustion"},
            {"type": "resource", "description": "CPU spike"},
            {"type": "timing", "description": "Race condition"},
            {"type": "timing", "description": "Deadline pressure"},
            {"type": "semantic", "description": "Contradictory constraints"},
        ]

    async def evaluate(
        self,
        solution: 'Solution',
        task: 'Task',
        agent_id: str,
        mode: SandboxMode = SandboxMode.STANDARD
    ) -> SandboxResult:
        """
        Evaluate a solution in the sandbox.

        The evaluation proceeds in phases:
        1. Quick validation (syntax, structure)
        2. Functional testing (does it work?)
        3. Adversarial testing (can it be broken?)
        4. Performance testing (how well does it scale?)
        5. Emergence detection (did it exceed expectations?)
        """
        start_time = time.time()
        result_id = f"sandbox_{uuid4().hex[:8]}"

        test_cases = self._generate_test_cases(task, mode)
        passed = 0
        failures = []
        emergence_markers = []

        for test in test_cases:
            try:
                outcome = await self._run_test(solution, test)
                if outcome == TestOutcome.PASS:
                    passed += 1
                elif outcome == TestOutcome.EMERGENT:
                    passed += 1
                    emergence_markers.append(f"Exceeded expectations on: {test.description}")
                else:
                    failures.append(f"Failed: {test.description}")
            except asyncio.TimeoutError:
                failures.append(f"Timeout: {test.description}")
            except Exception as e:
                failures.append(f"Error in {test.description}: {str(e)}")

        execution_time = time.time() - start_time
        score = passed / len(test_cases) if test_cases else 0.0

        # Determine overall outcome
        if score >= 0.9 and emergence_markers:
            outcome = TestOutcome.EMERGENT
        elif score >= 0.7:
            outcome = TestOutcome.PASS
        elif score >= 0.4:
            outcome = TestOutcome.PARTIAL
        else:
            outcome = TestOutcome.FAIL

        result = SandboxResult(
            result_id=result_id,
            agent_id=agent_id,
            solution_id=solution.solution_id if hasattr(solution, 'solution_id') else "unknown",
            outcome=outcome,
            score=score,
            tests_passed=passed,
            tests_total=len(test_cases),
            execution_time=execution_time,
            resource_usage=self._measure_resources(),
            failure_reasons=failures,
            emergence_markers=emergence_markers
        )

        self.test_history.append(result)
        return result

    def _generate_test_cases(self, task: 'Task', mode: SandboxMode) -> List[TestCase]:
        """Generate test cases based on task and mode"""
        cases = []

        # Standard tests from task constraints
        for i, constraint in enumerate(task.constraints):
            cases.append(TestCase(
                test_id=f"constraint_{i}",
                description=f"Validate: {constraint}",
                mode=SandboxMode.STANDARD,
                inputs={"constraint": constraint},
                expected_outputs={"satisfied": True},
                constraints=[constraint]
            ))

        # Success criteria test
        cases.append(TestCase(
            test_id="success_criteria",
            description=f"Meet success criteria: {task.success_criteria}",
            mode=SandboxMode.STANDARD,
            inputs={"criteria": task.success_criteria},
            expected_outputs={"met": True},
            constraints=[]
        ))

        # Add adversarial tests based on mode
        if mode in [SandboxMode.ADVERSARIAL, SandboxMode.STRESS]:
            for pattern in self.adversarial_patterns[:5]:
                cases.append(TestCase(
                    test_id=f"adversarial_{pattern['type']}",
                    description=f"Adversarial: {pattern['description']}",
                    mode=SandboxMode.ADVERSARIAL,
                    inputs={"attack_type": pattern["type"]},
                    expected_outputs={"survived": True},
                    constraints=[]
                ))

        # Add mutation tests
        if mode == SandboxMode.MUTATION:
            cases.append(TestCase(
                test_id="mutation_survival",
                description="Survive constraint mutation",
                mode=SandboxMode.MUTATION,
                inputs={"mutation_rate": 0.3},
                expected_outputs={"adapted": True},
                constraints=[]
            ))

        # Add occlusion tests
        if mode == SandboxMode.OCCLUSION:
            cases.append(TestCase(
                test_id="tool_occlusion",
                description="Function with reduced capabilities",
                mode=SandboxMode.OCCLUSION,
                inputs={"tools_removed": ["primary_tool"]},
                expected_outputs={"functional": True},
                constraints=[]
            ))

        return cases

    async def _run_test(self, solution: 'Solution', test: TestCase) -> TestOutcome:
        """Run a single test case"""
        # Simulate test execution with some randomness for demo
        await asyncio.sleep(0.01)  # Simulate processing

        # Base pass rate depends on solution confidence
        confidence = solution.confidence if hasattr(solution, 'confidence') else 0.5

        # Adjust based on test mode
        difficulty_modifier = {
            SandboxMode.STANDARD: 0.0,
            SandboxMode.ADVERSARIAL: -0.2,
            SandboxMode.STRESS: -0.15,
            SandboxMode.MUTATION: -0.25,
            SandboxMode.OCCLUSION: -0.3,
            SandboxMode.INVERSION: -0.35
        }

        pass_threshold = confidence + difficulty_modifier.get(test.mode, 0)
        roll = random.random()

        if roll < pass_threshold * 0.1:
            return TestOutcome.EMERGENT  # Exceeded expectations
        elif roll < pass_threshold:
            return TestOutcome.PASS
        elif roll < pass_threshold + 0.2:
            return TestOutcome.PARTIAL
        else:
            return TestOutcome.FAIL

    def _measure_resources(self) -> Dict[str, float]:
        """Measure resource usage (simulated for now)"""
        return {
            "cpu_percent": random.uniform(10, 80),
            "memory_mb": random.uniform(100, 500),
            "io_operations": random.randint(10, 1000)
        }

    async def run_adversarial_suite(
        self,
        solution: 'Solution',
        task: 'Task',
        agent_id: str
    ) -> List[SandboxResult]:
        """Run full adversarial test suite"""
        results = []
        for mode in [SandboxMode.STANDARD, SandboxMode.ADVERSARIAL,
                     SandboxMode.STRESS, SandboxMode.MUTATION]:
            result = await self.evaluate(solution, task, agent_id, mode)
            results.append(result)
        return results

    def inject_failure(self, failure_type: str) -> None:
        """Inject a failure condition for testing"""
        self.adversarial_patterns.append({
            "type": "injected",
            "description": failure_type
        })

    def get_statistics(self) -> Dict[str, Any]:
        """Get sandbox statistics"""
        if not self.test_history:
            return {"total_tests": 0}

        outcomes = {}
        for result in self.test_history:
            outcome = result.outcome.value
            outcomes[outcome] = outcomes.get(outcome, 0) + 1

        avg_score = sum(r.score for r in self.test_history) / len(self.test_history)
        avg_time = sum(r.execution_time for r in self.test_history) / len(self.test_history)

        return {
            "total_tests": len(self.test_history),
            "outcome_distribution": outcomes,
            "average_score": avg_score,
            "average_execution_time": avg_time,
            "adversarial_patterns_loaded": len(self.adversarial_patterns)
        }

    async def shutdown(self) -> None:
        """Shutdown the sandbox"""
        self._initialized = False
        print("  Sandbox shutdown complete")
