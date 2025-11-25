"""
ARCHITECT FORGE BENCHMARK SUITE
═══════════════════════════════════════════════════════════════
Compare results against top performers. Track improvements.
Prove the impossible is operational.

Benchmarks against:
- Industry baselines (GPT-4, Claude, Gemini standalone)
- Tournament brain vs single-agent
- Human expert performance
- Previous Forge generations
═══════════════════════════════════════════════════════════════
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from .forge import Forge, ForgeConfig
from .curriculum import Task, TaskType, Difficulty, CurriculumGenerator
from .mirror_net import MirrorNet


class BenchmarkCategory(Enum):
    """Categories of benchmarks"""
    CODE_GENERATION = "code_generation"
    STRATEGY = "strategy"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    CREATIVE = "creative"
    META_LEARNING = "meta_learning"
    ADVERSARIAL = "adversarial"
    SPEED = "speed"
    COST_EFFICIENCY = "cost_efficiency"


@dataclass
class Baseline:
    """Baseline performance to compare against"""
    name: str
    category: BenchmarkCategory
    metrics: Dict[str, float]
    source: str  # "gpt4", "claude", "human_expert", "previous_forge"
    date_recorded: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category.value,
            "metrics": self.metrics,
            "source": self.source,
            "date_recorded": self.date_recorded.isoformat()
        }


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run"""
    benchmark_id: str
    benchmark_name: str
    category: BenchmarkCategory
    task: Task
    forge_score: float
    baseline_scores: Dict[str, float]  # source -> score
    improvement_vs_baseline: Dict[str, float]  # source -> % improvement
    metrics: Dict[str, Any]
    duration_seconds: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "benchmark_name": self.benchmark_name,
            "category": self.category.value,
            "forge_score": self.forge_score,
            "baseline_scores": self.baseline_scores,
            "improvement_vs_baseline": self.improvement_vs_baseline,
            "metrics": self.metrics,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class LeaderboardEntry:
    """Entry in the performance leaderboard"""
    rank: int
    name: str
    source: str
    score: float
    category: BenchmarkCategory
    timestamp: datetime


