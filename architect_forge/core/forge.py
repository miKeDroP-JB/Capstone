"""
Architect Forge: Main orchestrator

Ties together MirrorNet, Sandbox, Jury, and Ouroboros Ledger
into a complete meta-learning system.
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import random

from .mirrornet import MirrorNet, Architect
from .sandbox import Sandbox, FidelityLevel
from .jury import Jury
from .ledger import OuroborosLedger, EventType


@dataclass
class Task:
    """Task for architects to solve"""
    task_id: str
    description: str
    domain: str  # 'code', 'business', 'science', 'design', etc.
    difficulty: float  # 0.0 to 1.0
    constraints: Dict[str, Any]
    success_criteria: Dict[str, Any]


@dataclass
class TrainingCycleResult:
    """Result from one complete training cycle"""
    cycle_number: int
    tasks_attempted: int
    solutions_generated: int
    solutions_approved: int
    apprentices_created: int
    population_diversity: float
    average_quality: float
    best_solution_score: float
    duration: float


class TaskGenerator:
    """Generate diverse tasks for training"""

    @staticmethod
    def create_batch(
        domains: List[str],
        difficulties: List[float],
        count: int = 10
    ) -> List[Task]:
        """Create a batch of diverse tasks"""
        tasks = []

        for i in range(count):
            domain = random.choice(domains)
            difficulty = random.choice(difficulties)

            task = Task(
                task_id=f"task_{int(time.time())}_{i:03d}",
                description=f"Solve a {difficulty:.0%} difficulty {domain} problem",
                domain=domain,
                difficulty=difficulty,
                constraints={
                    'max_time': 60,
                    'max_resources': 'medium',
                },
                success_criteria={
                    'min_quality': 0.6,
                    'min_robustness': 0.5,
                },
            )

            tasks.append(task)

        return tasks

    @staticmethod
    def create_custom(
        description: str,
        domain: str = 'general',
        difficulty: float = 0.5,
        **kwargs
    ) -> Task:
        """Create a custom task"""
        return Task(
            task_id=f"task_custom_{int(time.time())}",
            description=description,
            domain=domain,
            difficulty=difficulty,
            constraints=kwargs.get('constraints', {}),
            success_criteria=kwargs.get('success_criteria', {}),
        )


class AntiFramework:
    """Adversarial constraint mutation system"""

    @staticmethod
    def mutate_task(task: Task, mutation_rate: float = 0.3) -> Task:
        """
        Apply adversarial mutations to force adaptation

        In v0.1: Basic constraint modifications
        In production: More sophisticated mutations
        """
        if random.random() > mutation_rate:
            return task  # No mutation

        mutations = [
            'remove_constraint',
            'invert_objective',
            'increase_difficulty',
            'cross_domain',
            'resource_starve',
        ]

        mutation = random.choice(mutations)

        if mutation == 'remove_constraint':
            # Remove a random constraint
            if task.constraints:
                key = random.choice(list(task.constraints.keys()))
                task.constraints.pop(key, None)

        elif mutation == 'invert_objective':
            # Invert success criteria
            for key in task.success_criteria:
                if key.startswith('min_'):
                    new_key = key.replace('min_', 'max_')
                    task.success_criteria[new_key] = 1.0 - task.success_criteria.pop(key)

        elif mutation == 'increase_difficulty':
            task.difficulty = min(1.0, task.difficulty * 1.5)

        elif mutation == 'cross_domain':
            domains = ['code', 'business', 'science', 'design', 'math']
            other_domains = [d for d in domains if d != task.domain]
            if other_domains:
                task.domain = random.choice(other_domains)

        elif mutation == 'resource_starve':
            task.constraints['max_time'] = max(10, task.constraints.get('max_time', 60) // 2)

        return task


class ArchitectForge:
    """
    Main orchestrator for the Architect Forge system

    Coordinates MirrorNet, Sandbox, Jury, and Ledger to create
    a self-improving meta-intelligence.
    """

    def __init__(self, population_size: int = 16):
        self.mirrornet = MirrorNet(population_size=population_size)
        self.sandbox = Sandbox()
        self.jury = Jury()
        self.ledger = OuroborosLedger()

        self.cycle_count = 0
        self.history: List[TrainingCycleResult] = []

    def initialize(self) -> None:
        """Initialize the Forge"""
        print("🔥 Initializing Architect Forge...")

        # Initialize population
        self.mirrornet.initialize_population()

        # Record creation events
        for architect in self.mirrornet.architects:
            self.ledger.record_event(
                event_type=EventType.ARCHITECT_CREATED,
                data={
                    'archetype': architect.archetype.value,
                    'generation': architect.generation,
                    'parent_ids': architect.parent_ids,
                },
                architect_id=architect.id,
            )

        print(f"✓ Initialized {len(self.mirrornet.architects)} architects")
        print(f"✓ Population diversity: {self.mirrornet.get_diversity_score():.2%}")

    def training_cycle(
        self,
        num_tasks: int = 5,
        mutation_rate: float = 0.3,
        fidelity: FidelityLevel = FidelityLevel.MEDIUM
    ) -> TrainingCycleResult:
        """
        Run one complete training cycle

        1. Generate tasks
        2. Apply anti-framework mutations
        3. Architects attempt solutions
        4. Sandbox tests solutions
        5. Jury evaluates
        6. Record to ledger
        7. Create apprentices from best
        8. Evolve population

        Returns:
            TrainingCycleResult with metrics
        """
        start_time = time.time()
        self.cycle_count += 1

        print(f"\n{'='*60}")
        print(f"🔄 Training Cycle #{self.cycle_count}")
        print(f"{'='*60}")

        # 1. Generate tasks
        print(f"\n📋 Generating {num_tasks} tasks...")
        tasks = TaskGenerator.create_batch(
            domains=['code', 'business', 'science', 'design'],
            difficulties=[0.3, 0.5, 0.7],
            count=num_tasks
        )

        # 2. Apply anti-framework mutations
        print(f"🔀 Applying anti-framework mutations (rate={mutation_rate:.0%})...")
        mutated_tasks = []
        for task in tasks:
            mutated = AntiFramework.mutate_task(task, mutation_rate)
            mutated_tasks.append(mutated)

        # 3. Architects attempt solutions
        print(f"\n🏗️  {len(self.mirrornet.architects)} architects solving {len(mutated_tasks)} tasks...")
        solutions = {}

        for architect in self.mirrornet.architects:
            for task in mutated_tasks:
                solution = architect.solve(task.__dict__)
                solutions[(architect.id, task.task_id)] = solution

                # Record to ledger
                self.ledger.record_event(
                    event_type=EventType.SOLUTION_GENERATED,
                    data={
                        'task_id': task.task_id,
                        'task_domain': task.domain,
                        'task_difficulty': task.difficulty,
                    },
                    architect_id=architect.id,
                )

        print(f"✓ Generated {len(solutions)} solutions")

        # 4. Sandbox testing
        print(f"\n🧪 Testing solutions in Sandbox (fidelity={fidelity.value})...")
        results = {}

        for (arch_id, task_id), solution in solutions.items():
            result = self.sandbox.test_solution(solution, fidelity=fidelity)
            results[(arch_id, task_id)] = result

            # Record to ledger
            self.ledger.record_event(
                event_type=EventType.SOLUTION_TESTED,
                data={
                    'task_id': task_id,
                    'success': result.success,
                    'metrics': result.metrics,
                },
                architect_id=arch_id,
            )

        print(f"✓ Tested {len(results)} solutions")

        # 5. Jury evaluation
        print(f"\n⚖️  Jury evaluating solutions...")
        verdicts = {}
        approved_solutions = []
        quality_scores = []

        for (arch_id, task_id), result in results.items():
            solution = solutions[(arch_id, task_id)]

            context = {
                'safety_violations': result.safety_violations,
                'resource_usage': result.resource_usage.__dict__,
                'metrics': result.metrics,
            }

            verdict = self.jury.evaluate_solution(solution, context)
            verdicts[(arch_id, task_id)] = verdict

            quality_scores.append(verdict.final_score)

            if verdict.recommendation == 'approve':
                approved_solutions.append((arch_id, task_id, solution, verdict))

            # Record to ledger
            self.ledger.record_event(
                event_type=EventType.SOLUTION_EVALUATED,
                data={
                    'task_id': task_id,
                    'verdict': {
                        'final_score': verdict.final_score,
                        'recommendation': verdict.recommendation,
                        'consensus_level': verdict.consensus_level,
                    },
                },
                architect_id=arch_id,
            )

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        best_score = max(quality_scores) if quality_scores else 0.0

        print(f"✓ Evaluated {len(verdicts)} solutions")
        print(f"  • Approved: {len(approved_solutions)}")
        print(f"  • Average quality: {avg_quality:.2%}")
        print(f"  • Best score: {best_score:.2%}")

        # 6. Create apprentices from best solutions
        print(f"\n🎓 Creating apprentices from approved solutions...")
        apprentices_created = 0

        for arch_id, task_id, solution, verdict in approved_solutions[:5]:  # Top 5
            # In v0.1, apprentice is just a record
            # In production, this would compile to deployable agent

            apprentice_id = f"apprentice_{self.cycle_count}_{apprentices_created:03d}"

            self.ledger.record_event(
                event_type=EventType.APPRENTICE_CREATED,
                data={
                    'parent_architect': arch_id,
                    'task_id': task_id,
                    'quality_score': verdict.final_score,
                    'solution': solution,
                },
                architect_id=apprentice_id,
            )

            apprentices_created += 1

        print(f"✓ Created {apprentices_created} apprentices")

        # 7. Evolve population
        print(f"\n🧬 Evolving population...")
        fitness_scores = {}

        for arch_id in [a.id for a in self.mirrornet.architects]:
            # Calculate fitness from verdicts
            arch_verdicts = [v for (aid, tid), v in verdicts.items() if aid == arch_id]

            if arch_verdicts:
                avg_score = sum(v.final_score for v in arch_verdicts) / len(arch_verdicts)
                fitness_scores[arch_id] = avg_score
            else:
                fitness_scores[arch_id] = 0.0

        self.mirrornet.evolve_population(fitness_scores)

        # Record evolution
        self.ledger.record_event(
            event_type=EventType.POPULATION_EVOLVED,
            data={
                'generation': self.mirrornet.generation,
                'diversity': self.mirrornet.get_diversity_score(),
                'fitness_scores': fitness_scores,
            },
            architect_id='system',
        )

        diversity = self.mirrornet.get_diversity_score()
        print(f"✓ Population evolved to generation {self.mirrornet.generation}")
        print(f"  • Diversity: {diversity:.2%}")

        # 8. Results
        duration = time.time() - start_time

        result = TrainingCycleResult(
            cycle_number=self.cycle_count,
            tasks_attempted=len(tasks),
            solutions_generated=len(solutions),
            solutions_approved=len(approved_solutions),
            apprentices_created=apprentices_created,
            population_diversity=diversity,
            average_quality=avg_quality,
            best_solution_score=best_score,
            duration=duration,
        )

        self.history.append(result)

        print(f"\n⏱️  Cycle completed in {duration:.2f}s")

        return result

    def run_training(
        self,
        num_cycles: int = 10,
        tasks_per_cycle: int = 5,
        mutation_rate: float = 0.3
    ) -> List[TrainingCycleResult]:
        """
        Run multiple training cycles

        Args:
            num_cycles: Number of cycles to run
            tasks_per_cycle: Tasks per cycle
            mutation_rate: Anti-framework mutation rate

        Returns:
            List of TrainingCycleResults
        """
        print(f"\n🚀 Starting training: {num_cycles} cycles")

        results = []

        for i in range(num_cycles):
            result = self.training_cycle(
                num_tasks=tasks_per_cycle,
                mutation_rate=mutation_rate,
            )
            results.append(result)

        print(f"\n{'='*60}")
        print(f"✅ Training complete!")
        print(f"{'='*60}")
        print(f"Total cycles: {num_cycles}")
        print(f"Total solutions: {sum(r.solutions_generated for r in results)}")
        print(f"Total apprentices: {sum(r.apprentices_created for r in results)}")
        print(f"Final diversity: {results[-1].population_diversity:.2%}")
        print(f"Final avg quality: {results[-1].average_quality:.2%}")

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get Forge statistics"""
        return {
            'cycles_run': self.cycle_count,
            'population_size': len(self.mirrornet.architects),
            'population_diversity': self.mirrornet.get_diversity_score(),
            'ledger_stats': self.ledger.get_stats(),
            'training_history': [
                {
                    'cycle': r.cycle_number,
                    'quality': r.average_quality,
                    'diversity': r.population_diversity,
                    'apprentices': r.apprentices_created,
                }
                for r in self.history
            ],
        }

    def save_state(self, directory: str) -> None:
        """Save complete Forge state"""
        import os
        os.makedirs(directory, exist_ok=True)

        self.mirrornet.save(f"{directory}/mirrornet.json")
        self.ledger.save(f"{directory}/ledger.json")

        print(f"✓ Saved Forge state to {directory}/")

    @classmethod
    def load_state(cls, directory: str) -> 'ArchitectForge':
        """Load Forge state from directory"""
        forge = cls()

        forge.mirrornet = MirrorNet.load(f"{directory}/mirrornet.json")
        forge.ledger = OuroborosLedger.load(f"{directory}/ledger.json")

        print(f"✓ Loaded Forge state from {directory}/")

        return forge
