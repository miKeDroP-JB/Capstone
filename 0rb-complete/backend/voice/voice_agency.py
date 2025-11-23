#!/usr/bin/env python3
"""
VOICE CALLING AGENCY SYSTEM
============================
Twilio + ElevenLabs integration for automated voice campaigns.
Community-first: 20% revenue share hardcoded.
"""
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path

# Twilio (install: pip install twilio)
# from twilio.rest import Client
# ElevenLabs (install: pip install elevenlabs)
# from elevenlabs import generate, set_api_key


@dataclass
class Campaign:
    """Voice campaign configuration"""
    id: str
    name: str
    script: str
    voice_id: str  # ElevenLabs voice ID
    target_list: List[str]  # Phone numbers
    status: str  # active, paused, completed
    created_at: datetime
    stats: Dict = None

    def __post_init__(self):
        if self.stats is None:
            self.stats = {
                "calls_made": 0,
                "calls_answered": 0,
                "conversions": 0,
                "revenue": 0.0
            }


@dataclass
class Call:
    """Individual call record"""
    id: str
    campaign_id: str
    phone_number: str
    status: str  # queued, calling, completed, failed
    answered: bool
    duration: int  # seconds
    recording_url: Optional[str]
    transcript: Optional[str]
    converted: bool
    revenue: float
    timestamp: datetime


