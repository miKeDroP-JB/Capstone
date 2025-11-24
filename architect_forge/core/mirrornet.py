"""
MirrorNet: Population-based architect agent system

Maintains diverse population of architect-agents with different inductive biases.
"""

import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import time


class ArchetypeType(Enum):
    """Different architect personalities/approaches"""
    ANALYTICAL_OPTIMIZER = "analytical_optimizer"
    CREATIVE_EXPLORER = "creative_explorer"
    CONSERVATIVE_VALIDATOR = "conservative_validator"
    AGGRESSIVE_INNOVATOR = "aggressive_innovator"
    PATTERN_SYNTHESIZER = "pattern_synthesizer"
    CONSTRAINT_BREAKER = "constraint_breaker"
    RESOURCE_MINIMIZER = "resource_minimizer"
    SCALE_ARCHITECT = "scale_architect"
    ADVERSARIAL_THINKER = "adversarial_thinker"
    RAPID_PROTOTYPER = "rapid_prototyper"
    SYSTEMATIC_DEBUGGER = "systematic_debugger"
    INTUITIVE_DESIGNER = "intuitive_designer"
    EFFICIENCY_FANATIC = "efficiency_fanatic"
    ROBUSTNESS_GUARDIAN = "robustness_guardian"
    INNOVATION_MAXIMIZER = "innovation_maximizer"
    PRAGMATIC_BUILDER = "pragmatic_builder"


