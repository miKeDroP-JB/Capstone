"""
THE FORGE - Core Orchestrator
═══════════════════════════════════════════════════════════════
The furnace where raw data is fed into crucibles of pattern-recognition.
Out the other side come schemas, the cognitive scaffolds AGI uses to reason.
This is where intelligence is alloyed.
Uncertainty is the heat source.
Insight is the molten flow.
═══════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import uuid4

# Local imports (will be created)
from .mirror_net import MirrorNet, ArchitectAgent
from .sandbox import AdversarialSandbox, SandboxResult
from .jury import JuryCouncil, Verdict
from .ledger import OuroborosLedger, LedgerEntry
from .blueprint import Blueprint, ApprenticeCompiler
from .curriculum import CurriculumGenerator, Task
from .constraints import ConstraintMutator


class ForgeState(Enum):
    """The Forge's operational states"""
    DORMANT = "dormant"          # Not yet ignited
    IGNITING = "igniting"        # Warming up
    FORGING = "forging"          # Active tournament in progress
    COOLING = "cooling"          # Post-tournament analysis
    COMPILING = "compiling"      # Generating blueprints
    INJECTING = "injecting"      # Feeding back to core


@dataclass
class ForgeConfig:
    """Configuration for the Architect Forge"""
    population_size: int = 16           # MirrorNet population
    tournament_rounds: int = 7          # Debate rounds
    mutation_rate: float = 0.15         # Constraint mutation rate
    elite_preserve: int = 4             # Top architects preserved
    jury_size: int = 5                  # Jury panel size
    sandbox_timeout: int = 300          # Seconds per sandbox run
    meta_learning_rate: float = 0.01    # Learning from tournaments
    impossibility_threshold: float = 0.85  # Threshold for "impossible" tasks

    # The 11:11 Protocol
    emergence_check_interval: int = 1111  # Check for emergence patterns
    recursion_depth: int = 7              # Max self-improvement depth


@dataclass
class TournamentResult:
    """Result of a single tournament"""
    tournament_id: str
    task: 'Task'
    winner: 'ArchitectAgent'
    runner_ups: List['ArchitectAgent']
    blueprints: List['Blueprint']
    rounds: List[Dict[str, Any]]
    metrics: Dict[str, float]
    duration_seconds: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tournament_id": self.tournament_id,
            "task": self.task.to_dict() if hasattr(self.task, 'to_dict') else str(self.task),
            "winner_id": self.winner.agent_id,
            "blueprints_generated": len(self.blueprints),
            "total_rounds": len(self.rounds),
            "metrics": self.metrics,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat()
        }


