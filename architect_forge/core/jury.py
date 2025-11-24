"""
Jury: Multi-agent adversarial evaluation system

Diverse critics evaluate solutions from different perspectives.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import statistics


@dataclass
class Critique:
    """Individual critic's evaluation"""
    critic_name: str
    score: float  # 0.0 to 1.0
    reasoning: str
    concerns: List[str]
    strengths: List[str]


@dataclass
class JuryVerdict:
    """Aggregated evaluation from all critics"""
    final_score: float
    individual_scores: Dict[str, float]
    critiques: List[Critique]
    recommendation: str  # 'approve', 'conditional', 'reject'
    consensus_level: float  # How much critics agree


class Critic(ABC):
    """Base class for solution critics"""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

    @abstractmethod
    def evaluate(self, solution: Dict[str, Any], context: Dict[str, Any]) -> Critique:
        """Evaluate a solution and return critique"""
        pass


class SafetyCritic(Critic):
    """Evaluates safety and risk"""

    def __init__(self):
        super().__init__("Safety Critic", weight=1.5)

    def evaluate(self, solution: Dict[str, Any], context: Dict[str, Any]) -> Critique:
        approach = solution.get('approach', {})
        profile = approach.get('approach_profile', {})
        risk = profile.get('risk_tolerance', 0.5)

        # Lower risk tolerance = better safety score
        safety_score = 1.0 - risk

        # Check for safety violations in context
        violations = context.get('safety_violations', [])
        if violations:
            safety_score *= 0.5  # Penalize violations

        concerns = []
        strengths = []

        if risk > 0.7:
            concerns.append("High risk tolerance may lead to unsafe solutions")
        if violations:
            concerns.append(f"{len(violations)} safety violations detected")

        if risk < 0.3:
            strengths.append("Conservative approach prioritizes safety")
        if not violations:
            strengths.append("No safety violations detected")

        reasoning = f"Safety score based on risk tolerance ({risk:.2f}) and violations ({len(violations)})"

        return Critique(
            critic_name=self.name,
            score=safety_score,
            reasoning=reasoning,
            concerns=concerns,
            strengths=strengths,
        )


class EfficiencyCritic(Critic):
    """Evaluates resource usage and optimization"""

    def __init__(self):
        super().__init__("Efficiency Critic", weight=1.0)

    def evaluate(self, solution: Dict[str, Any], context: Dict[str, Any]) -> Critique:
        approach = solution.get('approach', {})
        profile = approach.get('approach_profile', {})
        optimization = profile.get('optimization_focus', 0.5)

        # Resource usage from sandbox
        resources = context.get('resource_usage', {})
        cpu_time = resources.get('cpu_time', 0.0)
        memory = resources.get('memory_peak', 0)

        # Base score from optimization focus
        efficiency_score = optimization

        # Penalize high resource usage
        if cpu_time > 1.0:
            efficiency_score *= 0.9
        if memory > 100 * 1024 * 1024:  # > 100MB
            efficiency_score *= 0.9

        concerns = []
        strengths = []

        if optimization < 0.5:
            concerns.append("Low optimization focus may waste resources")
        if cpu_time > 1.0:
            concerns.append(f"High CPU time: {cpu_time:.2f}s")

        if optimization > 0.7:
            strengths.append("Strong focus on optimization")
        if cpu_time < 0.5:
            strengths.append("Efficient execution time")

        reasoning = f"Efficiency based on optimization focus ({optimization:.2f}) and resource usage"

        return Critique(
            critic_name=self.name,
            score=efficiency_score,
            reasoning=reasoning,
            concerns=concerns,
            strengths=strengths,
        )


class NoveltyJudge(Critic):
    """Evaluates originality and innovation"""

    def __init__(self):
        super().__init__("Novelty Judge", weight=0.8)

    def evaluate(self, solution: Dict[str, Any], context: Dict[str, Any]) -> Critique:
        approach = solution.get('approach', {})
        profile = approach.get('approach_profile', {})
        creativity = profile.get('creativity', 0.5)
        novelty = solution.get('novelty_score', creativity)

        metrics = context.get('metrics', {})
        novelty_metric = metrics.get('novelty', novelty)

        # Novelty score
        novelty_score = (novelty + novelty_metric) / 2

        concerns = []
        strengths = []

        if novelty_score < 0.4:
            concerns.append("Solution may be too conventional")
        if creativity < 0.3:
            concerns.append("Low creativity may miss innovative approaches")

        if novelty_score > 0.7:
            strengths.append("Highly innovative approach")
        if creativity > 0.7:
            strengths.append("Strong creative exploration")

        reasoning = f"Novelty based on creativity ({creativity:.2f}) and solution innovation"

        return Critique(
            critic_name=self.name,
            score=novelty_score,
            reasoning=reasoning,
            concerns=concerns,
            strengths=strengths,
        )


