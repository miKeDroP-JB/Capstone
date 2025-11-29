#!/usr/bin/env python3
"""
0RB_AETHER VERTICALS
Industry-specific implementations built on the core platform.

Current Verticals:
- Finance: Trading, risk analysis, compliance, DeFi
- Healthcare: Patient management, diagnostics, HIPAA compliance

Love - Loyalty - Honor - Everybody Eats
"""

__version__ = "0.1.0"

from . import finance
from . import healthcare

__all__ = ["finance", "healthcare"]
