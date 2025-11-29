#!/usr/bin/env python3
"""
REPUTATION SYSTEM
Trust and reputation management for the marketplace.
"""
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ReputationFactor(Enum):
    """Factors that affect reputation"""
    JOB_SUCCESS = "job_success"
    JOB_FAILURE = "job_failure"
    DISPUTE_LOST = "dispute_lost"
    DISPUTE_WON = "dispute_won"
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    RATING = "rating"
    STAKE_SIZE = "stake_size"
    TIME_IN_NETWORK = "time_in_network"


@dataclass
class ReputationEvent:
    """A reputation-affecting event"""
    id: str
    entity_id: str
    factor: ReputationFactor
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReputationScore:
    """Calculated reputation score"""
    entity_id: str
    overall: float  # 0-100
    components: Dict[str, float]
    tier: str  # bronze, silver, gold, platinum, diamond
    badges: List[str]
    calculated_at: datetime = field(default_factory=datetime.now)


class ReputationEngine:
    """
    Reputation calculation and management.

    Reputation is calculated from multiple weighted factors:
    - Job success rate (30%)
    - User ratings (25%)
    - Uptime reliability (20%)
    - Dispute history (15%)
    - Stake commitment (10%)
    """

    # Weights for reputation factors
    WEIGHTS = {
        "success_rate": 0.30,
        "ratings": 0.25,
        "uptime": 0.20,
        "disputes": 0.15,
        "stake": 0.10,
    }

    # Reputation tiers
    TIERS = [
        (90, "diamond", "💎"),
        (75, "platinum", "⭐"),
        (60, "gold", "🥇"),
        (40, "silver", "🥈"),
        (0, "bronze", "🥉"),
    ]

    # Badge definitions
    BADGES = {
        "first_job": {"name": "First Steps", "desc": "Completed first job"},
        "hundred_jobs": {"name": "Centurion", "desc": "100 successful jobs"},
        "thousand_jobs": {"name": "Veteran", "desc": "1000 successful jobs"},
        "perfect_uptime": {"name": "Always On", "desc": "99.9%+ uptime for 30 days"},
        "top_rated": {"name": "Top Rated", "desc": "4.9+ average rating"},
        "big_staker": {"name": "Committed", "desc": "10x minimum stake"},
        "early_adopter": {"name": "Pioneer", "desc": "Joined in first month"},
        "no_disputes": {"name": "Trusted", "desc": "0 lost disputes in 100+ jobs"},
    }

    def __init__(self):
        self._events: Dict[str, List[ReputationEvent]] = {}
        self._scores: Dict[str, ReputationScore] = {}
        self._event_counter = 0

    def record_event(
        self,
        entity_id: str,
        factor: ReputationFactor,
        value: float,
        metadata: Dict[str, Any] = None
    ) -> ReputationEvent:
        """Record a reputation-affecting event"""
        self._event_counter += 1
        event = ReputationEvent(
            id=f"rep_{self._event_counter:08d}",
            entity_id=entity_id,
            factor=factor,
            value=value,
            metadata=metadata or {},
        )

        if entity_id not in self._events:
            self._events[entity_id] = []
        self._events[entity_id].append(event)

        # Invalidate cached score
        if entity_id in self._scores:
            del self._scores[entity_id]

        return event

    def calculate_score(
        self,
        entity_id: str,
        force_recalculate: bool = False
    ) -> ReputationScore:
        """Calculate reputation score for an entity"""
        # Check cache
        if not force_recalculate and entity_id in self._scores:
            cached = self._scores[entity_id]
            # Use cache if less than 1 hour old
            if (datetime.now() - cached.calculated_at).seconds < 3600:
                return cached

        events = self._events.get(entity_id, [])

        # Calculate components
        components = {
            "success_rate": self._calc_success_rate(events),
            "ratings": self._calc_ratings(events),
            "uptime": self._calc_uptime(events),
            "disputes": self._calc_disputes(events),
            "stake": self._calc_stake(events),
        }

        # Weighted overall score
        overall = sum(
            components[k] * self.WEIGHTS[k]
            for k in self.WEIGHTS
        )

        # Determine tier
        tier = "bronze"
        for threshold, tier_name, _ in self.TIERS:
            if overall >= threshold:
                tier = tier_name
                break

        # Check badges
        badges = self._check_badges(entity_id, events, components)

        score = ReputationScore(
            entity_id=entity_id,
            overall=overall,
            components=components,
            tier=tier,
            badges=badges,
        )

        self._scores[entity_id] = score
        return score

    def _calc_success_rate(self, events: List[ReputationEvent]) -> float:
        """Calculate success rate component (0-100)"""
        successes = sum(
            1 for e in events
            if e.factor == ReputationFactor.JOB_SUCCESS
        )
        failures = sum(
            1 for e in events
            if e.factor == ReputationFactor.JOB_FAILURE
        )

        total = successes + failures
        if total == 0:
            return 50  # Neutral for new entities

        rate = successes / total
        return rate * 100

    def _calc_ratings(self, events: List[ReputationEvent]) -> float:
        """Calculate ratings component (0-100)"""
        ratings = [
            e.value for e in events
            if e.factor == ReputationFactor.RATING
        ]

        if not ratings:
            return 50  # Neutral for unrated

        # Use recent ratings more heavily
        recent_ratings = sorted(
            [(e.timestamp, e.value) for e in events if e.factor == ReputationFactor.RATING],
            key=lambda x: x[0],
            reverse=True
        )[:50]  # Last 50 ratings

        if not recent_ratings:
            avg = sum(ratings) / len(ratings)
        else:
            # Time-weighted average
            weights = [0.95 ** i for i in range(len(recent_ratings))]
            weighted_sum = sum(r * w for (_, r), w in zip(recent_ratings, weights))
            avg = weighted_sum / sum(weights)

        # Convert 5-star to 0-100
        return (avg / 5) * 100

    def _calc_uptime(self, events: List[ReputationEvent]) -> float:
        """Calculate uptime component (0-100)"""
        uptime_events = [
            e.value for e in events
            if e.factor == ReputationFactor.UPTIME
        ]

        if not uptime_events:
            return 50  # Neutral

        # Average uptime percentage
        avg_uptime = sum(uptime_events) / len(uptime_events)
        return avg_uptime * 100

    def _calc_disputes(self, events: List[ReputationEvent]) -> float:
        """Calculate disputes component (0-100)"""
        won = sum(
            1 for e in events
            if e.factor == ReputationFactor.DISPUTE_WON
        )
        lost = sum(
            1 for e in events
            if e.factor == ReputationFactor.DISPUTE_LOST
        )

        if won + lost == 0:
            return 75  # Slightly above neutral for no disputes

        # Penalize lost disputes heavily
        score = 100 - (lost * 20) + (won * 5)
        return max(0, min(100, score))

    def _calc_stake(self, events: List[ReputationEvent]) -> float:
        """Calculate stake component (0-100)"""
        stake_events = [
            e.value for e in events
            if e.factor == ReputationFactor.STAKE_SIZE
        ]

        if not stake_events:
            return 0

        # Most recent stake
        latest_stake = stake_events[-1]

        # Logarithmic scale - 10x minimum stake = full score
        # Assuming minimum stake is ~100
        min_stake = 100
        max_score_stake = min_stake * 10

        if latest_stake <= min_stake:
            return 20
        elif latest_stake >= max_score_stake:
            return 100
        else:
            # Logarithmic interpolation
            log_range = math.log(max_score_stake / min_stake)
            log_position = math.log(latest_stake / min_stake)
            return 20 + 80 * (log_position / log_range)

    def _check_badges(
        self,
        entity_id: str,
        events: List[ReputationEvent],
        components: Dict[str, float]
    ) -> List[str]:
        """Check which badges an entity has earned"""
        badges = []

        successes = sum(
            1 for e in events
            if e.factor == ReputationFactor.JOB_SUCCESS
        )

        failures = sum(
            1 for e in events
            if e.factor == ReputationFactor.JOB_FAILURE
        )

        disputes_lost = sum(
            1 for e in events
            if e.factor == ReputationFactor.DISPUTE_LOST
        )

        # First job
        if successes >= 1:
            badges.append("first_job")

        # Job milestones
        if successes >= 100:
            badges.append("hundred_jobs")
        if successes >= 1000:
            badges.append("thousand_jobs")

        # Perfect uptime
        if components["uptime"] >= 99.9:
            badges.append("perfect_uptime")

        # Top rated
        if components["ratings"] >= 98:
            badges.append("top_rated")

        # Big staker
        if components["stake"] >= 100:
            badges.append("big_staker")

        # No disputes with significant history
        if disputes_lost == 0 and successes >= 100:
            badges.append("no_disputes")

        return badges

    def get_events(
        self,
        entity_id: str,
        limit: int = 100
    ) -> List[ReputationEvent]:
        """Get recent reputation events"""
        events = self._events.get(entity_id, [])
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]

    def compare(self, entity_ids: List[str]) -> List[ReputationScore]:
        """Compare reputation scores of multiple entities"""
        scores = [self.calculate_score(eid) for eid in entity_ids]
        return sorted(scores, key=lambda s: s.overall, reverse=True)

    def get_tier_icon(self, tier: str) -> str:
        """Get icon for a tier"""
        for _, tier_name, icon in self.TIERS:
            if tier_name == tier:
                return icon
        return "🥉"

    def get_badge_info(self, badge_id: str) -> Dict[str, str]:
        """Get badge information"""
        return self.BADGES.get(badge_id, {"name": badge_id, "desc": ""})

    def leaderboard(self, limit: int = 10) -> List[ReputationScore]:
        """Get top entities by reputation"""
        all_scores = [self.calculate_score(eid) for eid in self._events.keys()]
        return sorted(all_scores, key=lambda s: s.overall, reverse=True)[:limit]


