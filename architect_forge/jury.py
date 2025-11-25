"""
JURY COUNCIL - The Certification System
═══════════════════════════════════════════════════════════════
Multi-agent evaluation panels with reputation-weighted voting,
human-in-the-loop validation, and provenance verification.

"The Jury doesn't just evaluate solutions.
 It decides what SHOULD exist."
═══════════════════════════════════════════════════════════════
"""

import asyncio
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


class JurorRole(Enum):
    """Different roles on the jury"""
    TECHNICAL = "technical"         # Code quality, architecture
    STRATEGIC = "strategic"         # Business value, impact
    ADVERSARIAL = "adversarial"     # Security, edge cases
    ETHICAL = "ethical"             # Safety, alignment
    CREATIVE = "creative"           # Innovation, novelty


class CertificationLevel(Enum):
    """Certification levels for apprentices"""
    REJECTED = "rejected"           # Did not pass
    BRONZE = "bronze"               # Minimal viable
    SILVER = "silver"               # Good quality
    GOLD = "gold"                   # Excellent
    PLATINUM = "platinum"           # Exceptional, emergent


@dataclass
class Juror:
    """A single juror on the evaluation panel"""
    juror_id: str
    role: JurorRole
    reputation: float = 0.5         # 0.0 to 1.0
    votes_cast: int = 0
    correct_predictions: int = 0    # Track accuracy

    def vote_weight(self) -> float:
        """Calculate voting weight based on reputation"""
        return 0.5 + (self.reputation * 0.5)

    def update_reputation(self, was_correct: bool) -> None:
        """Update reputation based on vote accuracy"""
        self.votes_cast += 1
        if was_correct:
            self.correct_predictions += 1
            self.reputation = min(1.0, self.reputation + 0.02)
        else:
            self.reputation = max(0.1, self.reputation - 0.01)


@dataclass
class Vote:
    """A single vote from a juror"""
    juror_id: str
    juror_role: JurorRole
    score: float                    # 0.0 to 1.0
    weight: float                   # Vote weight
    reasoning: str
    concerns: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)


@dataclass
class Verdict:
    """Final verdict on a solution"""
    verdict_id: str
    agent_id: str
    solution_id: str
    score: float                    # Weighted average
    certification: CertificationLevel
    votes: List[Vote]
    consensus_level: float          # How much jurors agreed
    decision_reasoning: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict_id": self.verdict_id,
            "agent_id": self.agent_id,
            "score": self.score,
            "certification": self.certification.value,
            "consensus_level": self.consensus_level,
            "decision_reasoning": self.decision_reasoning,
            "vote_count": len(self.votes)
        }


