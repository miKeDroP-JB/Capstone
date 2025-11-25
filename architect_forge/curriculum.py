"""
CURRICULUM GENERATOR - Task and Environment Generation
═══════════════════════════════════════════════════════════════
Generates curricula, environments, tasks, and evaluation regimes.
Progressive difficulty scaling based on performance.

"The curriculum doesn't just teach.
 It discovers what needs to be learned."
═══════════════════════════════════════════════════════════════
"""

import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class TaskType(Enum):
    """Types of tasks the Forge can generate"""
    CODE = "code"                       # Software development
    STRATEGY = "strategy"               # Business strategy
    DESIGN = "design"                   # System/UX design
    ANALYSIS = "analysis"               # Data analysis
    COMMUNICATION = "communication"     # Writing, persuasion
    SECURITY = "security"               # Security testing
    INTEGRATION = "integration"         # System integration
    OPTIMIZATION = "optimization"       # Performance tuning
    CREATIVE = "creative"               # Novel solutions
    META = "meta"                       # Self-improvement


class Difficulty(Enum):
    """Task difficulty levels"""
    TRIVIAL = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5
    IMPOSSIBLE = 6  # The goal


@dataclass
class Task:
    """A task for architects to solve"""
    task_id: str
    task_type: str
    objective: str
    constraints: List[str]
    success_criteria: str
    difficulty: Difficulty = Difficulty.MEDIUM
    context: Dict[str, Any] = field(default_factory=dict)
    time_limit_seconds: Optional[int] = None
    resources_available: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "objective": self.objective,
            "constraints": self.constraints,
            "success_criteria": self.success_criteria,
            "difficulty": self.difficulty.value,
            "time_limit_seconds": self.time_limit_seconds
        }


@dataclass
class CurriculumLevel:
    """A level in the curriculum"""
    level: int
    name: str
    difficulty: Difficulty
    task_types: List[TaskType]
    constraint_count: int
    success_threshold: float  # Required score to advance


