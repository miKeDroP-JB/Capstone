#!/usr/bin/env python3
"""
0RB MEMORY SYSTEM
Multi-modal memory for the AGI Kernel.

Memory Types:
- Vector Store: Semantic similarity search
- Episodic Memory: Event sequences and experiences
- Semantic Memory: Facts, concepts, relationships

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import hashlib
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class MemoryEntry:
    """A single memory entry"""
    id: str
    content: str
    memory_type: str  # episodic, semantic, procedural
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance: float = 0.5
    decay_rate: float = 0.1

    def access(self):
        """Record memory access"""
        self.accessed_at = datetime.now()
        self.access_count += 1

    @property
    def strength(self) -> float:
        """Calculate memory strength based on recency and access"""
        age_hours = (datetime.now() - self.accessed_at).total_seconds() / 3600
        recency = math.exp(-self.decay_rate * age_hours)
        frequency = min(1.0, self.access_count / 10)
        return (recency * 0.5 + frequency * 0.3 + self.importance * 0.2)


class VectorStore:
    """
    Simple vector store for semantic search.
    Uses cosine similarity for matching.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict] = {}

    def _simple_embed(self, text: str) -> List[float]:
        """
        Simple embedding based on character frequencies.
        In production, use sentence-transformers or similar.
        """
        # Character frequency vector
        vector = [0.0] * self.dimension

        # Hash-based projection
        for i, char in enumerate(text.lower()):
            idx = hash(f"{char}_{i % 10}") % self.dimension
            vector[idx] += 1.0

        # Normalize
        magnitude = math.sqrt(sum(v*v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot = sum(x*y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x*x for x in a))
        mag_b = math.sqrt(sum(x*x for x in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def add(self, id: str, text: str, metadata: Dict = None):
        """Add a vector to the store"""
        embedding = self._simple_embed(text)
        self.vectors[id] = embedding
        self.metadata[id] = {
            "text": text,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat()
        }

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """Search for similar vectors"""
        query_vec = self._simple_embed(query)

        scores = []
        for id, vec in self.vectors.items():
            similarity = self._cosine_similarity(query_vec, vec)
            scores.append((id, similarity, self.metadata.get(id, {})))

        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def delete(self, id: str):
        """Delete a vector"""
        self.vectors.pop(id, None)
        self.metadata.pop(id, None)

    def __len__(self):
        return len(self.vectors)


class EpisodicMemory:
    """
    Episodic memory for event sequences.
    Stores experiences with temporal context.
    """

    @dataclass
    class Episode:
        """A single episode/event"""
        id: str
        event_type: str
        description: str
        context: Dict[str, Any]
        outcome: Optional[str] = None
        emotions: List[str] = field(default_factory=list)
        timestamp: datetime = field(default_factory=datetime.now)
        linked_episodes: List[str] = field(default_factory=list)
        importance: float = 0.5

    def __init__(self, max_episodes: int = 10000):
        self.episodes: Dict[str, EpisodicMemory.Episode] = {}
        self.timeline: List[str] = []  # Episode IDs in order
        self.max_episodes = max_episodes
        self._episode_counter = 0

    def record(
        self,
        event_type: str,
        description: str,
        context: Dict = None,
        outcome: str = None,
        importance: float = 0.5
    ) -> str:
        """Record a new episode"""
        self._episode_counter += 1
        episode_id = f"ep_{self._episode_counter:06d}"

        episode = self.Episode(
            id=episode_id,
            event_type=event_type,
            description=description,
            context=context or {},
            outcome=outcome,
            importance=importance
        )

        self.episodes[episode_id] = episode
        self.timeline.append(episode_id)

        # Link to recent similar episodes
        self._link_similar(episode)

        # Cleanup old episodes if needed
        if len(self.episodes) > self.max_episodes:
            self._cleanup()

        return episode_id

    def _link_similar(self, episode: 'EpisodicMemory.Episode'):
        """Link episode to similar recent episodes"""
        recent = self.timeline[-20:]  # Last 20 episodes
        for ep_id in recent:
            if ep_id == episode.id:
                continue
            other = self.episodes.get(ep_id)
            if other and other.event_type == episode.event_type:
                episode.linked_episodes.append(ep_id)

    def _cleanup(self):
        """Remove old, low-importance episodes"""
        # Sort by importance and age
        cutoff = datetime.now() - timedelta(days=30)
        to_remove = []

        for ep_id, ep in self.episodes.items():
            if ep.timestamp < cutoff and ep.importance < 0.3:
                to_remove.append(ep_id)

        for ep_id in to_remove[:len(self.episodes) - self.max_episodes]:
            del self.episodes[ep_id]
            if ep_id in self.timeline:
                self.timeline.remove(ep_id)

    def recall_recent(self, n: int = 10) -> List['EpisodicMemory.Episode']:
        """Recall most recent episodes"""
        recent_ids = self.timeline[-n:]
        return [self.episodes[id] for id in reversed(recent_ids) if id in self.episodes]

    def recall_by_type(self, event_type: str, n: int = 10) -> List['EpisodicMemory.Episode']:
        """Recall episodes by type"""
        matches = [ep for ep in self.episodes.values() if ep.event_type == event_type]
        matches.sort(key=lambda e: e.timestamp, reverse=True)
        return matches[:n]

    def recall_similar(self, description: str, n: int = 5) -> List['EpisodicMemory.Episode']:
        """Recall similar episodes by description"""
        # Simple keyword matching
        keywords = set(description.lower().split())

        scored = []
        for ep in self.episodes.values():
            ep_keywords = set(ep.description.lower().split())
            overlap = len(keywords & ep_keywords)
            if overlap > 0:
                scored.append((ep, overlap))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [ep for ep, _ in scored[:n]]

    def get_narrative(self, episode_id: str) -> str:
        """Get narrative of an episode and its linked episodes"""
        episode = self.episodes.get(episode_id)
        if not episode:
            return ""

        narrative = [f"[{episode.timestamp}] {episode.event_type}: {episode.description}"]

        if episode.outcome:
            narrative.append(f"  Outcome: {episode.outcome}")

        for linked_id in episode.linked_episodes[:3]:
            linked = self.episodes.get(linked_id)
            if linked:
                narrative.append(f"  Related: {linked.description[:50]}...")

        return "\n".join(narrative)


class SemanticMemory:
    """
    Semantic memory for facts, concepts, and relationships.
    Knowledge graph style storage.
    """

    @dataclass
    class Concept:
        """A concept/entity in semantic memory"""
        id: str
        name: str
        category: str
        attributes: Dict[str, Any] = field(default_factory=dict)
        relationships: List[Tuple[str, str]] = field(default_factory=list)  # (relation, target_id)
        sources: List[str] = field(default_factory=list)
        confidence: float = 1.0
        created_at: datetime = field(default_factory=datetime.now)
        updated_at: datetime = field(default_factory=datetime.now)

    def __init__(self):
        self.concepts: Dict[str, SemanticMemory.Concept] = {}
        self.categories: Dict[str, List[str]] = defaultdict(list)
        self.name_index: Dict[str, str] = {}  # name -> id mapping

    def add_concept(
        self,
        name: str,
        category: str,
        attributes: Dict = None,
        confidence: float = 1.0
    ) -> str:
        """Add or update a concept"""
        # Check if exists
        existing_id = self.name_index.get(name.lower())
        if existing_id:
            # Update existing
            concept = self.concepts[existing_id]
            concept.attributes.update(attributes or {})
            concept.confidence = max(concept.confidence, confidence)
            concept.updated_at = datetime.now()
            return existing_id

        # Create new
        concept_id = f"concept_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        concept = self.Concept(
            id=concept_id,
            name=name,
            category=category,
            attributes=attributes or {},
            confidence=confidence
        )

        self.concepts[concept_id] = concept
        self.categories[category].append(concept_id)
        self.name_index[name.lower()] = concept_id

        return concept_id

    def add_relationship(self, source_name: str, relation: str, target_name: str):
        """Add a relationship between concepts"""
        source_id = self.name_index.get(source_name.lower())
        target_id = self.name_index.get(target_name.lower())

        if not source_id:
            source_id = self.add_concept(source_name, "unknown")
        if not target_id:
            target_id = self.add_concept(target_name, "unknown")

        source = self.concepts[source_id]
        source.relationships.append((relation, target_id))

    def query(self, name: str) -> Optional['SemanticMemory.Concept']:
        """Query a concept by name"""
        concept_id = self.name_index.get(name.lower())
        return self.concepts.get(concept_id)

    def query_category(self, category: str) -> List['SemanticMemory.Concept']:
        """Get all concepts in a category"""
        concept_ids = self.categories.get(category, [])
        return [self.concepts[id] for id in concept_ids if id in self.concepts]

    def get_related(self, name: str, relation: str = None) -> List[Tuple[str, 'SemanticMemory.Concept']]:
        """Get related concepts"""
        concept = self.query(name)
        if not concept:
            return []

        related = []
        for rel, target_id in concept.relationships:
            if relation is None or rel == relation:
                target = self.concepts.get(target_id)
                if target:
                    related.append((rel, target))

        return related

    def search(self, query: str) -> List['SemanticMemory.Concept']:
        """Search concepts by name or attributes"""
        query_lower = query.lower()
        results = []

        for concept in self.concepts.values():
            # Name match
            if query_lower in concept.name.lower():
                results.append((concept, 1.0))
                continue

            # Attribute match
            for key, value in concept.attributes.items():
                if query_lower in str(value).lower():
                    results.append((concept, 0.5))
                    break

        results.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in results]


class UnifiedMemory:
    """
    Unified memory system combining all memory types.
    Provides a single interface for memory operations.
    """

    def __init__(self):
        self.vector_store = VectorStore()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()

        # Memory stats
        self.operations = 0

    def remember(
        self,
        content: str,
        memory_type: str = "auto",
        metadata: Dict = None,
        importance: float = 0.5
    ) -> str:
        """
        Store a memory, automatically routing to appropriate system.

        Args:
            content: The content to remember
            memory_type: "episodic", "semantic", "vector", or "auto"
            metadata: Additional metadata
            importance: Importance score (0-1)
        """
        self.operations += 1
        metadata = metadata or {}

        if memory_type == "auto":
            memory_type = self._classify_memory(content)

        if memory_type == "episodic":
            return self.episodic.record(
                event_type=metadata.get("event_type", "general"),
                description=content,
                context=metadata,
                importance=importance
            )

        elif memory_type == "semantic":
            return self.semantic.add_concept(
                name=metadata.get("name", content[:50]),
                category=metadata.get("category", "fact"),
                attributes={"content": content, **metadata},
            )

        else:  # vector
            mem_id = f"mem_{self.operations:06d}"
            self.vector_store.add(mem_id, content, metadata)
            return mem_id

    def recall(self, query: str, memory_type: str = "all", n: int = 5) -> List[Dict]:
        """
        Recall memories matching a query.

        Returns list of memory dicts with content and metadata.
        """
        results = []

        if memory_type in ["all", "vector"]:
            vector_results = self.vector_store.search(query, n)
            for id, score, meta in vector_results:
                results.append({
                    "type": "vector",
                    "id": id,
                    "content": meta.get("text", ""),
                    "score": score,
                    "metadata": meta
                })

        if memory_type in ["all", "episodic"]:
            episodes = self.episodic.recall_similar(query, n)
            for ep in episodes:
                results.append({
                    "type": "episodic",
                    "id": ep.id,
                    "content": ep.description,
                    "score": ep.importance,
                    "metadata": {"event_type": ep.event_type, "outcome": ep.outcome}
                })

        if memory_type in ["all", "semantic"]:
            concepts = self.semantic.search(query)[:n]
            for concept in concepts:
                results.append({
                    "type": "semantic",
                    "id": concept.id,
                    "content": concept.name,
                    "score": concept.confidence,
                    "metadata": concept.attributes
                })

        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:n]

    def _classify_memory(self, content: str) -> str:
        """Classify content into memory type"""
        content_lower = content.lower()

        # Episodic indicators
        episodic_words = ["happened", "did", "went", "saw", "heard", "felt", "yesterday", "today"]
        if any(word in content_lower for word in episodic_words):
            return "episodic"

        # Semantic indicators
        semantic_words = ["is a", "are", "means", "defined as", "consists of"]
        if any(phrase in content_lower for phrase in semantic_words):
            return "semantic"

        # Default to vector
        return "vector"

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system stats"""
        return {
            "operations": self.operations,
            "vector_store": len(self.vector_store),
            "episodic": len(self.episodic.episodes),
            "semantic": len(self.semantic.concepts),
        }


# Demo
def demo():
    """Demonstrate memory system"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    0RB MEMORY SYSTEM                          ║
║                                                               ║
║     Vector Store + Episodic Memory + Semantic Memory          ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    memory = UnifiedMemory()

    # Add various memories
    print("[+] Adding memories...")

    memory.remember("The user asked to build a REST API", "episodic",
                   {"event_type": "request"})
    memory.remember("REST API is an architectural style for web services", "semantic",
                   {"name": "REST API", "category": "technology"})
    memory.remember("Python is great for building APIs with FastAPI", "vector",
                   {"topic": "programming"})

    memory.semantic.add_relationship("REST API", "uses", "HTTP")
    memory.semantic.add_relationship("FastAPI", "implements", "REST API")

    # Query
    print("\n[*] Searching for 'API'...")
    results = memory.recall("API")
    for r in results:
        print(f"  [{r['type']}] {r['content'][:50]}... (score: {r['score']:.2f})")

    # Stats
    print(f"\n[*] Memory Stats: {memory.get_stats()}")


if __name__ == "__main__":
    demo()