@dataclass
class Architect:
    """Individual architect agent"""
    id: str
    archetype: ArchetypeType
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Personality parameters (0.0 to 1.0)
    creativity: float = 0.5
    risk_tolerance: float = 0.5
    optimization_focus: float = 0.5
    speed_vs_quality: float = 0.5

    def __post_init__(self):
        """Initialize personality based on archetype"""
        archetype_profiles = {
            ArchetypeType.ANALYTICAL_OPTIMIZER: {
                'creativity': 0.3, 'risk_tolerance': 0.2,
                'optimization_focus': 0.9, 'speed_vs_quality': 0.3
            },
            ArchetypeType.CREATIVE_EXPLORER: {
                'creativity': 0.95, 'risk_tolerance': 0.8,
                'optimization_focus': 0.4, 'speed_vs_quality': 0.6
            },
            ArchetypeType.CONSERVATIVE_VALIDATOR: {
                'creativity': 0.2, 'risk_tolerance': 0.1,
                'optimization_focus': 0.6, 'speed_vs_quality': 0.2
            },
            ArchetypeType.AGGRESSIVE_INNOVATOR: {
                'creativity': 0.85, 'risk_tolerance': 0.95,
                'optimization_focus': 0.5, 'speed_vs_quality': 0.8
            },
            ArchetypeType.PATTERN_SYNTHESIZER: {
                'creativity': 0.7, 'risk_tolerance': 0.5,
                'optimization_focus': 0.7, 'speed_vs_quality': 0.4
            },
            ArchetypeType.CONSTRAINT_BREAKER: {
                'creativity': 0.9, 'risk_tolerance': 0.85,
                'optimization_focus': 0.3, 'speed_vs_quality': 0.7
            },
            ArchetypeType.RESOURCE_MINIMIZER: {
                'creativity': 0.6, 'risk_tolerance': 0.4,
                'optimization_focus': 0.95, 'speed_vs_quality': 0.5
            },
            ArchetypeType.SCALE_ARCHITECT: {
                'creativity': 0.5, 'risk_tolerance': 0.3,
                'optimization_focus': 0.8, 'speed_vs_quality': 0.3
            },
            ArchetypeType.ADVERSARIAL_THINKER: {
                'creativity': 0.75, 'risk_tolerance': 0.7,
                'optimization_focus': 0.6, 'speed_vs_quality': 0.6
            },
            ArchetypeType.RAPID_PROTOTYPER: {
                'creativity': 0.8, 'risk_tolerance': 0.8,
                'optimization_focus': 0.4, 'speed_vs_quality': 0.9
            },
            ArchetypeType.SYSTEMATIC_DEBUGGER: {
                'creativity': 0.4, 'risk_tolerance': 0.2,
                'optimization_focus': 0.7, 'speed_vs_quality': 0.2
            },
            ArchetypeType.INTUITIVE_DESIGNER: {
                'creativity': 0.9, 'risk_tolerance': 0.6,
                'optimization_focus': 0.5, 'speed_vs_quality': 0.6
            },
            ArchetypeType.EFFICIENCY_FANATIC: {
                'creativity': 0.5, 'risk_tolerance': 0.3,
                'optimization_focus': 1.0, 'speed_vs_quality': 0.4
            },
            ArchetypeType.ROBUSTNESS_GUARDIAN: {
                'creativity': 0.4, 'risk_tolerance': 0.15,
                'optimization_focus': 0.7, 'speed_vs_quality': 0.25
            },
            ArchetypeType.INNOVATION_MAXIMIZER: {
                'creativity': 1.0, 'risk_tolerance': 0.9,
                'optimization_focus': 0.6, 'speed_vs_quality': 0.7
            },
            ArchetypeType.PRAGMATIC_BUILDER: {
                'creativity': 0.5, 'risk_tolerance': 0.5,
                'optimization_focus': 0.6, 'speed_vs_quality': 0.7
            },
        }

        if self.archetype in archetype_profiles:
            profile = archetype_profiles[self.archetype]
            self.creativity = profile['creativity']
            self.risk_tolerance = profile['risk_tolerance']
            self.optimization_focus = profile['optimization_focus']
            self.speed_vs_quality = profile['speed_vs_quality']

    def solve(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a task based on this architect's personality

        In v0.1, this is a stub that returns personality-based approach.
        In production, this would call LLM with personality-tuned prompts.
        """
        approach = {
            'architect_id': self.id,
            'archetype': self.archetype.value,
            'task': task,
            'approach_profile': {
                'creativity': self.creativity,
                'risk_tolerance': self.risk_tolerance,
                'optimization_focus': self.optimization_focus,
                'speed_vs_quality': self.speed_vs_quality,
            },
            'timestamp': time.time(),
        }

        # Simulate solution generation based on personality
        # In production, this would be LLM calls with tuned system prompts
        solution = {
            'approach': approach,
            'estimated_quality': self._estimate_quality(task),
            'estimated_time': self._estimate_time(task),
            'estimated_risk': self.risk_tolerance,
            'novelty_score': self.creativity,
        }

        return solution

    def _estimate_quality(self, task: Dict[str, Any]) -> float:
        """Estimate solution quality based on personality"""
        base_quality = 0.5
        quality = base_quality + (self.optimization_focus * 0.3)
        quality += (1.0 - self.speed_vs_quality) * 0.2
        return min(1.0, quality)

    def _estimate_time(self, task: Dict[str, Any]) -> float:
        """Estimate time to solution based on personality"""
        base_time = 1.0
        time_factor = base_time * (1.0 - self.speed_vs_quality)
        return max(0.1, time_factor)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize architect to dictionary"""
        return {
            'id': self.id,
            'archetype': self.archetype.value,
            'fitness': self.fitness,
            'generation': self.generation,
            'parent_ids': self.parent_ids,
            'metadata': self.metadata,
            'personality': {
                'creativity': self.creativity,
                'risk_tolerance': self.risk_tolerance,
                'optimization_focus': self.optimization_focus,
                'speed_vs_quality': self.speed_vs_quality,
            }
        }


@dataclass
class PopulationMetrics:
    """Metrics about population diversity and health"""
    diversity_score: float
    average_fitness: float
    best_fitness: float
    worst_fitness: float
    archetype_distribution: Dict[str, int]
    generation: int


class MirrorNet:
    """
    Population-based architecture for diverse problem-solving

    Maintains diverse population of architect-agents, evolves them
    based on performance, and manages population diversity.
    """

    def __init__(self, population_size: int = 16):
        self.population_size = population_size
        self.architects: List[Architect] = []
        self.generation = 0
        self.history: List[PopulationMetrics] = []

    def initialize_population(self) -> None:
        """Create initial diverse population"""
        self.architects = []

        # Use all archetypes, cycling if population > archetypes
        archetypes = list(ArchetypeType)

        for i in range(self.population_size):
            archetype = archetypes[i % len(archetypes)]
            architect = Architect(
                id=f"arch_{self.generation}_{i:03d}",
                archetype=archetype,
                generation=self.generation,
            )
            self.architects.append(architect)

    def get_diversity_score(self) -> float:
        """Calculate population diversity (0.0 to 1.0)"""
        if not self.architects:
            return 0.0

        # Diversity based on archetype distribution
        archetype_counts = {}
        for arch in self.architects:
            archetype_counts[arch.archetype] = archetype_counts.get(arch.archetype, 0) + 1

        # Perfect diversity = uniform distribution
        ideal_count = self.population_size / len(ArchetypeType)
        diversity = 1.0 - sum(
            abs(count - ideal_count) / self.population_size
            for count in archetype_counts.values()
        ) / len(archetype_counts)

        return max(0.0, min(1.0, diversity))

    def get_metrics(self) -> PopulationMetrics:
        """Get current population metrics"""
        if not self.architects:
            return PopulationMetrics(
                diversity_score=0.0,
                average_fitness=0.0,
                best_fitness=0.0,
                worst_fitness=0.0,
                archetype_distribution={},
                generation=self.generation
            )

        fitnesses = [a.fitness for a in self.architects]
        archetype_dist = {}
        for arch in self.architects:
            archetype_dist[arch.archetype.value] = archetype_dist.get(arch.archetype.value, 0) + 1

        return PopulationMetrics(
            diversity_score=self.get_diversity_score(),
            average_fitness=sum(fitnesses) / len(fitnesses),
            best_fitness=max(fitnesses),
            worst_fitness=min(fitnesses),
            archetype_distribution=archetype_dist,
            generation=self.generation
        )

    def evolve_population(self, fitness_scores: Dict[str, float]) -> None:
        """
        Apply evolutionary pressure to population

        Uses:
        - Tournament selection
        - Crossover of successful patterns
        - Mutation for diversity
        - Elitism to preserve best
        """
        # Update fitness scores
        for architect in self.architects:
            if architect.id in fitness_scores:
                architect.fitness = fitness_scores[architect.id]

        # Sort by fitness
        self.architects.sort(key=lambda a: a.fitness, reverse=True)

        # Elitism: keep top 25%
        elite_count = max(2, self.population_size // 4)
        elite = self.architects[:elite_count]

        # Tournament selection for rest
        new_generation = elite.copy()

        while len(new_generation) < self.population_size:
            # Tournament selection
            parent1 = self._tournament_select(3)
            parent2 = self._tournament_select(3)

            # Crossover
            child = self._crossover(parent1, parent2)

            # Mutation
            if random.random() < 0.2:  # 20% mutation rate
                child = self._mutate(child)

            new_generation.append(child)

        self.architects = new_generation
        self.generation += 1

        # Record metrics
        self.history.append(self.get_metrics())

    def _tournament_select(self, tournament_size: int) -> Architect:
        """Select architect via tournament selection"""
        tournament = random.sample(self.architects, min(tournament_size, len(self.architects)))
        return max(tournament, key=lambda a: a.fitness)

    def _crossover(self, parent1: Architect, parent2: Architect) -> Architect:
        """Create child architect from two parents"""
        # Randomly choose archetype from either parent
        archetype = random.choice([parent1.archetype, parent2.archetype])

        child = Architect(
            id=f"arch_{self.generation + 1}_{len(self.architects):03d}",
            archetype=archetype,
            generation=self.generation + 1,
            parent_ids=[parent1.id, parent2.id],
        )

        # Blend personality traits
        child.creativity = (parent1.creativity + parent2.creativity) / 2
        child.risk_tolerance = (parent1.risk_tolerance + parent2.risk_tolerance) / 2
        child.optimization_focus = (parent1.optimization_focus + parent2.optimization_focus) / 2
        child.speed_vs_quality = (parent1.speed_vs_quality + parent2.speed_vs_quality) / 2

        return child

    def _mutate(self, architect: Architect) -> Architect:
        """Apply random mutation to architect"""
        mutation_rate = 0.1

        if random.random() < mutation_rate:
            architect.creativity = max(0.0, min(1.0, architect.creativity + random.gauss(0, 0.1)))
        if random.random() < mutation_rate:
            architect.risk_tolerance = max(0.0, min(1.0, architect.risk_tolerance + random.gauss(0, 0.1)))
        if random.random() < mutation_rate:
            architect.optimization_focus = max(0.0, min(1.0, architect.optimization_focus + random.gauss(0, 0.1)))
        if random.random() < mutation_rate:
            architect.speed_vs_quality = max(0.0, min(1.0, architect.speed_vs_quality + random.gauss(0, 0.1)))

        return architect

    def add_architect(self, architect: Architect) -> None:
        """Add new architect to population (e.g., successful apprentice)"""
        if len(self.architects) >= self.population_size:
            # Remove lowest fitness architect
            self.architects.sort(key=lambda a: a.fitness, reverse=True)
            self.architects = self.architects[:self.population_size - 1]

        self.architects.append(architect)

    def get_architect(self, architect_id: str) -> Optional[Architect]:
        """Get architect by ID"""
        for arch in self.architects:
            if arch.id == architect_id:
                return arch
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize MirrorNet to dictionary"""
        return {
            'population_size': self.population_size,
            'generation': self.generation,
            'architects': [a.to_dict() for a in self.architects],
            'metrics': self.get_metrics().__dict__,
            'history': [m.__dict__ for m in self.history],
        }

    def save(self, filepath: str) -> None:
        """Save MirrorNet state to file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'MirrorNet':
        """Load MirrorNet state from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        mirrornet = cls(population_size=data['population_size'])
        mirrornet.generation = data['generation']

        # Reconstruct architects
        mirrornet.architects = []
        for arch_data in data['architects']:
            arch = Architect(
                id=arch_data['id'],
                archetype=ArchetypeType(arch_data['archetype']),
                fitness=arch_data['fitness'],
                generation=arch_data['generation'],
                parent_ids=arch_data['parent_ids'],
                metadata=arch_data['metadata'],
            )
            pers = arch_data['personality']
            arch.creativity = pers['creativity']
            arch.risk_tolerance = pers['risk_tolerance']
            arch.optimization_focus = pers['optimization_focus']
            arch.speed_vs_quality = pers['speed_vs_quality']
            mirrornet.architects.append(arch)

        return mirrornet
