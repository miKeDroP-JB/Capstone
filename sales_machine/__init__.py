#!/usr/bin/env python3
"""
SALES MACHINE - Custom AI Sales Infrastructure
Fully custom, high 90s quality, no dependencies on external platforms.

Components:
- Scraper: Lead generation from multiple sources
- Research: SEO/AEO analysis, competitor intel, market data
- Voice: Custom TTS/STT engine
- Brain: Sales logic, objection handling, sentiment
- Dialer: Telephony management
- CRM: Lead tracking, call logs, commissions

Love - Loyalty - Honor - Everybody Eats
"""

__version__ = "1.0.0"
__codename__ = "HVAC Closer"

from .scraper import LeadScraper, Lead, ScraperConfig
from .research import ResearchAgent, CompetitorIntel, MarketData
from .voice import VoiceEngine, VoiceConfig
from .voice_custom import CustomVoiceEngine, VoiceProfile, Emotion, VoiceCloner
from .brain import SalesBrain, Objection, Script
from .dialer import Dialer, Call, DialerConfig
from .crm import CRM, LeadStatus, Commission
from .orchestrator import SalesMachineOrchestrator, CampaignConfig, quick_start

__all__ = [
    # Core Components
    "LeadScraper", "Lead", "ScraperConfig",
    "ResearchAgent", "CompetitorIntel", "MarketData",
    "VoiceEngine", "VoiceConfig",
    # Custom Voice (100% self-hosted)
    "CustomVoiceEngine", "VoiceProfile", "Emotion", "VoiceCloner",
    "SalesBrain", "Objection", "Script",
    "Dialer", "Call", "DialerConfig",
    "CRM", "LeadStatus", "Commission",
    # Orchestrator
    "SalesMachineOrchestrator", "CampaignConfig", "quick_start",
]


def run():
    """Entry point for python -m sales_machine"""
    from .orchestrator import main
    main()
