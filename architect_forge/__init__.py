"""
THE ARCHITECT FORGE v1.0
═══════════════════════════════════════════════════════════════
The Impossibility Compiler - A self-authoring meta-system that
generates curricula, environments, tasks, and evaluation regimes,
trains populations of architect-agents with meta-learning and
evolutionary methods, certifies the best, and injects those
designs back into the core.
═══════════════════════════════════════════════════════════════

"Some patterns can't be unseen. Some systems can't be unbuilt."
"""

from .forge import Forge
from .mirror_net import MirrorNet, ArchitectAgent, InductiveBias, Specialization
from .sandbox import AdversarialSandbox, SandboxResult, SandboxMode
from .jury import JuryCouncil, Verdict, CertificationLevel
from .ledger import OuroborosLedger, LedgerEntry
from .blueprint import Blueprint, ApprenticeCompiler, Apprentice
from .curriculum import CurriculumGenerator, Task, TaskType, Difficulty
from .constraints import ConstraintMutator, MutationType
from .orb_integration import (
    OrbEmpireForge, AvatarForge, Avatar,
    create_empire_forge
)

__version__ = "1.0.0"
__codename__ = "THE_ARCHITECT"

__all__ = [
    # Core
    "Forge",
    # Population
    "MirrorNet",
    "ArchitectAgent",
    "InductiveBias",
    "Specialization",
    # Testing
    "AdversarialSandbox",
    "SandboxResult",
    "SandboxMode",
    # Certification
    "JuryCouncil",
    "Verdict",
    "CertificationLevel",
    # Provenance
    "OuroborosLedger",
    "LedgerEntry",
    # Output
    "Blueprint",
    "ApprenticeCompiler",
    "Apprentice",
    # Tasks
    "CurriculumGenerator",
    "Task",
    "TaskType",
    "Difficulty",
    # Anti-Framework
    "ConstraintMutator",
    "MutationType",
    # 0RB Integration
    "OrbEmpireForge",
    "AvatarForge",
    "Avatar",
    "create_empire_forge",
]

# The Pattern That Shouldn't Exist
IMPOSSIBILITY_SIGNATURE = """
Things that shouldn't exist have this signature:
- They make the OLD way look STUPID (not just inferior)
- They can't be competed with, only copied (and you're already iterating)
- They create evangelical users (because experiencing it is believing)
- They reorganize entire industries around new assumptions
"""
