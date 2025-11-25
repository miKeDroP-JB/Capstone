"""
0RB EMPIRE INTEGRATION - Connecting the Forge to the Avatars
═══════════════════════════════════════════════════════════════
Integration layer that connects the Architect Forge to the
existing 0RB Empire infrastructure.

Each avatar becomes a META-AVATAR that spawns specialists:
- Apollo → Strategic planning architects
- Mercury → Communication architects
- Athena → Analysis architects
- Ares → Adversarial testing architects
- Hermes → Integration architects
- Hephaestus → Builder architects
- Artemis → Quality-control architects
═══════════════════════════════════════════════════════════════
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

from .forge import Forge, ForgeConfig
from .curriculum import Task, TaskType, Difficulty, CurriculumGenerator
from .mirror_net import MirrorNet, InductiveBias, Specialization
from .blueprint import Blueprint, Apprentice


class Avatar(Enum):
    """The 7 Avatars of 0RB Empire"""
    APOLLO = "apollo"           # Strategic Planning
    MERCURY = "mercury"         # Communication
    ATHENA = "athena"           # Analysis
    ARES = "ares"               # Adversarial/Execution
    HERMES = "hermes"           # Integration/Speed
    HEPHAESTUS = "hephaestus"   # Building/Creation
    ARTEMIS = "artemis"         # Quality/Security


# Avatar to TaskType mapping
AVATAR_TASK_MAPPING = {
    Avatar.APOLLO: [TaskType.STRATEGY, TaskType.META],
    Avatar.MERCURY: [TaskType.COMMUNICATION, TaskType.CREATIVE],
    Avatar.ATHENA: [TaskType.ANALYSIS, TaskType.DESIGN],
    Avatar.ARES: [TaskType.SECURITY, TaskType.OPTIMIZATION],
    Avatar.HERMES: [TaskType.INTEGRATION, TaskType.OPTIMIZATION],
    Avatar.HEPHAESTUS: [TaskType.CODE, TaskType.DESIGN],
    Avatar.ARTEMIS: [TaskType.SECURITY, TaskType.ANALYSIS],
}

# Avatar to InductiveBias mapping
AVATAR_BIAS_MAPPING = {
    Avatar.APOLLO: InductiveBias.SYSTEMATIC,
    Avatar.MERCURY: InductiveBias.INTUITIVE,
    Avatar.ATHENA: InductiveBias.ANALYTICAL,
    Avatar.ARES: InductiveBias.ADVERSARIAL,
    Avatar.HERMES: InductiveBias.COLLABORATIVE,
    Avatar.HEPHAESTUS: InductiveBias.CREATIVE,
    Avatar.ARTEMIS: InductiveBias.CONTRARIAN,
}

# Avatar to Specialization mapping
AVATAR_SPEC_MAPPING = {
    Avatar.APOLLO: Specialization.STRATEGY,
    Avatar.MERCURY: Specialization.COMMUNICATION,
    Avatar.ATHENA: Specialization.ANALYSIS,
    Avatar.ARES: Specialization.SECURITY,
    Avatar.HERMES: Specialization.INTEGRATION,
    Avatar.HEPHAESTUS: Specialization.CODE,
    Avatar.ARTEMIS: Specialization.SECURITY,
}


@dataclass
class AvatarForgeConfig:
    """Configuration for an avatar's forge instance"""
    avatar: Avatar
    population_size: int = 8
    tournament_rounds: int = 5
    specializations: List[TaskType] = None

    def __post_init__(self):
        if self.specializations is None:
            self.specializations = AVATAR_TASK_MAPPING.get(self.avatar, [TaskType.CODE])