class CurriculumGenerator:
    """
    Generates progressive curricula for training architect agents.

    Features:
    - Adaptive difficulty based on performance
    - Cross-domain task generation
    - Constraint injection
    - Impossibility seeding (tasks at the edge of capability)
    """

    # Task templates by type
    TASK_TEMPLATES = {
        TaskType.CODE: [
            "Implement {feature} with {constraint1} and {constraint2}",
            "Refactor {system} to achieve {metric} improvement",
            "Debug and fix {issue} in production {system}",
            "Design API for {domain} that handles {scale} requests",
        ],
        TaskType.STRATEGY: [
            "Develop go-to-market strategy for {product} targeting {market}",
            "Create acquisition strategy to achieve {metric} in {timeframe}",
            "Design pricing model for {service} that maximizes {objective}",
        ],
        TaskType.DESIGN: [
            "Design user experience for {feature} optimizing for {metric}",
            "Create system architecture for {scale} with {constraint}",
            "Design data model for {domain} supporting {operations}",
        ],
        TaskType.ANALYSIS: [
            "Analyze {dataset} to identify {pattern}",
            "Research {topic} and synthesize {deliverable}",
            "Evaluate {options} based on {criteria}",
        ],
        TaskType.COMMUNICATION: [
            "Write {document_type} for {audience} about {topic}",
            "Create pitch for {product} targeting {investor_type}",
            "Develop messaging strategy for {campaign}",
        ],
        TaskType.SECURITY: [
            "Identify vulnerabilities in {system}",
            "Design security architecture for {application}",
            "Create incident response plan for {threat}",
        ],
        TaskType.INTEGRATION: [
            "Integrate {system_a} with {system_b} handling {edge_cases}",
            "Design migration from {legacy} to {modern}",
            "Create sync protocol between {sources}",
        ],
        TaskType.OPTIMIZATION: [
            "Optimize {metric} for {system} by {percentage}",
            "Reduce {resource} consumption in {component}",
            "Improve {process} efficiency by {factor}",
        ],
        TaskType.CREATIVE: [
            "Generate novel approach to {problem} that breaks {assumption}",
            "Combine {domain_a} and {domain_b} to create {innovation}",
            "Invert {convention} to achieve {outcome}",
        ],
        TaskType.META: [
            "Improve own {capability} by analyzing {history}",
            "Generate curriculum for training {agent_type}",
            "Design evaluation criteria for {task_class}",
        ],
    }

    # Constraint types
    CONSTRAINT_TYPES = [
        "time_limit",
        "resource_limit",
        "compatibility",
        "security",
        "scalability",
        "cost",
        "simplicity",
        "extensibility",
        "testability",
        "documentation",
    ]

    # Fill values for templates
    FILL_VALUES = {
        "feature": ["authentication", "search", "analytics", "notification", "payment", "messaging"],
        "system": ["backend API", "frontend app", "database layer", "cache system", "message queue"],
        "metric": ["latency", "throughput", "conversion", "retention", "satisfaction"],
        "product": ["SaaS platform", "mobile app", "AI service", "marketplace", "developer tool"],
        "market": ["enterprise", "SMB", "consumer", "developer", "healthcare"],
        "domain": ["e-commerce", "fintech", "healthcare", "education", "logistics"],
        "scale": ["1000 users", "1M requests/day", "global", "real-time", "high-availability"],
        "constraint": ["zero downtime", "GDPR compliance", "air-gapped", "mobile-first"],
        "timeframe": ["90 days", "Q4", "year-end", "next sprint"],
        "percentage": ["50%", "10x", "order of magnitude"],
    }

    def __init__(self):
        self.difficulty_calibration: Dict[str, float] = {}  # task_type -> current difficulty
        self.generated_count = 0
        self.curriculum_levels = self._define_levels()

    def _define_levels(self) -> List[CurriculumLevel]:
        """Define curriculum progression levels"""
        return [
            CurriculumLevel(
                level=1,
                name="Fundamentals",
                difficulty=Difficulty.EASY,
                task_types=[TaskType.CODE, TaskType.ANALYSIS],
                constraint_count=1,
                success_threshold=0.7
            ),
            CurriculumLevel(
                level=2,
                name="Applied Skills",
                difficulty=Difficulty.MEDIUM,
                task_types=[TaskType.CODE, TaskType.DESIGN, TaskType.ANALYSIS],
                constraint_count=2,
                success_threshold=0.75
            ),
            CurriculumLevel(
                level=3,
                name="Complex Challenges",
                difficulty=Difficulty.HARD,
                task_types=[TaskType.STRATEGY, TaskType.INTEGRATION, TaskType.SECURITY],
                constraint_count=3,
                success_threshold=0.8
            ),
            CurriculumLevel(
                level=4,
                name="Expert Domains",
                difficulty=Difficulty.EXPERT,
                task_types=[TaskType.OPTIMIZATION, TaskType.CREATIVE],
                constraint_count=4,
                success_threshold=0.85
            ),
            CurriculumLevel(
                level=5,
                name="Impossibility",
                difficulty=Difficulty.IMPOSSIBLE,
                task_types=[TaskType.META, TaskType.CREATIVE],
                constraint_count=5,
                success_threshold=0.9
            ),
        ]

    def generate_task(
        self,
        task_type: Optional[TaskType] = None,
        difficulty: Optional[Difficulty] = None
    ) -> Task:
        """Generate a task"""
        task_type = task_type or random.choice(list(TaskType))
        difficulty = difficulty or self._get_calibrated_difficulty(task_type.value)

        # Get template
        templates = self.TASK_TEMPLATES.get(task_type, self.TASK_TEMPLATES[TaskType.CODE])
        template = random.choice(templates)

        # Fill template
        objective = self._fill_template(template)

        # Generate constraints based on difficulty
        num_constraints = min(difficulty.value, len(self.CONSTRAINT_TYPES))
        constraints = self._generate_constraints(num_constraints)

        # Generate success criteria
        success_criteria = self._generate_success_criteria(task_type, difficulty)

        self.generated_count += 1

        return Task(
            task_id=f"task_{uuid4().hex[:8]}",
            task_type=task_type.value,
            objective=objective,
            constraints=constraints,
            success_criteria=success_criteria,
            difficulty=difficulty,
            time_limit_seconds=self._calculate_time_limit(difficulty),
            resources_available=self._get_available_resources(difficulty)
        )

    def _fill_template(self, template: str) -> str:
        """Fill template placeholders with values"""
        result = template
        for key, values in self.FILL_VALUES.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, random.choice(values), 1)
            # Also handle numbered variants
            for i in range(1, 4):
                placeholder_n = f"{{{key}{i}}}"
                if placeholder_n in result:
                    result = result.replace(placeholder_n, random.choice(values), 1)
        return result

    def _generate_constraints(self, count: int) -> List[str]:
        """Generate task constraints"""
        constraint_templates = {
            "time_limit": "Complete within {time} seconds",
            "resource_limit": "Use no more than {amount} {resource}",
            "compatibility": "Must be compatible with {system}",
            "security": "Must pass {security_standard} compliance",
            "scalability": "Must scale to {scale}",
            "cost": "Stay within ${budget} budget",
            "simplicity": "Maximum {lines} lines of code",
            "extensibility": "Must support future {feature}",
            "testability": "Achieve {coverage}% test coverage",
            "documentation": "Include {doc_type} documentation",
        }

        selected = random.sample(self.CONSTRAINT_TYPES, min(count, len(self.CONSTRAINT_TYPES)))
        constraints = []

        for c_type in selected:
            template = constraint_templates.get(c_type, f"Satisfy {c_type} requirement")
            # Simple fill
            constraint = template.format(
                time=random.choice(["30", "60", "300"]),
                amount=random.choice(["100MB", "1GB", "1000"]),
                resource=random.choice(["memory", "CPU", "API calls"]),
                system=random.choice(["legacy API", "mobile", "cloud"]),
                security_standard=random.choice(["SOC2", "HIPAA", "GDPR"]),
                scale=random.choice(["10x current", "1M users", "global"]),
                budget=random.choice(["1000", "10000", "100"]),
                lines=random.choice(["100", "500", "1000"]),
                feature=random.choice(["plugins", "themes", "integrations"]),
                coverage=random.choice(["80", "90", "95"]),
                doc_type=random.choice(["API", "user", "developer"])
            )
            constraints.append(constraint)

        return constraints

    def _generate_success_criteria(self, task_type: TaskType, difficulty: Difficulty) -> str:
        """Generate success criteria for a task"""
        criteria_by_type = {
            TaskType.CODE: "Working implementation that passes all tests",
            TaskType.STRATEGY: "Actionable plan with measurable outcomes",
            TaskType.DESIGN: "Complete specification with rationale",
            TaskType.ANALYSIS: "Documented findings with recommendations",
            TaskType.COMMUNICATION: "Clear, compelling content for target audience",
            TaskType.SECURITY: "Comprehensive assessment with remediation steps",
            TaskType.INTEGRATION: "Seamless data flow with error handling",
            TaskType.OPTIMIZATION: "Measurable improvement in target metric",
            TaskType.CREATIVE: "Novel solution that breaks stated assumption",
            TaskType.META: "Self-improvement demonstrated through metrics",
        }

        base = criteria_by_type.get(task_type, "Complete the objective successfully")

        if difficulty.value >= Difficulty.HARD.value:
            base += " under adversarial conditions"
        if difficulty.value >= Difficulty.EXPERT.value:
            base += " with emergent capability demonstration"

        return base

    def _get_calibrated_difficulty(self, task_type: str) -> Difficulty:
        """Get difficulty calibrated to current performance"""
        current = self.difficulty_calibration.get(task_type, 3.0)
        return Difficulty(min(6, max(1, int(current))))

    def _calculate_time_limit(self, difficulty: Difficulty) -> int:
        """Calculate time limit based on difficulty"""
        base_times = {
            Difficulty.TRIVIAL: 30,
            Difficulty.EASY: 60,
            Difficulty.MEDIUM: 180,
            Difficulty.HARD: 300,
            Difficulty.EXPERT: 600,
            Difficulty.IMPOSSIBLE: 1200,
        }
        return base_times.get(difficulty, 180)

    def _get_available_resources(self, difficulty: Difficulty) -> List[str]:
        """Get available resources based on difficulty (harder = fewer resources)"""
        all_resources = ["documentation", "examples", "hints", "tools", "libraries", "templates"]
        available_count = max(1, 6 - difficulty.value)
        return random.sample(all_resources, available_count)

    def update_difficulty(self, task_type: str, success_rate: float) -> None:
        """Update difficulty calibration based on performance"""
        current = self.difficulty_calibration.get(task_type, 3.0)

        if success_rate > 0.85:
            # Too easy, increase difficulty
            new_difficulty = min(6.0, current + 0.5)
        elif success_rate < 0.5:
            # Too hard, decrease difficulty
            new_difficulty = max(1.0, current - 0.3)
        else:
            # About right, small adjustment
            new_difficulty = current + (success_rate - 0.7) * 0.2

        self.difficulty_calibration[task_type] = new_difficulty

    def generate_harder_task(self, previous_task: Task, result: 'TournamentResult') -> Task:
        """Generate a harder variant of a task based on tournament result"""
        new_difficulty = Difficulty(min(6, previous_task.difficulty.value + 1))

        # Add more constraints
        new_constraints = previous_task.constraints.copy()
        new_constraints.extend(self._generate_constraints(1))

        return Task(
            task_id=f"task_{uuid4().hex[:8]}",
            task_type=previous_task.task_type,
            objective=previous_task.objective + " (advanced variant)",
            constraints=new_constraints,
            success_criteria=previous_task.success_criteria + " with higher standards",
            difficulty=new_difficulty,
            context={"previous_task_id": previous_task.task_id}
        )

    def generate_curriculum(self, target_level: int = 5) -> List[Task]:
        """Generate a full curriculum up to target level"""
        curriculum = []

        for level in self.curriculum_levels:
            if level.level > target_level:
                break

            # Generate tasks for this level
            for task_type in level.task_types:
                task = self.generate_task(task_type, level.difficulty)
                curriculum.append(task)

        return curriculum

    def get_statistics(self) -> Dict[str, Any]:
        """Get curriculum generator statistics"""
        return {
            "total_generated": self.generated_count,
            "difficulty_calibration": self.difficulty_calibration,
            "curriculum_levels": len(self.curriculum_levels)
        }