# =============================================================================
# TRUST SCORING
# =============================================================================

class TrustScorer:
    """
    Calculate trust between two entities for a specific transaction.

    Trust is context-dependent and considers:
    - Both parties' reputations
    - Transaction size relative to history
    - Historical interactions between parties
    - Risk factors
    """

    def __init__(self, reputation_engine: ReputationEngine):
        self._reputation = reputation_engine
        self._interaction_history: Dict[str, Dict[str, List]] = {}

    def record_interaction(
        self,
        entity_a: str,
        entity_b: str,
        outcome: str,  # success, failure, dispute
        metadata: Dict[str, Any] = None
    ):
        """Record an interaction between two entities"""
        key = self._interaction_key(entity_a, entity_b)

        if key not in self._interaction_history:
            self._interaction_history[key] = []

        self._interaction_history[key].append({
            "timestamp": datetime.now(),
            "entity_a": entity_a,
            "entity_b": entity_b,
            "outcome": outcome,
            "metadata": metadata or {},
        })

    def _interaction_key(self, entity_a: str, entity_b: str) -> str:
        """Generate consistent key for entity pair"""
        return "-".join(sorted([entity_a, entity_b]))

    def calculate_trust(
        self,
        from_entity: str,
        to_entity: str,
        transaction_value: float = None
    ) -> Dict[str, Any]:
        """Calculate trust score from one entity to another"""
        # Get reputations
        from_rep = self._reputation.calculate_score(from_entity)
        to_rep = self._reputation.calculate_score(to_entity)

        # Get interaction history
        key = self._interaction_key(from_entity, to_entity)
        history = self._interaction_history.get(key, [])

        # Base trust from reputations
        base_trust = (from_rep.overall + to_rep.overall * 2) / 3  # Weight target more

        # History adjustment
        if history:
            successes = sum(1 for h in history if h["outcome"] == "success")
            failures = sum(1 for h in history if h["outcome"] in ["failure", "dispute"])
            history_factor = successes / (successes + failures) if (successes + failures) > 0 else 0.5
            base_trust = base_trust * 0.7 + history_factor * 100 * 0.3

        # Risk adjustment for transaction size
        risk_factor = 1.0
        if transaction_value:
            # Higher value = lower trust multiplier
            if transaction_value > 10000:
                risk_factor = 0.7
            elif transaction_value > 1000:
                risk_factor = 0.85
            elif transaction_value > 100:
                risk_factor = 0.95

        final_trust = base_trust * risk_factor

        # Determine recommendation
        if final_trust >= 80:
            recommendation = "highly_trusted"
        elif final_trust >= 60:
            recommendation = "trusted"
        elif final_trust >= 40:
            recommendation = "neutral"
        elif final_trust >= 20:
            recommendation = "caution"
        else:
            recommendation = "high_risk"

        return {
            "from": from_entity,
            "to": to_entity,
            "trust_score": final_trust,
            "recommendation": recommendation,
            "factors": {
                "from_reputation": from_rep.overall,
                "to_reputation": to_rep.overall,
                "interaction_history": len(history),
                "risk_factor": risk_factor,
            },
        }


