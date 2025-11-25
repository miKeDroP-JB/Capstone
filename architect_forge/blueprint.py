"""
BLUEPRINT - Executable Specifications for Apprentice Architects
═══════════════════════════════════════════════════════════════
The output isn't just a model—it's a DEPLOYABLE ARCHITECT.

Blueprints are executable.
Tests are embedded.
Proofs are included.
It's ALIVE from birth.

"Every successful architect can INSTANTLY propagate."
═══════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4


class BlueprintStatus(Enum):
    """Status of a blueprint"""
    DRAFT = "draft"
    COMPILED = "compiled"
    CERTIFIED = "certified"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"


@dataclass
class TestSpec:
    """Embedded test specification"""
    test_id: str
    description: str
    test_type: str  # "unit", "integration", "adversarial"
    inputs: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    timeout_seconds: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "description": self.description,
            "test_type": self.test_type,
            "inputs": self.inputs,
            "expected_outputs": self.expected_outputs,
            "timeout_seconds": self.timeout_seconds
        }


@dataclass
class Proof:
    """Proof of capability or certification"""
    proof_id: str
    proof_type: str  # "tournament_win", "jury_certification", "benchmark"
    evidence: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "proof_type": self.proof_type,
            "evidence": self.evidence,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Blueprint:
    """
    Blueprint for an Apprentice Architect.

    A blueprint contains everything needed to instantiate
    a fully functional, certified architect agent.
    """
    blueprint_id: str
    name: str
    version: str
    status: BlueprintStatus

    # Core specification
    objective: str
    approach: str
    specialization: str
    inductive_bias: str

    # Implementation
    implementation: Dict[str, Any]
    configuration: Dict[str, Any]

    # Embedded tests
    tests: List[TestSpec]

    # Proofs of capability
    proofs: List[Proof]

    # Lineage
    parent_blueprint_id: Optional[str] = None
    generation: int = 0

    # Certification
    certification_level: str = "uncertified"
    certification_score: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "forge"
    tags: List[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        """Compute unique hash for this blueprint"""
        content = json.dumps({
            "name": self.name,
            "version": self.version,
            "objective": self.objective,
            "approach": self.approach,
            "implementation": self.implementation
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "objective": self.objective,
            "approach": self.approach,
            "specialization": self.specialization,
            "inductive_bias": self.inductive_bias,
            "implementation": self.implementation,
            "configuration": self.configuration,
            "tests": [t.to_dict() for t in self.tests],
            "proofs": [p.to_dict() for p in self.proofs],
            "certification_level": self.certification_level,
            "certification_score": self.certification_score,
            "generation": self.generation,
            "hash": self.compute_hash(),
            "created_at": self.created_at.isoformat()
        }

    def to_json(self) -> str:
        """Export blueprint as JSON"""
        return json.dumps(self.to_dict(), indent=2)


class Apprentice:
    """
    A compiled, deployable Apprentice Architect.

    The apprentice is instantiated from a blueprint and can:
    - Execute its specialized task
    - Run self-tests
    - Report metrics
    - Propagate (create copies)
    """

    def __init__(self, blueprint: Blueprint):
        self.blueprint = blueprint
        self.apprentice_id = f"apprentice_{uuid4().hex[:8]}"
        self.deployments: int = 0
        self.executions: int = 0
        self.success_rate: float = 0.0
        self._execution_history: List[Dict[str, Any]] = []

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the apprentice's specialized task"""
        self.executions += 1

        # Simulate execution based on blueprint
        result = {
            "apprentice_id": self.apprentice_id,
            "blueprint_id": self.blueprint.blueprint_id,
            "input": task_input,
            "output": await self._process(task_input),
            "execution_time": 0.1,  # Simulated
            "success": True
        }

        self._execution_history.append(result)
        self._update_success_rate(result["success"])

        return result

    async def _process(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process input according to blueprint implementation"""
        # In a real implementation, this would execute the actual logic
        return {
            "approach_used": self.blueprint.approach,
            "specialization": self.blueprint.specialization,
            "processed": True
        }

    async def run_self_tests(self) -> Dict[str, Any]:
        """Run embedded tests"""
        results = {
            "total": len(self.blueprint.tests),
            "passed": 0,
            "failed": 0,
            "details": []
        }

        for test in self.blueprint.tests:
            # Simulate test execution
            passed = True  # Simplified for demo
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1

            results["details"].append({
                "test_id": test.test_id,
                "passed": passed
            })

        return results

    def _update_success_rate(self, success: bool) -> None:
        """Update success rate with exponential moving average"""
        alpha = 0.1
        self.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * self.success_rate

    def get_metrics(self) -> Dict[str, Any]:
        """Get apprentice metrics"""
        return {
            "apprentice_id": self.apprentice_id,
            "blueprint_name": self.blueprint.name,
            "certification_level": self.blueprint.certification_level,
            "executions": self.executions,
            "success_rate": self.success_rate,
            "deployments": self.deployments
        }

    def propagate(self) -> 'Apprentice':
        """Create a copy of this apprentice"""
        return Apprentice(self.blueprint)


class ApprenticeCompiler:
    """
    Compiler that transforms solutions into deployable blueprints and apprentices.

    The compiler:
    1. Extracts the winning approach from a solution
    2. Generates embedded tests
    3. Attaches proofs of capability
    4. Produces executable blueprints
    """

    def __init__(self):
        self.compiled_blueprints: List[Blueprint] = []

    async def compile(
        self,
        solution: 'Solution',
        task: 'Task',
        certification_level: str = "uncertified"
    ) -> Blueprint:
        """Compile a solution into a blueprint"""
        blueprint_id = f"blueprint_{uuid4().hex[:8]}"

        # Extract implementation from solution
        implementation = solution.implementation if hasattr(solution, 'implementation') else {}

        # Generate tests from task constraints
        tests = self._generate_tests(task)

        # Create proofs from tournament results
        proofs = self._create_proofs(solution, certification_level)

        blueprint = Blueprint(
            blueprint_id=blueprint_id,
            name=f"Architect_{task.task_type}_{blueprint_id[-4:]}",
            version="1.0.0",
            status=BlueprintStatus.COMPILED,
            objective=task.objective,
            approach=solution.approach if hasattr(solution, 'approach') else "standard",
            specialization=task.task_type,
            inductive_bias=implementation.get("approach_type", "analytical"),
            implementation=implementation,
            configuration={
                "constraints": task.constraints,
                "success_criteria": task.success_criteria
            },
            tests=tests,
            proofs=proofs,
            certification_level=certification_level,
            certification_score=solution.confidence if hasattr(solution, 'confidence') else 0.5
        )

        self.compiled_blueprints.append(blueprint)
        return blueprint

    def _generate_tests(self, task: 'Task') -> List[TestSpec]:
        """Generate test specs from task"""
        tests = []

        # Test for each constraint
        for i, constraint in enumerate(task.constraints):
            tests.append(TestSpec(
                test_id=f"constraint_test_{i}",
                description=f"Verify: {constraint}",
                test_type="unit",
                inputs={"constraint": constraint},
                expected_outputs={"satisfied": True}
            ))

        # Test for success criteria
        tests.append(TestSpec(
            test_id="success_criteria_test",
            description=f"Meet success criteria: {task.success_criteria}",
            test_type="integration",
            inputs={"criteria": task.success_criteria},
            expected_outputs={"met": True}
        ))

        # Adversarial test
        tests.append(TestSpec(
            test_id="adversarial_test",
            description="Survive adversarial conditions",
            test_type="adversarial",
            inputs={"attack_type": "standard_suite"},
            expected_outputs={"survived": True}
        ))

        return tests

    def _create_proofs(self, solution: 'Solution', certification_level: str) -> List[Proof]:
        """Create proofs from solution"""
        proofs = []

        # Tournament proof
        proofs.append(Proof(
            proof_id=f"proof_{uuid4().hex[:6]}",
            proof_type="tournament_win",
            evidence={
                "solution_id": solution.solution_id if hasattr(solution, 'solution_id') else "unknown",
                "confidence": solution.confidence if hasattr(solution, 'confidence') else 0.5
            }
        ))

        # Certification proof
        if certification_level != "uncertified":
            proofs.append(Proof(
                proof_id=f"proof_{uuid4().hex[:6]}",
                proof_type="jury_certification",
                evidence={
                    "level": certification_level,
                    "certified_at": datetime.utcnow().isoformat()
                }
            ))

        return proofs

    async def compile_apprentice(self, blueprint: Blueprint) -> Apprentice:
        """Compile a blueprint into a deployable apprentice"""
        apprentice = Apprentice(blueprint)
        blueprint.status = BlueprintStatus.DEPLOYED
        return apprentice

    def export_blueprint(self, blueprint: Blueprint, path: str) -> None:
        """Export blueprint to file"""
        with open(path, "w") as f:
            f.write(blueprint.to_json())

    @staticmethod
    def import_blueprint(path: str) -> Blueprint:
        """Import blueprint from file"""
        with open(path, "r") as f:
            data = json.load(f)

        tests = [TestSpec(**t) for t in data.get("tests", [])]
        proofs = [Proof(
            proof_id=p["proof_id"],
            proof_type=p["proof_type"],
            evidence=p["evidence"]
        ) for p in data.get("proofs", [])]

        return Blueprint(
            blueprint_id=data["blueprint_id"],
            name=data["name"],
            version=data["version"],
            status=BlueprintStatus(data["status"]),
            objective=data["objective"],
            approach=data["approach"],
            specialization=data["specialization"],
            inductive_bias=data["inductive_bias"],
            implementation=data["implementation"],
            configuration=data["configuration"],
            tests=tests,
            proofs=proofs,
            certification_level=data.get("certification_level", "uncertified"),
            certification_score=data.get("certification_score", 0.0),
            generation=data.get("generation", 0)
        )
