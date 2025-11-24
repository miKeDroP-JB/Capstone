"""
Ouroboros Ledger: Cryptographic provenance tracking

Immutable record of all changes, decisions, and ancestry.
"""

import time
import hashlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class EventType(Enum):
    """Types of events recorded in ledger"""
    ARCHITECT_CREATED = "architect_created"
    SOLUTION_GENERATED = "solution_generated"
    SOLUTION_TESTED = "solution_tested"
    SOLUTION_EVALUATED = "solution_evaluated"
    APPRENTICE_CREATED = "apprentice_created"
    APPRENTICE_DEPLOYED = "apprentice_deployed"
    POPULATION_EVOLVED = "population_evolved"
    FEEDBACK_RECEIVED = "feedback_received"


@dataclass
class Event:
    """Single ledger event"""
    event_id: str
    timestamp: float
    event_type: EventType
    data: Dict[str, Any]
    architect_id: str
    parent_hash: Optional[str] = None
    signature: Optional[str] = None
    hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        d = asdict(self)
        d['event_type'] = self.event_type.value
        return d


@dataclass
class ProvenanceChain:
    """Complete ancestry of an architect/apprentice"""
    entity_id: str
    events: List[Event]
    ancestors: List[str]
    descendants: List[str]
    reputation_score: float