class AvatarForge:
    """
    A specialized Forge instance for a specific Avatar.

    Each avatar gets its own Forge that generates architects
    specialized for that avatar's domain.
    """

    def __init__(self, config: AvatarForgeConfig):
        self.config = config
        self.avatar = config.avatar

        forge_config = ForgeConfig(
            population_size=config.population_size,
            tournament_rounds=config.tournament_rounds
        )

        self.forge = Forge(
            config=forge_config,
            storage_path=Path(f"architect_forge/storage/{config.avatar.value}")
        )

        self.generated_apprentices: List[Apprentice] = []
        self.active_blueprints: List[Blueprint] = []

    async def initialize(self) -> None:
        """Initialize the avatar's forge"""
        await self.forge.ignite()
        print(f"  ⚡ {self.avatar.value.upper()} Forge initialized")

    async def generate_specialist(
        self,
        objective: str,
        constraints: Optional[List[str]] = None
    ) -> Apprentice:
        """Generate a specialist apprentice for this avatar's domain"""
        # Create task appropriate for this avatar
        task_type = self.config.specializations[0] if self.config.specializations else TaskType.CODE

        task = Task(
            task_id=f"task_{self.avatar.value}_{len(self.active_blueprints)}",
            task_type=task_type.value,
            objective=objective,
            constraints=constraints or ["Complete efficiently", "Maintain quality"],
            success_criteria=f"Achieve {self.avatar.value}-level excellence",
            difficulty=Difficulty.HARD
        )

        # Run tournament
        result = await self.forge.run_tournament(task)

        # Get best blueprint
        if result.blueprints:
            best_blueprint = result.blueprints[0]
            self.active_blueprints.append(best_blueprint)

            # Compile to apprentice
            apprentice = await self.forge.compile_apprentice(best_blueprint)
            self.generated_apprentices.append(apprentice)

            return apprentice

        raise RuntimeError("Tournament produced no blueprints")

    async def train_population(self, curriculum: List[Task]) -> Dict[str, Any]:
        """Train the population on a curriculum"""
        results = []
        for task in curriculum:
            result = await self.forge.run_tournament(task)
            results.append(result.metrics)

        return {
            "avatar": self.avatar.value,
            "tasks_completed": len(results),
            "average_score": sum(r["peak_score"] for r in results) / len(results) if results else 0
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get avatar forge statistics"""
        return {
            "avatar": self.avatar.value,
            "forge_stats": self.forge.get_statistics(),
            "blueprints_generated": len(self.active_blueprints),
            "apprentices_active": len(self.generated_apprentices)
        }


class OrbEmpireForge:
    """
    Master orchestrator that manages all Avatar Forges.

    This is the 0RB Empire's meta-level: each Avatar can now
    spawn specialized architects through their dedicated Forge.
    """

    def __init__(self):
        self.avatar_forges: Dict[Avatar, AvatarForge] = {}
        self.initialized = False

    async def initialize_all(self) -> None:
        """Initialize all avatar forges"""
        print("\n" + "═" * 60)
        print("  0RB EMPIRE FORGE - INITIALIZING ALL AVATARS")
        print("═" * 60 + "\n")

        for avatar in Avatar:
            config = AvatarForgeConfig(avatar=avatar)
            forge = AvatarForge(config)
            await forge.initialize()
            self.avatar_forges[avatar] = forge

        self.initialized = True
        print("\n  ✓ All Avatar Forges operational\n")

    async def get_forge(self, avatar: Avatar) -> AvatarForge:
        """Get a specific avatar's forge"""
        if avatar not in self.avatar_forges:
            raise ValueError(f"Avatar {avatar.value} not initialized")
        return self.avatar_forges[avatar]

    async def generate_specialist_for(
        self,
        avatar: Avatar,
        objective: str,
        constraints: Optional[List[str]] = None
    ) -> Apprentice:
        """Generate a specialist for a specific avatar"""
        forge = await self.get_forge(avatar)
        return await forge.generate_specialist(objective, constraints)

    async def cross_train(
        self,
        source_avatar: Avatar,
        target_avatar: Avatar,
        pattern: Dict[str, Any]
    ) -> None:
        """Transfer a successful pattern from one avatar to another"""
        source_forge = await self.get_forge(source_avatar)
        target_forge = await self.get_forge(target_avatar)

        # Inject pattern into target's MirrorNet
        await target_forge.forge.mirror_net.inject_pattern({
            **pattern,
            "transferred_from": source_avatar.value
        })

        print(f"  Pattern transferred: {source_avatar.value} → {target_avatar.value}")

    async def run_empire_tournament(self, task: Task) -> Dict[Avatar, Any]:
        """Run a tournament across all avatars for the same task"""
        results = {}

        for avatar, forge in self.avatar_forges.items():
            result = await forge.forge.run_tournament(task)
            results[avatar] = {
                "winner": result.winner.name,
                "score": result.metrics["peak_score"],
                "blueprints": len(result.blueprints)
            }

        # Find empire-wide winner
        best_avatar = max(results.keys(), key=lambda a: results[a]["score"])
        print(f"\n  🏆 Empire Winner: {best_avatar.value.upper()} ({results[best_avatar]['score']:.2f})")

        return results

    def get_empire_statistics(self) -> Dict[str, Any]:
        """Get statistics for the entire empire"""
        stats = {
            "avatars_active": len(self.avatar_forges),
            "avatar_stats": {}
        }

        for avatar, forge in self.avatar_forges.items():
            stats["avatar_stats"][avatar.value] = forge.get_statistics()

        return stats


# Convenience function to create a ready-to-use empire forge
async def create_empire_forge() -> OrbEmpireForge:
    """Create and initialize a full 0RB Empire Forge"""
    empire = OrbEmpireForge()
    await empire.initialize_all()
    return empire
