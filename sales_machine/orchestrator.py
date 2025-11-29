"""
SALES MACHINE ORCHESTRATOR
===========================
The brain that coordinates all components into a unified calling machine.

Flow:
1. Scraper finds leads -> Research enriches them -> Brain prepares scripts
2. Dialer initiates calls -> Voice handles TTS/STT -> Brain runs conversation
3. CRM tracks everything -> Commission calculated on success

Love - Loyalty - Honor - Everybody Eats
"""

import asyncio
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
import logging

# Import all components
from .scraper import LeadScraper, Lead, ScraperConfig
from .research import ResearchAgent, BusinessResearch
from .voice import VoiceEngine, VoiceConfig, VoiceProvider, STTProvider
from .brain import SalesBrain, ConversationState
from .dialer import Dialer, DialerConfig, Call, CallStatus
from .crm import CRM, CRMLead, LeadStatus, CallLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class CampaignStatus(Enum):
    """Campaign lifecycle states"""
    IDLE = "idle"
    LOADING_LEADS = "loading_leads"
    RESEARCHING = "researching"
    CALLING = "calling"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class CampaignConfig:
    """Campaign configuration"""
    name: str = "HVAC AI Campaign"

    # Scraping settings
    industry: str = "hvac"
    locations: List[str] = field(default_factory=lambda: ["Houston, TX"])
    max_leads_per_location: int = 50

    # Calling settings
    calls_per_hour: int = 30
    max_concurrent_calls: int = 5
    retry_failed_calls: bool = True
    max_retries: int = 3

    # Voice settings
    voice_id: str = "professional_male"
    speaking_rate: float = 1.0

    # Working hours (24h format)
    start_hour: int = 9
    end_hour: int = 18
    work_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Mon-Fri

    # Commission
    commission_rate: float = 0.10  # 10%

    # Research depth
    do_seo_analysis: bool = True
    do_competitor_analysis: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CampaignStats:
    """Real-time campaign statistics"""
    total_leads: int = 0
    leads_researched: int = 0
    calls_made: int = 0
    calls_connected: int = 0
    calls_completed: int = 0
    appointments_set: int = 0
    sales_closed: int = 0
    total_revenue: float = 0.0
    total_commission: float = 0.0
    avg_call_duration: float = 0.0
    conversion_rate: float = 0.0

    def update(self, crm: CRM):
        """Update stats from CRM"""
        analytics = crm.get_analytics()
        pipeline = analytics.get("pipeline", {})
        performance = analytics.get("performance", {})

        self.calls_made = performance.get("total_calls", 0)
        self.appointments_set = pipeline.get("appointment_set", 0)
        self.sales_closed = pipeline.get("closed_won", 0)

        if self.calls_made > 0:
            self.conversion_rate = (self.appointments_set + self.sales_closed) / self.calls_made