class VoiceAgency:
    """
    Voice calling agency with Twilio + ElevenLabs.

    Features:
    - Campaign management
    - Automated calling
    - Performance tracking
    - Automatic follow-ups
    - 20% community revenue share (hardcoded)
    """

    def __init__(self):
        # Twilio credentials
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

        # ElevenLabs
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

        # Storage
        self.campaigns_file = Path("campaigns.json")
        self.calls_file = Path("calls.json")
        self.revenue_file = Path("revenue_splits.json")

        self.campaigns: Dict[str, Campaign] = self._load_campaigns()
        self.calls: List[Call] = self._load_calls()

        # Revenue split (HARDCODED - Everybody Eats)
        self.REVENUE_SPLIT = {
            "owner": 0.70,      # 70%
            "community": 0.20,   # 20% to community
            "sanctuary": 0.10    # 10% to sanctuary.ai
        }

        print("""
╔═══════════════════════════════════════════════════════════════╗
║            VOICE CALLING AGENCY - ONLINE                      ║
║                                                               ║
║  Twilio + ElevenLabs Integration                             ║
║  Community Share: 20% (hardcoded)                            ║
║  Sanctuary Share: 10% (hardcoded)                            ║
║                                                               ║
║  Love • Loyalty • Honor • Everybody Eats                     ║
╚═══════════════════════════════════════════════════════════════╝
""")

        if not all([self.twilio_account_sid, self.elevenlabs_key]):
            print("⚠️  API keys not configured. Set environment variables:")
            print("   - TWILIO_ACCOUNT_SID")
            print("   - TWILIO_AUTH_TOKEN")
            print("   - TWILIO_PHONE_NUMBER")
            print("   - ELEVENLABS_API_KEY")
            print("\n   Running in DEMO mode.\n")

    def _load_campaigns(self) -> Dict[str, Campaign]:
        """Load campaigns from disk"""
        if not self.campaigns_file.exists():
            return {}

        data = json.loads(self.campaigns_file.read_text())
        campaigns = {}
        for c_data in data:
            c_data["created_at"] = datetime.fromisoformat(c_data["created_at"])
            campaigns[c_data["id"]] = Campaign(**c_data)
        return campaigns

    def _save_campaigns(self):
        """Save campaigns to disk"""
        data = []
        for campaign in self.campaigns.values():
            c_dict = asdict(campaign)
            c_dict["created_at"] = campaign.created_at.isoformat()
            data.append(c_dict)

        self.campaigns_file.write_text(json.dumps(data, indent=2))

    def _load_calls(self) -> List[Call]:
        """Load call history"""
        if not self.calls_file.exists():
            return []

        data = json.loads(self.calls_file.read_text())
        calls = []
        for c_data in data:
            c_data["timestamp"] = datetime.fromisoformat(c_data["timestamp"])
            calls.append(Call(**c_data))
        return calls

    def _save_calls(self):
        """Save call history"""
        data = []
        for call in self.calls:
            c_dict = asdict(call)
            c_dict["timestamp"] = call.timestamp.isoformat()
            data.append(c_dict)

        self.calls_file.write_text(json.dumps(data, indent=2))

    def create_campaign(
        self,
        name: str,
        script: str,
        voice_id: str,
        target_list: List[str]
    ) -> Campaign:
        """Create a new campaign"""
        campaign = Campaign(
            id=f"CAMP-{int(datetime.now().timestamp())}",
            name=name,
            script=script,
            voice_id=voice_id,
            target_list=target_list,
            status="active",
            created_at=datetime.now()
        )

        self.campaigns[campaign.id] = campaign
        self._save_campaigns()

        print(f"✅ Campaign created: {campaign.id}")
        print(f"   Name: {name}")
        print(f"   Targets: {len(target_list)} numbers")
        print(f"   Status: {campaign.status}")

        return campaign

    async def make_call(
        self,
        campaign_id: str,
        phone_number: str
    ) -> Call:
        """
        Make a single call.

        In production:
        1. Generate audio with ElevenLabs
        2. Initiate call with Twilio
        3. Stream audio during call
        4. Record response
        5. Track outcome
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        call = Call(
            id=f"CALL-{int(datetime.now().timestamp())}",
            campaign_id=campaign_id,
            phone_number=phone_number,
            status="queued",
            answered=False,
            duration=0,
            recording_url=None,
            transcript=None,
            converted=False,
            revenue=0.0,
            timestamp=datetime.now()
        )

        print(f"📞 Making call: {call.id}")
        print(f"   Campaign: {campaign.name}")
        print(f"   To: {phone_number}")

        # DEMO MODE (no actual call)
        if not all([self.twilio_account_sid, self.elevenlabs_key]):
            print("   ⚠️  DEMO MODE - Simulating call...")
            await asyncio.sleep(2)

            # Simulate outcome
            import random
            call.status = "completed"
            call.answered = random.choice([True, False])

            if call.answered:
                call.duration = random.randint(30, 300)
                call.converted = random.choice([True, False])

                if call.converted:
                    call.revenue = random.uniform(100, 500)

            print(f"   Status: {call.status}")
            print(f"   Answered: {call.answered}")
            if call.answered:
                print(f"   Duration: {call.duration}s")
                print(f"   Converted: {call.converted}")
                if call.converted:
                    print(f"   Revenue: ${call.revenue:.2f}")

        else:
            # PRODUCTION MODE (real call)
            try:
                # 1. Generate audio with ElevenLabs
                # audio = generate(
                #     text=campaign.script,
                #     voice=campaign.voice_id,
                #     model="eleven_monolingual_v1"
                # )

                # 2. Make call with Twilio
                # client = Client(self.twilio_account_sid, self.twilio_auth_token)
                # twilio_call = client.calls.create(
                #     to=phone_number,
                #     from_=self.twilio_phone,
                #     url="https://your-twiml-url.com/voice"  # TwiML endpoint
                # )

                # call.status = twilio_call.status
                # Track call completion...
                pass

            except Exception as e:
                print(f"   ❌ Call failed: {e}")
                call.status = "failed"

        # Update campaign stats
        campaign.stats["calls_made"] += 1
        if call.answered:
            campaign.stats["calls_answered"] += 1
        if call.converted:
            campaign.stats["conversions"] += 1
            campaign.stats["revenue"] += call.revenue

        # Split revenue
        if call.revenue > 0:
            self._split_revenue(call.revenue, campaign_id)

        # Save
        self.calls.append(call)
        self._save_calls()
        self._save_campaigns()

        return call

    def _split_revenue(self, total: float, campaign_id: str):
        """Split revenue according to hardcoded percentages"""
        split = {
            "campaign_id": campaign_id,
            "total": total,
            "owner": total * self.REVENUE_SPLIT["owner"],
            "community": total * self.REVENUE_SPLIT["community"],
            "sanctuary": total * self.REVENUE_SPLIT["sanctuary"],
            "timestamp": datetime.now().isoformat()
        }

        # Load existing splits
        if self.revenue_file.exists():
            splits = json.loads(self.revenue_file.read_text())
        else:
            splits = []

        splits.append(split)
        self.revenue_file.write_text(json.dumps(splits, indent=2))

        print(f"💰 Revenue split: ${total:.2f}")
        print(f"   Owner (70%): ${split['owner']:.2f}")
        print(f"   Community (20%): ${split['community']:.2f}")
        print(f"   Sanctuary (10%): ${split['sanctuary']:.2f}")

    async def run_campaign(self, campaign_id: str):
        """Run entire campaign (call all targets)"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        if campaign.status != "active":
            print(f"⚠️  Campaign {campaign_id} is not active")
            return

        print(f"\n🚀 Running campaign: {campaign.name}")
        print(f"   Targets: {len(campaign.target_list)}")
        print()

        for phone in campaign.target_list:
            try:
                await self.make_call(campaign_id, phone)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"   ❌ Error calling {phone}: {e}")

        print(f"\n✅ Campaign complete: {campaign.name}")
        print(f"   Calls made: {campaign.stats['calls_made']}")
        print(f"   Answered: {campaign.stats['calls_answered']}")
        print(f"   Conversions: {campaign.stats['conversions']}")
        print(f"   Revenue: ${campaign.stats['revenue']:.2f}")

    def get_stats(self) -> Dict:
        """Get overall statistics"""
        total_calls = len(self.calls)
        answered = sum(1 for c in self.calls if c.answered)
        converted = sum(1 for c in self.calls if c.converted)
        total_revenue = sum(c.revenue for c in self.calls)

        community_total = total_revenue * self.REVENUE_SPLIT["community"]
        sanctuary_total = total_revenue * self.REVENUE_SPLIT["sanctuary"]

        return {
            "campaigns": len(self.campaigns),
            "total_calls": total_calls,
            "answered": answered,
            "answer_rate": answered / total_calls if total_calls > 0 else 0,
            "conversions": converted,
            "conversion_rate": converted / answered if answered > 0 else 0,
            "total_revenue": total_revenue,
            "community_share": community_total,
            "sanctuary_share": sanctuary_total,
            "revenue_split": self.REVENUE_SPLIT
        }


