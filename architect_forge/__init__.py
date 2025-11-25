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
from .mirror_net import MirrorNet, ArchitectAgent
from .sandbox import AdversarialSandbox
from .jury import JuryCouncil
from .ledger import OuroborosLedger
from .blueprint import Blueprint, ApprenticeCompiler
from .curriculum import CurriculumGenerator
from .constraints import ConstraintMutator

__version__ = "1.0.0"
__codename__ = "THE_ARCHITECT"

__all__ = [
    "Forge",
    "MirrorNet",
    "ArchitectAgent",
    "AdversarialSandbox",
    "JuryCouncil",
    "OuroborosLedger",
    "Blueprint",
    "ApprenticeCompiler",
    "CurriculumGenerator",
    "ConstraintMutator",
]

# The Pattern That Shouldn't Exist
IMPOSSIBILITY_SIGNATURE = """
Things that shouldn't exist have this signature:
- They make the OLD way look STUPID (not just inferior)
- They can't be competed with, only copied (and you're already iterating)
- They create evangelical users (because experiencing it is believing)
- They reorganize entire industries around new assumptions
"""