class SalesMachineOrchestrator:
    """
    The master orchestrator that coordinates all sales machine components.

    This is your AI sales team in a box:
    - Finds leads automatically
    - Researches each business
    - Makes intelligent calls
    - Handles objections
    - Tracks everything
    - Calculates commissions
    """

    def __init__(self, config: Optional[CampaignConfig] = None):
        self.config = config or CampaignConfig()

        # Initialize components
        self.scraper = LeadScraper()
        self.researcher = ResearchAgent()
        self.voice = VoiceEngine()
        self.brain = SalesBrain()
        self.dialer = Dialer()
        self.crm = CRM()

        # State
        self.status = CampaignStatus.IDLE
        self.stats = CampaignStats()
        self.leads_queue: asyncio.Queue = asyncio.Queue()
        self.active_calls: Dict[str, Call] = {}

        # Callbacks
        self._on_call_start: Optional[Callable] = None
        self._on_call_end: Optional[Callable] = None
        self._on_appointment: Optional[Callable] = None
        self._on_sale: Optional[Callable] = None

        logger.info("🚀 Sales Machine Orchestrator initialized")
        logger.info(f"   Campaign: {self.config.name}")
        logger.info(f"   Industry: {self.config.industry}")
        logger.info(f"   Locations: {', '.join(self.config.locations)}")

    # ========== CONFIGURATION ==========

    def configure_voice(
        self,
        tts_provider: str = "elevenlabs",
        stt_provider: str = "deepgram",
        voice_id: str = "professional_male",
        api_keys: Optional[Dict[str, str]] = None
    ):
        """Configure voice engine"""
        provider_map = {
            "elevenlabs": VoiceProvider.ELEVENLABS,
            "openai": VoiceProvider.OPENAI,
            "playht": VoiceProvider.PLAYHT
        }

        stt_map = {
            "deepgram": STTProvider.DEEPGRAM,
            "whisper": STTProvider.WHISPER
        }

        config = VoiceConfig(
            tts_provider=provider_map.get(tts_provider, VoiceProvider.ELEVENLABS),
            stt_provider=stt_map.get(stt_provider, STTProvider.DEEPGRAM),
            voice_id=voice_id
        )

        self.voice = VoiceEngine(config)

        if api_keys:
            self.voice.set_api_keys(**api_keys)

        logger.info(f"🎙️ Voice configured: {tts_provider} / {stt_provider}")

    def configure_dialer(
        self,
        twilio_sid: str,
        twilio_token: str,
        twilio_number: str,
        calls_per_hour: int = 30
    ):
        """Configure Twilio dialer"""
        config = DialerConfig(
            twilio_account_sid=twilio_sid,
            twilio_auth_token=twilio_token,
            twilio_phone_number=twilio_number,
            max_calls_per_hour=calls_per_hour
        )

        self.dialer = Dialer(config)
        logger.info(f"📞 Dialer configured: {twilio_number}")

    def set_callbacks(
        self,
        on_call_start: Optional[Callable] = None,
        on_call_end: Optional[Callable] = None,
        on_appointment: Optional[Callable] = None,
        on_sale: Optional[Callable] = None
    ):
        """Set event callbacks"""
        self._on_call_start = on_call_start
        self._on_call_end = on_call_end
        self._on_appointment = on_appointment
        self._on_sale = on_sale

    # ========== LEAD MANAGEMENT ==========

    async def load_leads_from_scraper(self, locations: Optional[List[str]] = None):
        """Scrape leads from configured sources"""
        self.status = CampaignStatus.LOADING_LEADS
        locations = locations or self.config.locations

        logger.info(f"🔍 Scraping leads for {len(locations)} locations...")

        all_leads = []
        for location in locations:
            leads = await self.scraper.scrape_all_sources(
                industry=self.config.industry,
                location=location,
                max_results=self.config.max_leads_per_location
            )
            all_leads.extend(leads)
            logger.info(f"   Found {len(leads)} leads in {location}")

        # Deduplicate by phone
        seen_phones = set()
        unique_leads = []
        for lead in all_leads:
            if lead.phone and lead.phone not in seen_phones:
                seen_phones.add(lead.phone)
                unique_leads.append(lead)

        # Add to CRM and queue
        for lead in unique_leads:
            crm_lead = self.crm.add_lead(
                business_name=lead.name,
                phone=lead.phone or "",
                email=lead.email,
                industry=self.config.industry,
                source=lead.source,
                metadata={
                    "address": lead.address,
                    "website": lead.website,
                    "rating": lead.rating,
                    "review_count": lead.review_count
                }
            )
            await self.leads_queue.put(crm_lead)

        self.stats.total_leads = len(unique_leads)
        logger.info(f"✅ Loaded {len(unique_leads)} unique leads")

        return unique_leads

    async def load_leads_from_csv(self, csv_path: str):
        """Load leads from CSV file"""
        self.status = CampaignStatus.LOADING_LEADS

        import csv
        leads = []

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                crm_lead = self.crm.add_lead(
                    business_name=row.get('business_name', row.get('name', 'Unknown')),
                    phone=row.get('phone', ''),
                    email=row.get('email'),
                    industry=self.config.industry,
                    source="csv_import"
                )
                leads.append(crm_lead)
                await self.leads_queue.put(crm_lead)

        self.stats.total_leads = len(leads)
        logger.info(f"✅ Loaded {len(leads)} leads from CSV")

        return leads

    async def load_leads_from_list(self, leads_data: List[Dict[str, Any]]):
        """Load leads from a list of dictionaries"""
        self.status = CampaignStatus.LOADING_LEADS

        for data in leads_data:
            crm_lead = self.crm.add_lead(
                business_name=data.get('business_name', data.get('name', 'Unknown')),
                phone=data.get('phone', ''),
                email=data.get('email'),
                industry=self.config.industry,
                source=data.get('source', 'manual')
            )
            await self.leads_queue.put(crm_lead)

        self.stats.total_leads = len(leads_data)
        logger.info(f"✅ Loaded {len(leads_data)} leads")

    # ========== RESEARCH ==========

    async def research_lead(self, lead: CRMLead) -> Optional[BusinessResearch]:
        """Research a single lead"""
        try:
            research = await self.researcher.research_business(
                business_name=lead.business_name,
                website=lead.metadata.get('website'),
                industry=lead.industry,
                location=lead.metadata.get('address'),
                do_seo=self.config.do_seo_analysis,
                do_competitors=self.config.do_competitor_analysis
            )

            # Update lead with research
            lead.metadata['research'] = {
                'talking_points': research.talking_points,
                'pain_points': research.pain_points,
                'opportunities': research.opportunities,
                'seo_score': research.seo_data.overall_score if research.seo_data else None,
                'competitor_count': len(research.competitors)
            }

            self.stats.leads_researched += 1
            return research

        except Exception as e:
            logger.error(f"Research failed for {lead.business_name}: {e}")
            return None

    async def research_all_leads(self):
        """Research all leads in parallel"""
        self.status = CampaignStatus.RESEARCHING

        leads = list(self.crm.leads.values())
        logger.info(f"🔬 Researching {len(leads)} leads...")

        # Process in batches of 10
        batch_size = 10
        for i in range(0, len(leads), batch_size):
            batch = leads[i:i + batch_size]
            tasks = [self.research_lead(lead) for lead in batch]
            await asyncio.gather(*tasks)
            logger.info(f"   Researched {min(i + batch_size, len(leads))}/{len(leads)}")

        logger.info(f"✅ Research complete: {self.stats.leads_researched} leads enriched")

    # ========== CALLING ==========

    async def _handle_call(self, lead: CRMLead):
        """Handle a single call with full conversation flow"""
        try:
            # Get research data
            research = lead.metadata.get('research', {})
            talking_points = research.get('talking_points', [])
            pain_points = research.get('pain_points', [])

            # Initialize brain with lead context
            self.brain.set_lead_context(
                business_name=lead.business_name,
                industry=lead.industry,
                talking_points=talking_points,
                pain_points=pain_points
            )

            # Start the call
            logger.info(f"📞 Calling {lead.business_name} at {lead.phone}...")

            if self._on_call_start:
                await self._on_call_start(lead)

            # Make the call
            call = await self.dialer.call(
                to_number=lead.phone,
                lead_id=lead.id
            )

            if not call or call.status == CallStatus.FAILED:
                logger.warning(f"   Call failed to connect")
                self.crm.log_call(lead.id, "failed", 0, "Call failed to connect")
                return

            self.active_calls[call.id] = call
            self.stats.calls_connected += 1

            # Run conversation loop
            conversation_active = True
            while conversation_active:
                # Get audio from call (STT)
                audio_stream = await self.dialer.get_audio_stream(call.id)
                if not audio_stream:
                    break

                # Transcribe
                transcript = await self.voice.transcribe_stream(audio_stream)
                if not transcript:
                    continue

                logger.info(f"   Customer: {transcript}")

                # Get AI response
                response = self.brain.process_input(transcript)
                logger.info(f"   Agent: {response}")

                # Synthesize and play
                audio = await self.voice.synthesize(response)
                await self.dialer.play_audio(call.id, audio)

                # Check conversation state
                state = self.brain.get_state()

                if state == ConversationState.APPOINTMENT_SET:
                    self.stats.appointments_set += 1
                    if self._on_appointment:
                        await self._on_appointment(lead, self.brain.get_appointment_details())
                    conversation_active = False

                elif state == ConversationState.SALE_CLOSED:
                    self.stats.sales_closed += 1
                    sale_amount = self.brain.get_sale_amount()
                    self.stats.total_revenue += sale_amount
                    commission = sale_amount * self.config.commission_rate
                    self.stats.total_commission += commission

                    if self._on_sale:
                        await self._on_sale(lead, sale_amount, commission)
                    conversation_active = False

                elif state == ConversationState.ENDED:
                    conversation_active = False

            # End call
            call_duration = await self.dialer.end_call(call.id)
            del self.active_calls[call.id]

            # Log to CRM
            outcome = "appointment" if self.brain.get_state() == ConversationState.APPOINTMENT_SET else \
                      "sale" if self.brain.get_state() == ConversationState.SALE_CLOSED else \
                      "no_answer" if call_duration < 5 else "completed"

            self.crm.log_call(lead.id, outcome, call_duration, self.brain.get_conversation_summary())
            self.stats.calls_completed += 1

            if self._on_call_end:
                await self._on_call_end(lead, outcome, call_duration)

            logger.info(f"   Call ended: {outcome} ({call_duration}s)")

        except Exception as e:
            logger.error(f"Call error for {lead.business_name}: {e}")
            self.crm.log_call(lead.id, "error", 0, str(e))

    async def start_calling(self, max_calls: Optional[int] = None):
        """Start the calling campaign"""
        self.status = CampaignStatus.CALLING

        calls_made = 0
        max_calls = max_calls or float('inf')

        logger.info("📞 Starting calling campaign...")
        logger.info(f"   Max concurrent calls: {self.config.max_concurrent_calls}")
        logger.info(f"   Calls per hour limit: {self.config.calls_per_hour}")

        # Create worker tasks
        workers = []
        for i in range(self.config.max_concurrent_calls):
            workers.append(asyncio.create_task(self._call_worker(i)))

        # Wait for all workers or max calls
        try:
            await asyncio.gather(*workers)
        except asyncio.CancelledError:
            logger.info("Campaign stopped")

        self.status = CampaignStatus.COMPLETED
        logger.info("✅ Calling campaign complete")
        self._print_stats()

    async def _call_worker(self, worker_id: int):
        """Worker that processes calls from the queue"""
        while self.status == CampaignStatus.CALLING:
            try:
                # Check if within working hours
                if not self._is_working_hours():
                    logger.info(f"Worker {worker_id}: Outside working hours, waiting...")
                    await asyncio.sleep(60)
                    continue

                # Get next lead
                try:
                    lead = await asyncio.wait_for(self.leads_queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    continue

                # Make the call
                await self._handle_call(lead)
                self.stats.calls_made += 1

                # Rate limiting
                delay = 3600 / self.config.calls_per_hour
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)

    def _is_working_hours(self) -> bool:
        """Check if current time is within working hours"""
        now = datetime.now()

        if now.weekday() not in self.config.work_days:
            return False

        if not (self.config.start_hour <= now.hour < self.config.end_hour):
            return False

        return True

    async def pause(self):
        """Pause the campaign"""
        self.status = CampaignStatus.PAUSED
        logger.info("⏸️ Campaign paused")

    async def resume(self):
        """Resume the campaign"""
        if self.status == CampaignStatus.PAUSED:
            self.status = CampaignStatus.CALLING
            logger.info("▶️ Campaign resumed")

    async def stop(self):
        """Stop the campaign"""
        self.status = CampaignStatus.IDLE

        # End all active calls
        for call_id in list(self.active_calls.keys()):
            await self.dialer.end_call(call_id)

        self.active_calls.clear()
        logger.info("🛑 Campaign stopped")

    # ========== STATS & REPORTING ==========

    def _print_stats(self):
        """Print campaign statistics"""
        self.stats.update(self.crm)

        print("\n" + "=" * 50)
        print("📊 CAMPAIGN STATISTICS")
        print("=" * 50)
        print(f"Total Leads:        {self.stats.total_leads}")
        print(f"Leads Researched:   {self.stats.leads_researched}")
        print(f"Calls Made:         {self.stats.calls_made}")
        print(f"Calls Connected:    {self.stats.calls_connected}")
        print(f"Calls Completed:    {self.stats.calls_completed}")
        print(f"Appointments Set:   {self.stats.appointments_set}")
        print(f"Sales Closed:       {self.stats.sales_closed}")
        print(f"Conversion Rate:    {self.stats.conversion_rate:.1%}")
        print("-" * 50)
        print(f"Total Revenue:      ${self.stats.total_revenue:,.2f}")
        print(f"Total Commission:   ${self.stats.total_commission:,.2f}")
        print("=" * 50 + "\n")

    def get_stats(self) -> Dict[str, Any]:
        """Get campaign statistics as dict"""
        self.stats.update(self.crm)
        return asdict(self.stats)

    def export_results(self, output_path: str = "campaign_results.json"):
        """Export campaign results to JSON"""
        results = {
            "config": self.config.to_dict(),
            "stats": self.get_stats(),
            "leads": [asdict(l) for l in self.crm.leads.values()],
            "calls": [asdict(c) for c in self.crm.call_logs],
            "appointments": [asdict(a) for a in self.crm.appointments],
            "timestamp": datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"📄 Results exported to {output_path}")

    # ========== QUICK START ==========

    async def run_campaign(
        self,
        leads_source: str = "scrape",
        csv_path: Optional[str] = None,
        leads_list: Optional[List[Dict]] = None,
        max_calls: Optional[int] = None,
        do_research: bool = True
    ):
        """
        Run a complete campaign from start to finish.

        Args:
            leads_source: "scrape", "csv", or "list"
            csv_path: Path to CSV file if leads_source is "csv"
            leads_list: List of lead dicts if leads_source is "list"
            max_calls: Maximum number of calls to make
            do_research: Whether to research leads before calling
        """
        try:
            # Step 1: Load leads
            if leads_source == "scrape":
                await self.load_leads_from_scraper()
            elif leads_source == "csv" and csv_path:
                await self.load_leads_from_csv(csv_path)
            elif leads_source == "list" and leads_list:
                await self.load_leads_from_list(leads_list)
            else:
                raise ValueError(f"Invalid leads source: {leads_source}")

            # Step 2: Research
            if do_research:
                await self.research_all_leads()

            # Step 3: Start calling
            await self.start_calling(max_calls)

            # Step 4: Export results
            self.export_results()

        except Exception as e:
            self.status = CampaignStatus.ERROR
            logger.error(f"Campaign error: {e}")
            raise