# =============================================================================
# DEMO
# =============================================================================

async def demo():
    """Demo the voice agency"""

    print("""
╔═══════════════════════════════════════════════════════════════╗
║              VOICE AGENCY - DEMO                              ║
╚═══════════════════════════════════════════════════════════════╝
""")

    agency = VoiceAgency()

    # Create campaign
    campaign = agency.create_campaign(
        name="HVAC Leads - November",
        script="Hi, this is Alex from Elite HVAC Solutions. We help businesses save 30-40% on HVAC costs with zero upfront investment. Do you have a minute to hear how?",
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
        target_list=[
            "+1-555-0101",
            "+1-555-0102",
            "+1-555-0103",
            "+1-555-0104",
            "+1-555-0105"
        ]
    )

    print("\n" + "="*60 + "\n")

    # Run campaign
    await agency.run_campaign(campaign.id)

    print("\n" + "="*60)
    print("OVERALL STATISTICS")
    print("="*60)

    stats = agency.get_stats()
    print(f"""
Campaigns: {stats['campaigns']}
Total Calls: {stats['total_calls']}
Answer Rate: {stats['answer_rate']:.1%}
Conversions: {stats['conversions']}
Conversion Rate: {stats['conversion_rate']:.1%}

Revenue Generated: ${stats['total_revenue']:.2f}
Community Share (20%): ${stats['community_share']:.2f}
Sanctuary Share (10%): ${stats['sanctuary_share']:.2f}

💝 Everybody Eats! 30% of revenue goes to community + sanctuary.
""")


if __name__ == "__main__":
    asyncio.run(demo())