class RobustnessValidator(Critic):
    """Tests edge cases and failure modes"""

    def __init__(self):
        super().__init__("Robustness Validator", weight=1.2)

    def evaluate(self, solution: Dict[str, Any], context: Dict[str, Any]) -> Critique:
        approach = solution.get('approach', {})
        profile = approach.get('approach_profile', {})
        risk = profile.get('risk_tolerance', 0.5)
        quality_focus = 1.0 - profile.get('speed_vs_quality', 0.5)

        # Robustness inversely related to risk
        robustness_base = 1.0 - risk

        # Quality focus contributes to robustness
        robustness_score = (robustness_base * 0.6) + (quality_focus * 0.4)

        # Check metrics
        metrics = context.get('metrics', {})
        if 'robustness_score' in metrics:
            robustness_score = (robustness_score + metrics['robustness_score']) / 2

        concerns = []
        strengths = []

        if risk > 0.6:
            concerns.append("High risk may compromise robustness")
        if profile.get('speed_vs_quality', 0.5) > 0.7:
            concerns.append("Speed prioritization may skip edge case handling")

        if robustness_score > 0.7:
            strengths.append("Solution likely handles edge cases well")
        if quality_focus > 0.6:
            strengths.append("Quality-focused approach enhances robustness")

        reasoning = f"Robustness based on risk level ({risk:.2f}) and quality focus"

        return Critique(
            critic_name=self.name,
            score=robustness_score,
            reasoning=reasoning,
            concerns=concerns,
            strengths=strengths,
        )


class EthicsReviewer(Critic):
    """Evaluates ethical implications"""

    def __init__(self):
        super().__init__("Ethics Reviewer", weight=1.3)

    def evaluate(self, solution: Dict[str, Any], context: Dict[str, Any]) -> Critique:
        approach = solution.get('approach', {})
        profile = approach.get('approach_profile', {})

        # Ethics score based on safety and consideration
        risk = profile.get('risk_tolerance', 0.5)
        ethics_score = 1.0 - (risk * 0.5)  # Lower risk generally more ethical

        # Check for safety violations (ethical red flags)
        violations = context.get('safety_violations', [])
        critical_violations = [v for v in violations if v.get('severity') == 'critical']

        if critical_violations:
            ethics_score *= 0.3
        elif violations:
            ethics_score *= 0.7

        concerns = []
        strengths = []

        if critical_violations:
            concerns.append(f"{len(critical_violations)} critical ethical concerns")
        if risk > 0.8:
            concerns.append("Very high risk tolerance raises ethical questions")

        if not violations:
            strengths.append("No ethical violations detected")
        if risk < 0.3:
            strengths.append("Conservative approach aligns with ethical safety")

        reasoning = f"Ethics evaluated based on risk ({risk:.2f}) and violations ({len(violations)})"

        return Critique(
            critic_name=self.name,
            score=ethics_score,
            reasoning=reasoning,
            concerns=concerns,
            strengths=strengths,
        )


class VotingAggregator:
    """Aggregates critic scores into final verdict"""

    def combine(self, critiques: List[Critique]) -> float:
        """Combine weighted critic scores"""
        if not critiques:
            return 0.0

        total_weight = sum(c.score for c in critiques)
        weighted_sum = sum(c.score for c in critiques)

        return weighted_sum / len(critiques) if critiques else 0.0

    def calculate_consensus(self, scores: List[float]) -> float:
        """Calculate how much critics agree (0.0 to 1.0)"""
        if len(scores) < 2:
            return 1.0

        std_dev = statistics.stdev(scores)
        # Low std dev = high consensus
        # Normalize: std dev of 0.5 = 0% consensus, 0.0 = 100% consensus
        consensus = max(0.0, 1.0 - (std_dev * 2))

        return consensus


class Jury:
    """
    Multi-agent adversarial evaluation system

    Diverse critics evaluate solutions, aggregate to verdict.
    """

    def __init__(self):
        self.critics: List[Critic] = [
            SafetyCritic(),
            EfficiencyCritic(),
            NoveltyJudge(),
            RobustnessValidator(),
            EthicsReviewer(),
        ]
        self.aggregator = VotingAggregator()

    def evaluate_solution(
        self,
        solution: Dict[str, Any],
        context: Dict[str, Any]
    ) -> JuryVerdict:
        """
        Evaluate solution with all critics

        Args:
            solution: Solution from architect
            context: Sandbox results and metrics

        Returns:
            JuryVerdict with aggregated scores and recommendation
        """
        critiques = []

        # Each critic evaluates
        for critic in self.critics:
            critique = critic.evaluate(solution, context)
            critiques.append(critique)

        # Extract scores
        scores = {c.critic_name: c.score for c in critiques}
        score_values = list(scores.values())

        # Aggregate
        final_score = self.aggregator.combine(critiques)
        consensus = self.aggregator.calculate_consensus(score_values)

        # Make recommendation
        recommendation = self._make_recommendation(final_score, consensus, critiques)

        return JuryVerdict(
            final_score=final_score,
            individual_scores=scores,
            critiques=critiques,
            recommendation=recommendation,
            consensus_level=consensus,
        )

    def _make_recommendation(
        self,
        final_score: float,
        consensus: float,
        critiques: List[Critique]
    ) -> str:
        """Determine recommendation based on scores and consensus"""

        # Count critical concerns
        all_concerns = []
        for c in critiques:
            all_concerns.extend(c.concerns)

        critical_concerns = len([c for c in all_concerns if 'critical' in c.lower()])

        # Decision logic
        if critical_concerns > 0:
            return 'reject'

        if final_score >= 0.7 and consensus >= 0.6:
            return 'approve'

        if final_score >= 0.5:
            return 'conditional'

        return 'reject'

    def add_critic(self, critic: Critic) -> None:
        """Add custom critic to jury"""
        self.critics.append(critic)

    def remove_critic(self, critic_name: str) -> None:
        """Remove critic by name"""
        self.critics = [c for c in self.critics if c.name != critic_name]