# ============================================================
# QUICK START FUNCTION
# ============================================================

async def quick_start(
    twilio_sid: str,
    twilio_token: str,
    twilio_number: str,
    elevenlabs_key: Optional[str] = None,
    deepgram_key: Optional[str] = None,
    locations: List[str] = None,
    industry: str = "hvac",
    max_calls: int = 10
):
    """
    Quick start the sales machine with minimal configuration.

    Example:
        asyncio.run(quick_start(
            twilio_sid="AC...",
            twilio_token="...",
            twilio_number="+1234567890",
            locations=["Houston, TX", "Dallas, TX"]
        ))
    """
    config = CampaignConfig(
        name=f"{industry.upper()} AI Campaign",
        industry=industry,
        locations=locations or ["Houston, TX"]
    )

    machine = SalesMachineOrchestrator(config)

    # Configure components
    machine.configure_dialer(twilio_sid, twilio_token, twilio_number)

    if elevenlabs_key or deepgram_key:
        machine.configure_voice(
            api_keys={
                "elevenlabs": elevenlabs_key,
                "deepgram": deepgram_key
            }
        )

    # Run campaign
    await machine.run_campaign(
        leads_source="scrape",
        max_calls=max_calls,
        do_research=True
    )

    return machine


# ============================================================
# CLI ENTRY POINT
# ============================================================

