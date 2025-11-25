"""
OUROBOROS LEDGER - Trust and Provenance Tracking
═══════════════════════════════════════════════════════════════
Cryptographic signing, full provenance chain, reputation scoring,
and pattern attribution. The serpent eating its tail - every change
feeds back into the system.

"Every decision is signed. Every pattern is traced.
 Trust is earned, not assumed."
═══════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class EntryType(Enum):
    """Types of ledger entries"""
    TOURNAMENT_START = "tournament_start"
    TOURNAMENT_ROUND = "tournament_round"
    TOURNAMENT_COMPLETE = "tournament_complete"
    SOLUTION_SUBMITTED = "solution_submitted"
    VERDICT_ISSUED = "verdict_issued"
    BLUEPRINT_GENERATED = "blueprint_generated"
    APPRENTICE_DEPLOYED = "apprentice_deployed"
    PATTERN_INJECTED = "pattern_injected"
    EMERGENCE_DETECTED = "emergence_detected"
    HUMAN_REVIEW = "human_review"
    REPUTATION_UPDATE = "reputation_update"


@dataclass
class LedgerEntry:
    """A single entry in the Ouroboros Ledger"""
    entry_type: str
    data: Dict[str, Any]
    signature: str
    entry_id: str = field(default_factory=lambda: f"entry_{uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    previous_hash: Optional[str] = None

    def compute_hash(self) -> str:
        """Compute hash of this entry"""
        content = json.dumps({
            "entry_id": self.entry_id,
            "entry_type": self.entry_type,
            "data": self.data,
            "signature": self.signature,
            "timestamp": self.timestamp.isoformat(),
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "entry_type": self.entry_type,
            "data": self.data,
            "signature": self.signature,
            "timestamp": self.timestamp.isoformat(),
            "previous_hash": self.previous_hash,
            "hash": self.compute_hash()
        }


@dataclass
class ReputationScore:
    """Reputation tracking for entities (agents, jurors, etc.)"""
    entity_id: str
    entity_type: str  # "agent", "juror", "blueprint"
    score: float = 0.5
    contributions: int = 0
    successful_contributions: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)

    def update(self, success: bool, weight: float = 1.0) -> None:
        """Update reputation based on contribution outcome"""
        self.contributions += 1
        if success:
            self.successful_contributions += 1
            delta = 0.02 * weight
        else:
            delta = -0.01 * weight

        self.score = max(0.0, min(1.0, self.score + delta))
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "delta": delta,
            "new_score": self.score
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "score": self.score,
            "success_rate": self.successful_contributions / self.contributions if self.contributions > 0 else 0
        }


class OuroborosLedger:
    """
    The Ouroboros Ledger - immutable record of all Forge activity.

    Features:
    - Cryptographic chain (each entry linked to previous)
    - Full provenance tracking
    - Reputation system
    - Pattern attribution
    - Audit trail for human review
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("architect_forge/storage/ledger")
        self.entries: List[LedgerEntry] = []
        self.reputations: Dict[str, ReputationScore] = {}
        self.pattern_attributions: Dict[str, List[str]] = {}  # pattern_id -> [agent_ids]
        self._connected = False

    async def connect(self) -> None:
        """Connect to ledger storage"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        await self._load_existing()
        self._connected = True
        print(f"  Ouroboros Ledger connected: {len(self.entries)} entries loaded")

    async def _load_existing(self) -> None:
        """Load existing ledger entries from storage"""
        ledger_file = self.storage_path / "ledger.json"
        if ledger_file.exists():
            try:
                with open(ledger_file, "r") as f:
                    data = json.load(f)
                    for entry_data in data.get("entries", []):
                        entry = LedgerEntry(
                            entry_id=entry_data["entry_id"],
                            entry_type=entry_data["entry_type"],
                            data=entry_data["data"],
                            signature=entry_data["signature"],
                            timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                            previous_hash=entry_data.get("previous_hash")
                        )
                        self.entries.append(entry)

                    for rep_data in data.get("reputations", []):
                        rep = ReputationScore(
                            entity_id=rep_data["entity_id"],
                            entity_type=rep_data["entity_type"],
                            score=rep_data["score"],
                            contributions=rep_data.get("contributions", 0),
                            successful_contributions=rep_data.get("successful_contributions", 0)
                        )
                        self.reputations[rep.entity_id] = rep
            except (json.JSONDecodeError, KeyError):
                pass  # Start fresh if file is corrupted

    async def _save(self) -> None:
        """Save ledger to storage"""
        ledger_file = self.storage_path / "ledger.json"
        data = {
            "entries": [e.to_dict() for e in self.entries],
            "reputations": [r.to_dict() for r in self.reputations.values()],
            "pattern_attributions": self.pattern_attributions
        }
        with open(ledger_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    async def record(self, entry: LedgerEntry) -> str:
        """Record a new entry to the ledger"""
        # Link to previous entry
        if self.entries:
            entry.previous_hash = self.entries[-1].compute_hash()

        self.entries.append(entry)
        await self._save()

        return entry.entry_id

    async def get_entry(self, entry_id: str) -> Optional[LedgerEntry]:
        """Retrieve an entry by ID"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    async def get_entries_by_type(self, entry_type: str) -> List[LedgerEntry]:
        """Get all entries of a specific type"""
        return [e for e in self.entries if e.entry_type == entry_type]

    async def verify_chain(self) -> Tuple[bool, Optional[str]]:
        """Verify the integrity of the ledger chain"""
        if len(self.entries) < 2:
            return True, None

        for i in range(1, len(self.entries)):
            expected_hash = self.entries[i - 1].compute_hash()
            actual_hash = self.entries[i].previous_hash

            if expected_hash != actual_hash:
                return False, f"Chain broken at entry {self.entries[i].entry_id}"

        return True, None

    def get_reputation(self, entity_id: str) -> Optional[ReputationScore]:
        """Get reputation for an entity"""
        return self.reputations.get(entity_id)

    def update_reputation(
        self,
        entity_id: str,
        entity_type: str,
        success: bool,
        weight: float = 1.0
    ) -> float:
        """Update reputation for an entity"""
        if entity_id not in self.reputations:
            self.reputations[entity_id] = ReputationScore(
                entity_id=entity_id,
                entity_type=entity_type
            )

        self.reputations[entity_id].update(success, weight)
        return self.reputations[entity_id].score

    def attribute_pattern(self, pattern_id: str, agent_id: str) -> None:
        """Attribute a pattern discovery to an agent"""
        if pattern_id not in self.pattern_attributions:
            self.pattern_attributions[pattern_id] = []

        if agent_id not in self.pattern_attributions[pattern_id]:
            self.pattern_attributions[pattern_id].append(agent_id)

    def get_pattern_creators(self, pattern_id: str) -> List[str]:
        """Get agents who contributed to a pattern"""
        return self.pattern_attributions.get(pattern_id, [])

    async def get_provenance(self, entity_id: str) -> List[LedgerEntry]:
        """Get full provenance chain for an entity"""
        relevant_entries = []
        for entry in self.entries:
            # Check if entity is mentioned in entry data
            data_str = json.dumps(entry.data)
            if entity_id in data_str:
                relevant_entries.append(entry)
        return relevant_entries

    async def export_audit_trail(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Export audit trail for a date range"""
        trail = []
        for entry in self.entries:
            if start_date and entry.timestamp < start_date:
                continue
            if end_date and entry.timestamp > end_date:
                continue
            trail.append(entry.to_dict())
        return trail

    def get_statistics(self) -> Dict[str, Any]:
        """Get ledger statistics"""
        entry_types = {}
        for entry in self.entries:
            entry_types[entry.entry_type] = entry_types.get(entry.entry_type, 0) + 1

        return {
            "total_entries": len(self.entries),
            "entry_type_distribution": entry_types,
            "tracked_entities": len(self.reputations),
            "attributed_patterns": len(self.pattern_attributions),
            "chain_length": len(self.entries)
        }

    async def close(self) -> None:
        """Close ledger connection"""
        await self._save()
        self._connected = False
        print("  Ledger closed")


# Import Tuple for type hints
from typing import Tuple