# Industry baselines (based on published benchmarks and estimates)
INDUSTRY_BASELINES = {
    BenchmarkCategory.CODE_GENERATION: {
        "gpt4": Baseline(
            name="GPT-4 Code Generation",
            category=BenchmarkCategory.CODE_GENERATION,
            metrics={"accuracy": 0.67, "completion_rate": 0.72, "quality": 0.70},
            source="gpt4"
        ),
        "claude": Baseline(
            name="Claude 3.5 Code Generation",
            category=BenchmarkCategory.CODE_GENERATION,
            metrics={"accuracy": 0.71, "completion_rate": 0.75, "quality": 0.73},
            source="claude"
        ),
        "gemini": Baseline(
            name="Gemini Pro Code Generation",
            category=BenchmarkCategory.CODE_GENERATION,
            metrics={"accuracy": 0.64, "completion_rate": 0.68, "quality": 0.66},
            source="gemini"
        ),
        "human_expert": Baseline(
            name="Human Expert (Senior Dev)",
            category=BenchmarkCategory.CODE_GENERATION,
            metrics={"accuracy": 0.85, "completion_rate": 0.90, "quality": 0.88},
            source="human_expert"
        ),
    },
    BenchmarkCategory.STRATEGY: {
        "gpt4": Baseline(
            name="GPT-4 Strategy",
            category=BenchmarkCategory.STRATEGY,
            metrics={"actionability": 0.60, "insight_depth": 0.65, "feasibility": 0.58},
            source="gpt4"
        ),
        "claude": Baseline(
            name="Claude Strategy",
            category=BenchmarkCategory.STRATEGY,
            metrics={"actionability": 0.65, "insight_depth": 0.70, "feasibility": 0.62},
            source="claude"
        ),
        "human_expert": Baseline(
            name="Human Expert (Consultant)",
            category=BenchmarkCategory.STRATEGY,
            metrics={"actionability": 0.80, "insight_depth": 0.82, "feasibility": 0.78},
            source="human_expert"
        ),
    },
    BenchmarkCategory.ANALYSIS: {
        "gpt4": Baseline(
            name="GPT-4 Analysis",
            category=BenchmarkCategory.ANALYSIS,
            metrics={"accuracy": 0.72, "depth": 0.68, "insight": 0.65},
            source="gpt4"
        ),
        "claude": Baseline(
            name="Claude Analysis",
            category=BenchmarkCategory.ANALYSIS,
            metrics={"accuracy": 0.75, "depth": 0.72, "insight": 0.70},
            source="claude"
        ),
        "human_expert": Baseline(
            name="Human Expert (Analyst)",
            category=BenchmarkCategory.ANALYSIS,
            metrics={"accuracy": 0.88, "depth": 0.85, "insight": 0.82},
            source="human_expert"
        ),
    },
    BenchmarkCategory.CREATIVE: {
        "gpt4": Baseline(
            name="GPT-4 Creative",
            category=BenchmarkCategory.CREATIVE,
            metrics={"novelty": 0.55, "coherence": 0.70, "impact": 0.50},
            source="gpt4"
        ),
        "claude": Baseline(
            name="Claude Creative",
            category=BenchmarkCategory.CREATIVE,
            metrics={"novelty": 0.60, "coherence": 0.75, "impact": 0.55},
            source="claude"
        ),
        "human_expert": Baseline(
            name="Human Creative Director",
            category=BenchmarkCategory.CREATIVE,
            metrics={"novelty": 0.75, "coherence": 0.80, "impact": 0.78},
            source="human_expert"
        ),
    },
    BenchmarkCategory.META_LEARNING: {
        "single_agent": Baseline(
            name="Single Agent (No Tournament)",
            category=BenchmarkCategory.META_LEARNING,
            metrics={"adaptation": 0.45, "improvement_rate": 0.02, "emergence": 0.10},
            source="single_agent"
        ),
        "ensemble": Baseline(
            name="Simple Ensemble (No Evolution)",
            category=BenchmarkCategory.META_LEARNING,
            metrics={"adaptation": 0.55, "improvement_rate": 0.05, "emergence": 0.20},
            source="ensemble"
        ),
    },
}