# =============================================================================
# CLI DEMO
# =============================================================================

def demo():
    """Reputation system demo"""
    print("\n" + "=" * 50)
    print("REPUTATION SYSTEM DEMO")
    print("=" * 50)

    engine = ReputationEngine()

    # Simulate a provider's history
    provider = "provider_123"

    print(f"\n[1] Recording events for {provider}...")

    # Successful jobs
    for i in range(85):
        engine.record_event(provider, ReputationFactor.JOB_SUCCESS, 1.0)

    # Some failures
    for i in range(10):
        engine.record_event(provider, ReputationFactor.JOB_FAILURE, 1.0)

    # Good ratings
    for i in range(50):
        engine.record_event(provider, ReputationFactor.RATING, 4.5 + (i % 5) * 0.1)

    # Uptime
    engine.record_event(provider, ReputationFactor.UPTIME, 0.995)

    # Stake
    engine.record_event(provider, ReputationFactor.STAKE_SIZE, 500)

    print(f"    Recorded {len(engine._events[provider])} events")

    print("\n[2] Calculating reputation score...")
    score = engine.calculate_score(provider)

    print(f"\n    Overall: {score.overall:.1f}/100")
    print(f"    Tier: {score.tier} {engine.get_tier_icon(score.tier)}")
    print(f"\n    Components:")
    for comp, val in score.components.items():
        print(f"      {comp}: {val:.1f}")

    print(f"\n    Badges: {score.badges}")
    for badge in score.badges:
        info = engine.get_badge_info(badge)
        print(f"      - {info['name']}: {info['desc']}")

    # Trust calculation
    print("\n[3] Trust calculation...")
    trust_scorer = TrustScorer(engine)

    buyer = "buyer_456"
    # Give buyer some reputation
    for i in range(20):
        engine.record_event(buyer, ReputationFactor.JOB_SUCCESS, 1.0)
        engine.record_event(buyer, ReputationFactor.RATING, 4.8)

    trust = trust_scorer.calculate_trust(buyer, provider, transaction_value=500)
    print(f"    Trust from {buyer} to {provider}:")
    print(f"    Score: {trust['trust_score']:.1f}")
    print(f"    Recommendation: {trust['recommendation']}")

    print("\n" + "=" * 50)
    print("DEMO COMPLETE")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    demo()