def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="🚀 Sales Machine - AI Calling System")
    parser.add_argument("--industry", default="hvac", help="Industry to target")
    parser.add_argument("--locations", nargs="+", default=["Houston, TX"], help="Locations to scrape")
    parser.add_argument("--max-calls", type=int, default=10, help="Maximum calls to make")
    parser.add_argument("--csv", help="Load leads from CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Run without making actual calls")

    args = parser.parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                    🚀 SALES MACHINE                       ║
    ║              AI-Powered Calling System                    ║
    ║                                                           ║
    ║          Love - Loyalty - Honor - Everybody Eats          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Check for required env vars
    required_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
    missing = [v for v in required_vars if not os.environ.get(v)]

    if missing and not args.dry_run:
        print("⚠️  Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nSet these variables or use --dry-run for testing")
        return

    config = CampaignConfig(
        industry=args.industry,
        locations=args.locations
    )

    machine = SalesMachineOrchestrator(config)

    if not args.dry_run:
        machine.configure_dialer(
            twilio_sid=os.environ["TWILIO_ACCOUNT_SID"],
            twilio_token=os.environ["TWILIO_AUTH_TOKEN"],
            twilio_number=os.environ["TWILIO_PHONE_NUMBER"]
        )

    async def run():
        if args.csv:
            await machine.load_leads_from_csv(args.csv)
        else:
            await machine.load_leads_from_scraper()

        await machine.research_all_leads()

        if not args.dry_run:
            await machine.start_calling(max_calls=args.max_calls)
        else:
            print("\n🧪 DRY RUN - No calls made")
            machine._print_stats()

        machine.export_results()

    asyncio.run(run())


if __name__ == "__main__":
    main()