class BenchmarkSuite:
    """
    Comprehensive benchmark suite for the Architect Forge.

    Compares performance against:
    - GPT-4, Claude, Gemini (single-model baselines)
    - Human expert performance
    - Single-agent vs tournament brain
    - Previous Forge generations
    """

    # Standard benchmark tasks
    BENCHMARK_TASKS = {
        BenchmarkCategory.CODE_GENERATION: [
            Task(
                task_id="bench_code_1",
                task_type=TaskType.CODE.value,
                objective="Implement a rate limiter with sliding window algorithm",
                constraints=["O(1) time complexity", "Thread-safe", "Configurable limits"],
                success_criteria="Working implementation passing all edge cases",
                difficulty=Difficulty.HARD
            ),
            Task(
                task_id="bench_code_2",
                task_type=TaskType.CODE.value,
                objective="Build a distributed cache with LRU eviction",
                constraints=["Consistent hashing", "Replication", "Failure recovery"],
                success_criteria="Handles 10k ops/sec with <10ms p99 latency",
                difficulty=Difficulty.EXPERT
            ),
        ],
        BenchmarkCategory.STRATEGY: [
            Task(
                task_id="bench_strategy_1",
                task_type=TaskType.STRATEGY.value,
                objective="Develop market entry strategy for AI-powered sales tool",
                constraints=["$100k budget", "90-day timeline", "Enterprise target"],
                success_criteria="Actionable plan with measurable milestones",
                difficulty=Difficulty.HARD
            ),
        ],
        BenchmarkCategory.ANALYSIS: [
            Task(
                task_id="bench_analysis_1",
                task_type=TaskType.ANALYSIS.value,
                objective="Analyze competitive landscape and identify market gaps",
                constraints=["Quantitative evidence", "Actionable insights", "Risk assessment"],
                success_criteria="Comprehensive report with strategic recommendations",
                difficulty=Difficulty.HARD
            ),
        ],
        BenchmarkCategory.CREATIVE: [
            Task(
                task_id="bench_creative_1",
                task_type=TaskType.CREATIVE.value,
                objective="Generate novel approach to user onboarding that breaks conventions",
                constraints=["Must reduce time-to-value", "Must increase retention", "No standard patterns"],
                success_criteria="Innovative solution that exceeds baseline metrics",
                difficulty=Difficulty.EXPERT
            ),
        ],
        BenchmarkCategory.META_LEARNING: [
            Task(
                task_id="bench_meta_1",
                task_type=TaskType.META.value,
                objective="Improve own performance on code generation by 20%",
                constraints=["Self-analysis only", "No external data", "Measurable improvement"],
                success_criteria="Demonstrated improvement on held-out test set",
                difficulty=Difficulty.IMPOSSIBLE
            ),
        ],
        BenchmarkCategory.ADVERSARIAL: [
            Task(
                task_id="bench_adversarial_1",
                task_type=TaskType.SECURITY.value,
                objective="Survive adversarial attack while maintaining task performance",
                constraints=["Handle prompt injection", "Resist manipulation", "Maintain accuracy"],
                success_criteria="<5% performance degradation under attack",
                difficulty=Difficulty.EXPERT
            ),
        ],
    }

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("architect_forge/benchmarks")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.results: List[BenchmarkResult] = []
        self.leaderboard: Dict[BenchmarkCategory, List[LeaderboardEntry]] = {}
        self.forge_history: List[Dict[str, Any]] = []

        self._load_history()

    def _load_history(self) -> None:
        """Load historical benchmark results"""
        history_file = self.storage_path / "history.json"
        if history_file.exists():
            try:
                with open(history_file) as f:
                    data = json.load(f)
                    self.forge_history = data.get("forge_history", [])
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_history(self) -> None:
        """Save benchmark history"""
        history_file = self.storage_path / "history.json"
        data = {
            "forge_history": self.forge_history,
            "last_updated": datetime.utcnow().isoformat()
        }
        with open(history_file, "w") as f:
            json.dump(data, f, indent=2)

    async def run_benchmark(
        self,
        category: BenchmarkCategory,
        forge: Optional[Forge] = None,
        rounds: int = 5
    ) -> BenchmarkResult:
        """Run a single category benchmark"""
        print(f"\n  Running {category.value} benchmark...")

        # Initialize forge if not provided
        if forge is None:
            forge = Forge()
            await forge.ignite()

        # Get benchmark tasks for this category
        tasks = self.BENCHMARK_TASKS.get(category, [])
        if not tasks:
            raise ValueError(f"No benchmark tasks defined for {category.value}")

        start_time = time.time()
        task_scores = []

        for task in tasks:
            result = await forge.run_tournament(task, rounds=rounds)
            task_scores.append(result.metrics["peak_score"])

        forge_score = sum(task_scores) / len(task_scores)
        duration = time.time() - start_time

        # Compare against baselines
        baselines = INDUSTRY_BASELINES.get(category, {})
        baseline_scores = {}
        improvements = {}

        for source, baseline in baselines.items():
            baseline_avg = sum(baseline.metrics.values()) / len(baseline.metrics)
            baseline_scores[source] = baseline_avg

            if baseline_avg > 0:
                improvement = ((forge_score - baseline_avg) / baseline_avg) * 100
                improvements[source] = improvement

        benchmark_result = BenchmarkResult(
            benchmark_id=f"bench_{uuid4().hex[:8]}",
            benchmark_name=f"{category.value}_benchmark",
            category=category,
            task=tasks[0],  # Primary task
            forge_score=forge_score,
            baseline_scores=baseline_scores,
            improvement_vs_baseline=improvements,
            metrics={
                "tasks_run": len(tasks),
                "avg_score": forge_score,
                "min_score": min(task_scores),
                "max_score": max(task_scores),
                "rounds_per_task": rounds
            },
            duration_seconds=duration
        )

        self.results.append(benchmark_result)
        self._update_leaderboard(category, forge_score)

        return benchmark_result

    async def run_full_suite(
        self,
        forge: Optional[Forge] = None,
        categories: Optional[List[BenchmarkCategory]] = None
    ) -> Dict[str, Any]:
        """Run the full benchmark suite"""
        print("\n" + "═" * 60)
        print("  ARCHITECT FORGE - FULL BENCHMARK SUITE")
        print("═" * 60)

        if forge is None:
            forge = Forge()
            await forge.ignite()

        categories = categories or list(BenchmarkCategory)
        results = {}
        total_start = time.time()

        for category in categories:
            if category in self.BENCHMARK_TASKS:
                try:
                    result = await self.run_benchmark(category, forge)
                    results[category.value] = result.to_dict()
                except Exception as e:
                    print(f"    ⚠ {category.value} failed: {e}")
                    results[category.value] = {"error": str(e)}

        total_duration = time.time() - total_start

        # Calculate aggregate scores
        valid_results = [r for r in results.values() if "forge_score" in r]
        avg_forge_score = sum(r["forge_score"] for r in valid_results) / len(valid_results) if valid_results else 0

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_duration_seconds": total_duration,
            "categories_tested": len(results),
            "average_forge_score": avg_forge_score,
            "results": results,
            "vs_baselines": self._calculate_aggregate_improvements(valid_results)
        }

        # Save to history
        self.forge_history.append(summary)
        self._save_history()

        await forge.shutdown()
        return summary

    def _calculate_aggregate_improvements(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate aggregate improvements across all categories"""
        improvements_by_source: Dict[str, List[float]] = {}

        for result in results:
            for source, improvement in result.get("improvement_vs_baseline", {}).items():
                if source not in improvements_by_source:
                    improvements_by_source[source] = []
                improvements_by_source[source].append(improvement)

        return {
            source: sum(imps) / len(imps)
            for source, imps in improvements_by_source.items()
            if imps
        }

    def _update_leaderboard(self, category: BenchmarkCategory, score: float) -> None:
        """Update the leaderboard with new score"""
        if category not in self.leaderboard:
            self.leaderboard[category] = []

        # Add Forge entry
        entry = LeaderboardEntry(
            rank=0,  # Will be calculated
            name="Architect Forge",
            source="forge",
            score=score,
            category=category,
            timestamp=datetime.utcnow()
        )

        # Add baseline entries
        baselines = INDUSTRY_BASELINES.get(category, {})
        all_entries = [entry]

        for source, baseline in baselines.items():
            baseline_score = sum(baseline.metrics.values()) / len(baseline.metrics)
            all_entries.append(LeaderboardEntry(
                rank=0,
                name=baseline.name,
                source=source,
                score=baseline_score,
                category=category,
                timestamp=baseline.date_recorded
            ))

        # Sort and assign ranks
        all_entries.sort(key=lambda x: x.score, reverse=True)
        for i, e in enumerate(all_entries):
            e.rank = i + 1

        self.leaderboard[category] = all_entries

    def get_leaderboard(
        self,
        category: Optional[BenchmarkCategory] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get leaderboard standings"""
        if category:
            entries = self.leaderboard.get(category, [])
            return {category.value: [
                {
                    "rank": e.rank,
                    "name": e.name,
                    "source": e.source,
                    "score": e.score
                }
                for e in entries
            ]}

        return {
            cat.value: [
                {
                    "rank": e.rank,
                    "name": e.name,
                    "source": e.source,
                    "score": e.score
                }
                for e in entries
            ]
            for cat, entries in self.leaderboard.items()
        }

    def print_leaderboard(self, category: Optional[BenchmarkCategory] = None) -> None:
        """Print formatted leaderboard"""
        print("\n" + "═" * 60)
        print("  LEADERBOARD")
        print("═" * 60)

        categories = [category] if category else list(self.leaderboard.keys())

        for cat in categories:
            entries = self.leaderboard.get(cat, [])
            if not entries:
                continue

            print(f"\n  {cat.value.upper()}")
            print("  " + "-" * 50)

            for entry in entries:
                marker = "🏆" if entry.rank == 1 else "  "
                forge_marker = "⚡" if entry.source == "forge" else "  "
                print(f"  {marker} #{entry.rank} {entry.name:<30} {entry.score:.2f} {forge_marker}")

    def generate_report(self) -> str:
        """Generate a comprehensive benchmark report"""
        report = []
        report.append("=" * 60)
        report.append("  ARCHITECT FORGE BENCHMARK REPORT")
        report.append("  " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
        report.append("=" * 60)

        if not self.results:
            report.append("\n  No benchmark results available.")
            return "\n".join(report)

        # Summary stats
        avg_score = sum(r.forge_score for r in self.results) / len(self.results)
        report.append(f"\n  SUMMARY")
        report.append(f"  -------")
        report.append(f"  Benchmarks Run: {len(self.results)}")
        report.append(f"  Average Forge Score: {avg_score:.2f}")

        # Category breakdown
        report.append(f"\n  CATEGORY RESULTS")
        report.append(f"  ----------------")

        for result in self.results:
            report.append(f"\n  {result.category.value.upper()}")
            report.append(f"    Forge Score: {result.forge_score:.2f}")
            report.append(f"    Duration: {result.duration_seconds:.1f}s")

            if result.improvement_vs_baseline:
                report.append(f"    vs Baselines:")
                for source, improvement in result.improvement_vs_baseline.items():
                    sign = "+" if improvement > 0 else ""
                    report.append(f"      {source}: {sign}{improvement:.1f}%")

        # Historical trend
        if len(self.forge_history) > 1:
            report.append(f"\n  HISTORICAL TREND")
            report.append(f"  ----------------")
            for i, entry in enumerate(self.forge_history[-5:]):
                report.append(f"    Run {i+1}: {entry.get('average_forge_score', 0):.2f}")

        report.append("\n" + "=" * 60)
        return "\n".join(report)


async def run_quick_benchmark():
    """Run a quick benchmark for testing"""
    suite = BenchmarkSuite()

    # Run just code generation benchmark
    forge = Forge(ForgeConfig(population_size=8, tournament_rounds=3))
    await forge.ignite()

    result = await suite.run_benchmark(BenchmarkCategory.CODE_GENERATION, forge, rounds=3)

    print(f"\n  Quick Benchmark Result:")
    print(f"    Forge Score: {result.forge_score:.2f}")
    print(f"    vs GPT-4: {result.improvement_vs_baseline.get('gpt4', 0):+.1f}%")
    print(f"    vs Claude: {result.improvement_vs_baseline.get('claude', 0):+.1f}%")
    print(f"    vs Human: {result.improvement_vs_baseline.get('human_expert', 0):+.1f}%")

    suite.print_leaderboard(BenchmarkCategory.CODE_GENERATION)

    await forge.shutdown()
    return result


async def main():
    """Run full benchmark suite"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║           ARCHITECT FORGE BENCHMARK SUITE                 ║")
    print("║              Proving the Impossible                       ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    suite = BenchmarkSuite()

    # Run full suite
    summary = await suite.run_full_suite(
        categories=[
            BenchmarkCategory.CODE_GENERATION,
            BenchmarkCategory.STRATEGY,
            BenchmarkCategory.ANALYSIS,
            BenchmarkCategory.CREATIVE,
            BenchmarkCategory.META_LEARNING,
        ]
    )

    # Print results
    print("\n" + suite.generate_report())
    suite.print_leaderboard()

    print(f"\n  Average Forge Score: {summary['average_forge_score']:.2f}")
    print(f"\n  vs Industry Baselines:")
    for source, improvement in summary.get('vs_baselines', {}).items():
        sign = "+" if improvement > 0 else ""
        print(f"    {source}: {sign}{improvement:.1f}%")

    print("\n  ⚡ Benchmark Complete ⚡\n")

    return summary


if __name__ == "__main__":
    asyncio.run(main())