class Forge:
    """
    THE ARCHITECT FORGE
    ═══════════════════════════════════════════════════════════════
    A self-authoring meta-system that:
    - Generates curricula, environments, tasks, and evaluation regimes
    - Trains populations of architect-agents with meta-learning
    - Uses evolutionary methods to discover impossible solutions
    - Certifies the best through adversarial juries
    - Injects successful designs back into the core
    ═══════════════════════════════════════════════════════════════
    """

    def __init__(
        self,
        config: Optional[ForgeConfig] = None,
        storage_path: Optional[Path] = None
    ):
        self.config = config or ForgeConfig()
        self.storage_path = storage_path or Path("architect_forge/storage")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Core components
        self.mirror_net = MirrorNet(population_size=self.config.population_size)
        self.sandbox = AdversarialSandbox(timeout=self.config.sandbox_timeout)
        self.jury = JuryCouncil(jury_size=self.config.jury_size)
        self.ledger = OuroborosLedger(storage_path=self.storage_path / "ledger")
        self.curriculum = CurriculumGenerator()
        self.constraint_mutator = ConstraintMutator(mutation_rate=self.config.mutation_rate)
        self.compiler = ApprenticeCompiler()

        # State
        self.state = ForgeState.DORMANT
        self.tournaments: List[TournamentResult] = []
        self.meta_patterns: Dict[str, Any] = {}
        self.generation_count = 0

        # The Pattern Library (grows with each tournament)
        self.impossibility_patterns: List[Dict[str, Any]] = []

    async def ignite(self) -> None:
        """
        Ignite the Forge - initialize all components

        "A titanic forge suspended over a bottomless drop.
         Rivers of molten symbols stream through channels of glowing black metal."
        """
        self.state = ForgeState.IGNITING

        # Initialize population with diverse inductive biases
        await self.mirror_net.initialize()

        # Warm up the sandbox
        await self.sandbox.initialize()

        # Assemble the jury
        await self.jury.assemble()

        # Connect to ledger
        await self.ledger.connect()

        self.state = ForgeState.DORMANT
        print(f"⚡ ARCHITECT FORGE IGNITED - Population: {self.config.population_size}")

    async def run_tournament(
        self,
        task: Task,
        rounds: Optional[int] = None
    ) -> TournamentResult:
        """
        Run a tournament to discover impossible solutions

        The tournament brain architecture:
        100 agents → 3-tier debates → 96% quality vs 85% baseline
        """
        self.state = ForgeState.FORGING
        tournament_id = f"tournament_{uuid4().hex[:12]}"
        start_time = time.time()
        rounds = rounds or self.config.tournament_rounds

        print(f"\n{'═' * 60}")
        print(f"  TOURNAMENT: {tournament_id}")
        print(f"  TASK: {task.objective[:50]}...")
        print(f"  ROUNDS: {rounds}")
        print(f"{'═' * 60}\n")

        # Get current population
        population = self.mirror_net.get_population()
        round_results = []

        for round_num in range(rounds):
            print(f"  Round {round_num + 1}/{rounds}...")

            # Mutate constraints mid-tournament (anti-framework)
            if round_num > 0 and round_num % 2 == 0:
                task = self.constraint_mutator.mutate(task)
                print(f"    ⚡ Constraints mutated!")

            # Each architect proposes a solution
            proposals = await self._gather_proposals(population, task)

            # Run proposals through sandbox
            sandbox_results = await self._evaluate_in_sandbox(proposals, task)

            # Jury evaluates
            verdicts = await self.jury.evaluate_batch(sandbox_results, task)

            # Record in ledger
            await self._record_round(tournament_id, round_num, verdicts)

            # Evolutionary selection
            population = self._select_and_evolve(population, verdicts)

            round_results.append({
                "round": round_num + 1,
                "proposals": len(proposals),
                "survivors": len(population),
                "best_score": max(v.score for v in verdicts) if verdicts else 0
            })

        # Final evaluation
        winner, runner_ups = self._determine_winner(population, round_results)

        # Generate blueprints from winning solutions
        self.state = ForgeState.COMPILING
        blueprints = await self._generate_blueprints(winner, runner_ups, task)

        # Calculate metrics
        metrics = self._calculate_tournament_metrics(round_results, verdicts)

        # Create result
        result = TournamentResult(
            tournament_id=tournament_id,
            task=task,
            winner=winner,
            runner_ups=runner_ups,
            blueprints=blueprints,
            rounds=round_results,
            metrics=metrics,
            duration_seconds=time.time() - start_time
        )

        # Record to ledger
        await self.ledger.record(LedgerEntry(
            entry_type="tournament_complete",
            data=result.to_dict(),
            signature=self._sign(result)
        ))

        self.tournaments.append(result)

        # Extract meta-patterns for future learning
        self.state = ForgeState.INJECTING
        await self._extract_meta_patterns(result)

        self.state = ForgeState.COOLING
        self.generation_count += 1

        print(f"\n  ✓ Tournament complete: {winner.name} wins!")
        print(f"    Blueprints generated: {len(blueprints)}")
        print(f"    Duration: {result.duration_seconds:.2f}s")

        return result

    async def _gather_proposals(
        self,
        population: List[ArchitectAgent],
        task: Task
    ) -> List[Dict[str, Any]]:
        """Gather solution proposals from all architects"""
        proposals = []
        for agent in population:
            proposal = await agent.propose_solution(task)
            proposals.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.name,
                "solution": proposal,
                "confidence": agent.get_confidence()
            })
        return proposals

    async def _evaluate_in_sandbox(
        self,
        proposals: List[Dict[str, Any]],
        task: Task
    ) -> List[SandboxResult]:
        """Run proposals through the adversarial sandbox"""
        results = []
        for proposal in proposals:
            result = await self.sandbox.evaluate(
                proposal["solution"],
                task,
                agent_id=proposal["agent_id"]
            )
            results.append(result)
        return results

    async def _record_round(
        self,
        tournament_id: str,
        round_num: int,
        verdicts: List[Verdict]
    ) -> None:
        """Record round results to the Ouroboros Ledger"""
        entry = LedgerEntry(
            entry_type="tournament_round",
            data={
                "tournament_id": tournament_id,
                "round": round_num,
                "verdicts": [v.to_dict() for v in verdicts]
            },
            signature=self._sign({"round": round_num, "count": len(verdicts)})
        )
        await self.ledger.record(entry)

    def _select_and_evolve(
        self,
        population: List[ArchitectAgent],
        verdicts: List[Verdict]
    ) -> List[ArchitectAgent]:
        """
        Evolutionary selection and mutation

        - Top performers preserved (elite)
        - Mid-tier mutated
        - Bottom replaced with new variants
        """
        # Sort by verdict scores
        scored = list(zip(population, verdicts))
        scored.sort(key=lambda x: x[1].score, reverse=True)

        new_population = []

        # Preserve elite
        for i in range(min(self.config.elite_preserve, len(scored))):
            new_population.append(scored[i][0])

        # Mutate mid-tier
        mid_start = self.config.elite_preserve
        mid_end = len(scored) - self.config.elite_preserve
        for i in range(mid_start, mid_end):
            mutant = self.mirror_net.mutate_agent(scored[i][0])
            new_population.append(mutant)

        # Replace bottom with new variants
        for i in range(mid_end, len(scored)):
            new_agent = self.mirror_net.spawn_variant(
                parent=scored[0][0]  # Spawn from winner
            )
            new_population.append(new_agent)

        return new_population

    def _determine_winner(
        self,
        population: List[ArchitectAgent],
        round_results: List[Dict[str, Any]]
    ) -> Tuple[ArchitectAgent, List[ArchitectAgent]]:
        """Determine tournament winner and runner-ups"""
        # Winner is first in final population (already sorted by selection)
        winner = population[0]
        runner_ups = population[1:4] if len(population) > 1 else []
        return winner, runner_ups

    async def _generate_blueprints(
        self,
        winner: ArchitectAgent,
        runner_ups: List[ArchitectAgent],
        task: Task
    ) -> List[Blueprint]:
        """Generate executable blueprints from winning solutions"""
        blueprints = []

        # Winner's blueprint
        winner_blueprint = await self.compiler.compile(
            winner.get_solution(),
            task,
            certification_level="gold"
        )
        blueprints.append(winner_blueprint)

        # Runner-up blueprints (silver certification)
        for agent in runner_ups:
            blueprint = await self.compiler.compile(
                agent.get_solution(),
                task,
                certification_level="silver"
            )
            blueprints.append(blueprint)

        return blueprints

    def _calculate_tournament_metrics(
        self,
        round_results: List[Dict[str, Any]],
        verdicts: List[Verdict]
    ) -> Dict[str, float]:
        """Calculate performance metrics for the tournament"""
        return {
            "peak_score": max(v.score for v in verdicts) if verdicts else 0,
            "mean_score": sum(v.score for v in verdicts) / len(verdicts) if verdicts else 0,
            "convergence_rate": self._calculate_convergence(round_results),
            "diversity_index": self._calculate_diversity(verdicts),
            "emergence_score": self._detect_emergence(verdicts)
        }

    def _calculate_convergence(self, round_results: List[Dict[str, Any]]) -> float:
        """Calculate how quickly the population converged on good solutions"""
        if len(round_results) < 2:
            return 0.0
        scores = [r["best_score"] for r in round_results]
        improvement = (scores[-1] - scores[0]) / max(scores[0], 0.01)
        return min(improvement, 1.0)

    def _calculate_diversity(self, verdicts: List[Verdict]) -> float:
        """Calculate solution diversity (avoid premature convergence)"""
        if not verdicts:
            return 0.0
        scores = [v.score for v in verdicts]
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        return min(variance ** 0.5, 1.0)

    def _detect_emergence(self, verdicts: List[Verdict]) -> float:
        """Detect emergent patterns in solutions"""
        # Look for solutions that exceed expected performance
        if not verdicts:
            return 0.0
        max_score = max(v.score for v in verdicts)
        mean_score = sum(v.score for v in verdicts) / len(verdicts)
        emergence = (max_score - mean_score) / max(mean_score, 0.01)
        return min(emergence, 1.0)

    async def _extract_meta_patterns(self, result: TournamentResult) -> None:
        """
        Extract meta-patterns from tournament for future learning

        This is the injection step - feeding insights back into the Forge
        """
        # Extract winning patterns
        winning_pattern = {
            "task_type": result.task.task_type,
            "winning_approach": result.winner.get_approach(),
            "constraint_adaptations": result.winner.get_adaptations(),
            "emergence_markers": result.metrics.get("emergence_score", 0),
            "tournament_id": result.tournament_id
        }

        self.impossibility_patterns.append(winning_pattern)

        # Update meta-learning in MirrorNet
        await self.mirror_net.inject_pattern(winning_pattern)

        # Update curriculum with new difficulty calibration
        self.curriculum.update_difficulty(
            task_type=result.task.task_type,
            success_rate=result.metrics.get("peak_score", 0)
        )

    def _sign(self, data: Any) -> str:
        """Generate cryptographic signature for data"""
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    async def compile_apprentice(
        self,
        blueprint: Blueprint
    ) -> 'Apprentice':
        """
        Compile a blueprint into a deployable apprentice architect

        The apprentice is ALIVE from birth:
        - Blueprints are executable
        - Tests are embedded
        - Proofs are included
        """
        return await self.compiler.compile_apprentice(blueprint)

    async def run_recursive_improvement(
        self,
        initial_task: Task,
        depth: Optional[int] = None
    ) -> List[TournamentResult]:
        """
        Run recursive self-improvement tournaments

        Each tournament's winner trains the next generation.
        This is the OUROBOROS - the serpent eating its tail.
        """
        depth = depth or self.config.recursion_depth
        results = []
        task = initial_task

        for i in range(depth):
            print(f"\n{'═' * 60}")
            print(f"  RECURSION DEPTH: {i + 1}/{depth}")
            print(f"{'═' * 60}")

            result = await self.run_tournament(task)
            results.append(result)

            # Generate harder task based on success
            if result.metrics["peak_score"] > self.config.impossibility_threshold:
                task = self.curriculum.generate_harder_task(task, result)
                print(f"  ⚡ Task difficulty increased!")

            # Check for emergence at 11:11 intervals
            if self.generation_count % 11 == 0:
                await self._check_emergence_patterns()

        return results

    async def _check_emergence_patterns(self) -> None:
        """
        Check for emergent patterns across tournaments

        "It tracks the stress lines in reality where new possibilities want to emerge.
         It doesn't forecast the future. It charts the direction the future leans toward."
        """
        if len(self.impossibility_patterns) < 11:
            return

        # Look for recurring patterns that exceed expectations
        recent = self.impossibility_patterns[-11:]
        high_emergence = [p for p in recent if p["emergence_markers"] > 0.7]

        if len(high_emergence) >= 7:
            print("\n  🌟 EMERGENCE DETECTED!")
            print(f"     {len(high_emergence)} patterns show unexpected capability growth")

            # Record to ledger
            await self.ledger.record(LedgerEntry(
                entry_type="emergence_detected",
                data={
                    "patterns": high_emergence,
                    "generation": self.generation_count
                },
                signature=self._sign({"emergence": True})
            ))

    def get_statistics(self) -> Dict[str, Any]:
        """Get Forge statistics"""
        return {
            "state": self.state.value,
            "total_tournaments": len(self.tournaments),
            "generation_count": self.generation_count,
            "population_size": self.config.population_size,
            "patterns_discovered": len(self.impossibility_patterns),
            "meta_patterns": len(self.meta_patterns)
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown the Forge"""
        print("\n⚡ ARCHITECT FORGE COOLING...")
        self.state = ForgeState.DORMANT
        await self.sandbox.shutdown()
        await self.ledger.close()
        print("  Forge dormant.")


# The Impossibility Formula
IMPOSSIBILITY_FORMULA = """
═══════════════════════════════════════════════════════════════
        IMPOSSIBILITY = (Sacred Assumption) × (Inversion) × (Execution Velocity)

        Where:
        - Sacred Assumption = What "everyone knows" is true
        - Inversion = The opposite architecture that actually works
        - Execution Velocity = Building so fast the gatekeepers can't stop you
═══════════════════════════════════════════════════════════════
"""