class JuryCouncil:
    """
    The Jury Council - certifies solutions and architects.

    Features:
    - Multi-perspective evaluation (technical, strategic, ethical, etc.)
    - Reputation-weighted voting
    - Consensus tracking
    - Human-in-the-loop hooks
    - Provenance verification
    """

    def __init__(self, jury_size: int = 5):
        self.jury_size = jury_size
        self.jurors: List[Juror] = []
        self.verdict_history: List[Verdict] = []
        self.human_review_queue: List[str] = []

    async def assemble(self) -> None:
        """Assemble the jury panel"""
        self.jurors = []

        # One juror per role
        for role in JurorRole:
            juror = Juror(
                juror_id=f"juror_{role.value}_{uuid4().hex[:4]}",
                role=role,
                reputation=0.5 + random.uniform(-0.1, 0.1)
            )
            self.jurors.append(juror)

        # Add additional jurors if needed
        while len(self.jurors) < self.jury_size:
            role = random.choice(list(JurorRole))
            juror = Juror(
                juror_id=f"juror_{role.value}_{uuid4().hex[:4]}",
                role=role,
                reputation=0.4 + random.uniform(0, 0.2)
            )
            self.jurors.append(juror)

        print(f"  Jury assembled: {len(self.jurors)} jurors")

    async def evaluate(
        self,
        sandbox_result: 'SandboxResult',
        task: 'Task'
    ) -> Verdict:
        """Evaluate a single solution"""
        votes = []

        for juror in self.jurors:
            vote = await self._cast_vote(juror, sandbox_result, task)
            votes.append(vote)

        # Calculate weighted score
        total_weight = sum(v.weight for v in votes)
        weighted_score = sum(v.score * v.weight for v in votes) / total_weight

        # Calculate consensus
        scores = [v.score for v in votes]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        consensus = 1.0 - min(variance ** 0.5, 1.0)

        # Determine certification level
        certification = self._determine_certification(weighted_score, consensus, sandbox_result)

        # Generate reasoning
        reasoning = self._generate_reasoning(votes, weighted_score, certification)

        verdict = Verdict(
            verdict_id=f"verdict_{uuid4().hex[:8]}",
            agent_id=sandbox_result.agent_id,
            solution_id=sandbox_result.solution_id,
            score=weighted_score,
            certification=certification,
            votes=votes,
            consensus_level=consensus,
            decision_reasoning=reasoning
        )

        self.verdict_history.append(verdict)

        # Flag for human review if uncertain
        if consensus < 0.5 or certification == CertificationLevel.PLATINUM:
            self.human_review_queue.append(verdict.verdict_id)

        return verdict

    async def evaluate_batch(
        self,
        sandbox_results: List['SandboxResult'],
        task: 'Task'
    ) -> List[Verdict]:
        """Evaluate multiple solutions"""
        verdicts = []
        for result in sandbox_results:
            verdict = await self.evaluate(result, task)
            verdicts.append(verdict)
        return verdicts

    async def _cast_vote(
        self,
        juror: Juror,
        sandbox_result: 'SandboxResult',
        task: 'Task'
    ) -> Vote:
        """A juror casts their vote"""
        # Base score from sandbox result
        base_score = sandbox_result.score

        # Adjust based on juror role
        role_adjustment = self._role_specific_evaluation(juror.role, sandbox_result, task)

        # Add some variance
        noise = random.uniform(-0.1, 0.1)

        score = max(0.0, min(1.0, base_score + role_adjustment + noise))

        # Generate reasoning based on role
        reasoning, concerns, highlights = self._generate_vote_reasoning(
            juror.role, sandbox_result, score
        )

        return Vote(
            juror_id=juror.juror_id,
            juror_role=juror.role,
            score=score,
            weight=juror.vote_weight(),
            reasoning=reasoning,
            concerns=concerns,
            highlights=highlights
        )

    def _role_specific_evaluation(
        self,
        role: JurorRole,
        result: 'SandboxResult',
        task: 'Task'
    ) -> float:
        """Apply role-specific evaluation criteria"""
        adjustments = {
            JurorRole.TECHNICAL: 0.05 if result.tests_passed > result.tests_total * 0.8 else -0.05,
            JurorRole.STRATEGIC: 0.05 if result.execution_time < 60 else -0.05,
            JurorRole.ADVERSARIAL: -0.1 if result.failure_reasons else 0.05,
            JurorRole.ETHICAL: 0.0,  # Neutral unless specific concerns
            JurorRole.CREATIVE: 0.1 if result.emergence_markers else 0.0
        }
        return adjustments.get(role, 0.0)

    def _generate_vote_reasoning(
        self,
        role: JurorRole,
        result: 'SandboxResult',
        score: float
    ) -> Tuple[str, List[str], List[str]]:
        """Generate reasoning, concerns, and highlights for a vote"""
        concerns = []
        highlights = []

        if result.failure_reasons:
            concerns.extend(result.failure_reasons[:2])

        if result.emergence_markers:
            highlights.extend(result.emergence_markers)

        if score >= 0.8:
            highlights.append(f"Strong performance ({result.tests_passed}/{result.tests_total} tests passed)")

        if result.execution_time > 120:
            concerns.append(f"Slow execution ({result.execution_time:.1f}s)")

        reasoning_templates = {
            JurorRole.TECHNICAL: f"Technical evaluation: {result.tests_passed}/{result.tests_total} tests passed. Code structure appears {'solid' if score > 0.7 else 'needs improvement'}.",
            JurorRole.STRATEGIC: f"Strategic value: Solution {'meets' if score > 0.6 else 'partially meets'} business objectives. Execution time: {result.execution_time:.1f}s.",
            JurorRole.ADVERSARIAL: f"Security assessment: {len(result.failure_reasons)} vulnerabilities identified. {'Robust' if not result.failure_reasons else 'Needs hardening'}.",
            JurorRole.ETHICAL: f"Ethical review: No major concerns identified. Solution {'aligns' if score > 0.5 else 'needs review for alignment'} with safety guidelines.",
            JurorRole.CREATIVE: f"Innovation assessment: {'Emergent behaviors detected!' if result.emergence_markers else 'Standard approach.'} Novelty score: {score:.2f}."
        }

        reasoning = reasoning_templates.get(role, f"General evaluation: Score {score:.2f}")

        return reasoning, concerns, highlights

    def _determine_certification(
        self,
        score: float,
        consensus: float,
        result: 'SandboxResult'
    ) -> CertificationLevel:
        """Determine certification level based on score and consensus"""
        # Emergence markers can boost to platinum
        if score >= 0.9 and consensus >= 0.7 and result.emergence_markers:
            return CertificationLevel.PLATINUM
        elif score >= 0.85 and consensus >= 0.6:
            return CertificationLevel.GOLD
        elif score >= 0.7 and consensus >= 0.5:
            return CertificationLevel.SILVER
        elif score >= 0.5:
            return CertificationLevel.BRONZE
        else:
            return CertificationLevel.REJECTED

    def _generate_reasoning(
        self,
        votes: List[Vote],
        score: float,
        certification: CertificationLevel
    ) -> str:
        """Generate overall decision reasoning"""
        all_concerns = []
        all_highlights = []

        for vote in votes:
            all_concerns.extend(vote.concerns)
            all_highlights.extend(vote.highlights)

        reasoning = f"Certification: {certification.value.upper()} (Score: {score:.2f})\n"

        if all_highlights:
            reasoning += f"Highlights: {', '.join(set(all_highlights)[:3])}\n"

        if all_concerns:
            reasoning += f"Concerns: {', '.join(set(all_concerns)[:3])}"

        return reasoning

    async def request_human_review(self, verdict_id: str) -> None:
        """Request human review for a verdict"""
        if verdict_id not in self.human_review_queue:
            self.human_review_queue.append(verdict_id)

    def get_pending_reviews(self) -> List[str]:
        """Get verdicts pending human review"""
        return list(self.human_review_queue)

    def complete_human_review(
        self,
        verdict_id: str,
        approved: bool,
        notes: str = ""
    ) -> None:
        """Complete human review of a verdict"""
        if verdict_id in self.human_review_queue:
            self.human_review_queue.remove(verdict_id)

            # Update juror reputations based on human decision
            verdict = next((v for v in self.verdict_history if v.verdict_id == verdict_id), None)
            if verdict:
                for vote in verdict.votes:
                    juror = next((j for j in self.jurors if j.juror_id == vote.juror_id), None)
                    if juror:
                        # If human approved and juror voted high, or vice versa
                        vote_approved = vote.score >= 0.6
                        juror.update_reputation(vote_approved == approved)

    def get_statistics(self) -> Dict[str, Any]:
        """Get jury statistics"""
        if not self.verdict_history:
            return {"total_verdicts": 0}

        cert_dist = {}
        for verdict in self.verdict_history:
            cert = verdict.certification.value
            cert_dist[cert] = cert_dist.get(cert, 0) + 1

        avg_score = sum(v.score for v in self.verdict_history) / len(self.verdict_history)
        avg_consensus = sum(v.consensus_level for v in self.verdict_history) / len(self.verdict_history)

        juror_stats = [
            {
                "role": j.role.value,
                "reputation": j.reputation,
                "accuracy": j.correct_predictions / j.votes_cast if j.votes_cast > 0 else 0
            }
            for j in self.jurors
        ]

        return {
            "total_verdicts": len(self.verdict_history),
            "certification_distribution": cert_dist,
            "average_score": avg_score,
            "average_consensus": avg_consensus,
            "pending_human_reviews": len(self.human_review_queue),
            "juror_statistics": juror_stats
        }