class CryptoValidator:
    """Cryptographic validation utilities"""

    @staticmethod
    def hash_data(data: Dict[str, Any]) -> str:
        """Create SHA-256 hash of data"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    @staticmethod
    def sign_event(event: Dict[str, Any], private_key: Optional[str] = None) -> str:
        """
        Sign an event (simplified for v0.1)

        In production: use actual cryptographic signatures
        """
        # For v0.1, use hash as signature
        # In production, use proper signing with private key
        return CryptoValidator.hash_data(event)

    @staticmethod
    def verify_signature(event: Dict[str, Any], signature: str) -> bool:
        """Verify event signature"""
        expected = CryptoValidator.hash_data(event)
        return expected == signature


class OuroborosLedger:
    """
    Cryptographic provenance tracking system

    Records all events in an immutable chain with signatures.
    Enables full ancestry tracking and reputation scoring.
    """

    def __init__(self):
        self.chain: List[Event] = []
        self.validator = CryptoValidator()
        self.index_by_architect: Dict[str, List[Event]] = {}
        self.index_by_type: Dict[EventType, List[Event]] = {}

    def record_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        architect_id: str
    ) -> str:
        """
        Add signed event to ledger

        Args:
            event_type: Type of event
            data: Event data
            architect_id: ID of architect involved

        Returns:
            Event hash (event_id)
        """
        # Create event
        event_dict = {
            'timestamp': time.time(),
            'event_type': event_type.value,
            'data': data,
            'architect': architect_id,
            'parent_hash': self.chain[-1].hash if self.chain else None,
        }

        # Sign and hash
        signature = self.validator.sign_event(event_dict)
        event_dict['signature'] = signature

        event_id = self.validator.hash_data(event_dict)
        event_dict['event_id'] = event_id
        event_dict['hash'] = event_id

        # Create Event object
        event = Event(
            event_id=event_id,
            timestamp=event_dict['timestamp'],
            event_type=event_type,
            data=data,
            architect_id=architect_id,
            parent_hash=event_dict['parent_hash'],
            signature=signature,
            hash=event_id,
        )

        # Add to chain
        self.chain.append(event)

        # Update indices
        if architect_id not in self.index_by_architect:
            self.index_by_architect[architect_id] = []
        self.index_by_architect[architect_id].append(event)

        if event_type not in self.index_by_type:
            self.index_by_type[event_type] = []
        self.index_by_type[event_type].append(event)

        return event_id

    def get_events_by_architect(self, architect_id: str) -> List[Event]:
        """Get all events for an architect"""
        return self.index_by_architect.get(architect_id, [])

    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """Get all events of a type"""
        return self.index_by_type.get(event_type, [])

    def trace_lineage(self, entity_id: str) -> ProvenanceChain:
        """
        Trace complete ancestry of an architect/apprentice

        Args:
            entity_id: ID of entity to trace

        Returns:
            ProvenanceChain with full genealogy
        """
        events = self.get_events_by_architect(entity_id)

        if not events:
            return ProvenanceChain(
                entity_id=entity_id,
                events=[],
                ancestors=[],
                descendants=[],
                reputation_score=0.0,
            )

        # Find ancestors from creation event
        ancestors = []
        creation_events = [e for e in events if e.event_type == EventType.ARCHITECT_CREATED]

        if creation_events:
            parent_ids = creation_events[0].data.get('parent_ids', [])
            ancestors.extend(parent_ids)

            # Recursively find ancestors of ancestors
            for parent_id in parent_ids:
                parent_chain = self.trace_lineage(parent_id)
                ancestors.extend(parent_chain.ancestors)

        # Find descendants
        descendants = []
        all_creation_events = self.get_events_by_type(EventType.ARCHITECT_CREATED)

        for event in all_creation_events:
            parent_ids = event.data.get('parent_ids', [])
            if entity_id in parent_ids:
                descendants.append(event.architect_id)

        # Calculate reputation
        reputation = self._calculate_reputation(events)

        return ProvenanceChain(
            entity_id=entity_id,
            events=events,
            ancestors=list(set(ancestors)),
            descendants=list(set(descendants)),
            reputation_score=reputation,
        )

    def _calculate_reputation(self, events: List[Event]) -> float:
        """
        Calculate reputation score based on event history

        Args:
            events: Events for an architect

        Returns:
            Reputation score (0.0 to 1.0)
        """
        if not events:
            return 0.0

        # Factors:
        # - Number of successful solutions
        # - Quality scores from evaluations
        # - Deployment success rate
        # - Feedback scores

        success_count = 0
        total_attempts = 0
        quality_scores = []

        for event in events:
            if event.event_type == EventType.SOLUTION_EVALUATED:
                total_attempts += 1
                verdict = event.data.get('verdict', {})

                if verdict.get('recommendation') == 'approve':
                    success_count += 1

                final_score = verdict.get('final_score', 0.0)
                quality_scores.append(final_score)

        # Success rate
        success_rate = success_count / total_attempts if total_attempts > 0 else 0.0

        # Average quality
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        # Deployment bonus
        deployment_events = [e for e in events if e.event_type == EventType.APPRENTICE_DEPLOYED]
        deployment_bonus = min(0.2, len(deployment_events) * 0.05)

        # Combine
        reputation = (success_rate * 0.5) + (avg_quality * 0.4) + deployment_bonus

        return min(1.0, reputation)

    def get_reputation(self, architect_id: str) -> float:
        """Get reputation score for an architect"""
        chain = self.trace_lineage(architect_id)
        return chain.reputation_score

    def verify_chain_integrity(self) -> bool:
        """
        Verify integrity of the entire chain

        Returns:
            True if chain is valid, False otherwise
        """
        if not self.chain:
            return True

        for i, event in enumerate(self.chain):
            # Verify signature
            event_dict = {
                'timestamp': event.timestamp,
                'event_type': event.event_type.value,
                'data': event.data,
                'architect': event.architect_id,
                'parent_hash': event.parent_hash,
            }

            if not self.validator.verify_signature(event_dict, event.signature):
                return False

            # Verify hash chain
            if i > 0:
                if event.parent_hash != self.chain[i-1].hash:
                    return False

        return True

    def export_chain(self) -> List[Dict[str, Any]]:
        """Export entire chain as JSON-serializable list"""
        return [event.to_dict() for event in self.chain]

    def save(self, filepath: str) -> None:
        """Save ledger to file"""
        with open(filepath, 'w') as f:
            json.dump(self.export_chain(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'OuroborosLedger':
        """Load ledger from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        ledger = cls()

        for event_dict in data:
            event = Event(
                event_id=event_dict['event_id'],
                timestamp=event_dict['timestamp'],
                event_type=EventType(event_dict['event_type']),
                data=event_dict['data'],
                architect_id=event_dict['architect_id'],
                parent_hash=event_dict.get('parent_hash'),
                signature=event_dict.get('signature'),
                hash=event_dict.get('hash'),
            )

            ledger.chain.append(event)

            # Rebuild indices
            if event.architect_id not in ledger.index_by_architect:
                ledger.index_by_architect[event.architect_id] = []
            ledger.index_by_architect[event.architect_id].append(event)

            if event.event_type not in ledger.index_by_type:
                ledger.index_by_type[event.event_type] = []
            ledger.index_by_type[event.event_type].append(event)

        return ledger

    def get_stats(self) -> Dict[str, Any]:
        """Get ledger statistics"""
        event_counts = {}
        for event_type in EventType:
            event_counts[event_type.value] = len(self.get_events_by_type(event_type))

        return {
            'total_events': len(self.chain),
            'unique_architects': len(self.index_by_architect),
            'event_counts': event_counts,
            'chain_valid': self.verify_chain_integrity(),
        }
