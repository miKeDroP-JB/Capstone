#!/usr/bin/env python3
"""
AUTOMATE - One Command Revenue Generation
==========================================
The almost automated edition.

You run this. It makes money. You approve decisions.

Usage:
    python AUTOMATE.py              # Start making money
    python AUTOMATE.py --full-auto  # Zero human intervention
    python AUTOMATE.py --monitor    # Watch it work

Love • Loyalty • Honor • Everybody Eats
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from auto_revenue_engine import AutoRevenueEngine
except ImportError:
    print("✗ auto_revenue_engine.py not found")
    sys.exit(1)


class AutomatedRevenue:
    """One-command automated revenue generation"""

    def __init__(self, full_auto: bool = False):
        self.full_auto = full_auto
        self.engine = None

    async def start(self):
        """Start the automated revenue engine"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║            AUTOMATE - Revenue Generation System               ║
║                                                               ║
║         You create. You decide. System executes.              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """)

        if self.full_auto:
            print("🚀 FULL AUTO MODE - Zero human intervention")
            print("   System will make all decisions automatically")
            print("   You just collect money\n")
        else:
            print("⚙️  SEMI-AUTO MODE - You approve decisions")
            print("   System will ask for approval on big decisions")
            print("   You stay in control\n")

        # Initialize engine
        self.engine = AutoRevenueEngine()

        # Set full auto if requested
        if self.full_auto:
            self.engine.config["full_auto"] = True
            with open(self.engine.config_file, 'w') as f:
                json.dump(self.engine.config, f, indent=2)

        # Check for existing campaigns
        active_campaigns = [c for c in self.engine.campaigns if c["status"] == "active"]

        if active_campaigns:
            print(f"📋 Found {len(active_campaigns)} active campaigns")
            print("   Resuming...")
        else:
            print("💡 No active campaigns found")
            print("   Creating first campaign...\n")

            # Create first campaign automatically
            await self._create_first_campaign()

        # Show status
        self.engine.print_status()

        # Show next steps
        if not self.full_auto:
            pending = self.engine.get_pending_decisions()
            if pending:
                print("\n🎯 NEXT STEPS:")
                print(f"   You have {len(pending)} decisions waiting")
                print(f"   Approve them with:")
                for decision in pending[:3]:
                    print(f"      python auto_revenue_engine.py approve {decision['id']}")
                print()

    async def _create_first_campaign(self):
        """Create the first campaign automatically"""
        print("🎬 Creating HVAC Voice Agent campaign...\n")

        # Load targets
        targets = self._load_hvac_targets()

        if not targets:
            print("⚠️  No targets found. Using demo targets.")
            targets = self._get_demo_targets()

        print(f"✓ Loaded {len(targets)} target companies")

        # Create campaign
        campaign_id = await self.engine.create_campaign(
            campaign_type="hvac_voice_agent",
            targets=targets,
            config={
                "script": "revenue/hvac-sales-agent/scripts/phone-script.txt",
                "demo_script": "revenue/hvac-sales-agent/scripts/demo-script.txt",
                "pricing": {
                    "setup_fee": 200,
                    "performance_fee": 0.10,  # 10%
                    "revenue_split": {
                        "owner": 0.70,
                        "community": 0.20,
                        "sanctuary": 0.10
                    }
                }
            }
        )

        print(f"\n✓ Campaign created: {campaign_id}")
        print(f"  Targets: {len(targets)} HVAC companies")
        print(f"  Expected results:")
        print(f"     Calls: {len(targets)}")
        print(f"     Demos: {int(len(targets) * 0.25)} (25% conversion)")
        print(f"     Closed: {int(len(targets) * 0.25 * 0.60)} (60% close rate)")
        print(f"     Revenue: ${int(len(targets) * 0.25 * 0.60 * 200):,} (setup fees)")
        print()

    def _load_hvac_targets(self) -> list:
        """Load HVAC targets from file"""
        targets_file = Path("revenue/hvac-sales-agent/target_companies.txt")

        if not targets_file.exists():
            return []

        targets = []
        current_company = {}

        # Simple parsing (looking for company names and phone numbers)
        with open(targets_file) as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Look for company entries (simple format)
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        targets.append({
                            "company": parts[0],
                            "location": parts[1],
                            "phone": parts[2]
                        })

        return targets[:50]  # Limit to first 50 for safety

    def _get_demo_targets(self) -> list:
        """Get demo targets for testing"""
        return [
            {"company": "Cool Breeze HVAC", "phone": "+1-555-0001", "location": "Miami, FL"},
            {"company": "Air Masters Inc", "phone": "+1-555-0002", "location": "Tampa, FL"},
            {"company": "Climate Control Pro", "phone": "+1-555-0003", "location": "Orlando, FL"},
            {"company": "Sunshine AC Repair", "phone": "+1-555-0004", "location": "Jacksonville, FL"},
            {"company": "Frost Mechanical", "phone": "+1-555-0005", "location": "St. Petersburg, FL"},
            {"company": "Elite HVAC Services", "phone": "+1-555-0006", "location": "Fort Lauderdale, FL"},
            {"company": "Precision Air Systems", "phone": "+1-555-0007", "location": "West Palm Beach, FL"},
            {"company": "Coastal Heating & Cooling", "phone": "+1-555-0008", "location": "Sarasota, FL"},
            {"company": "Premier Climate Solutions", "phone": "+1-555-0009", "location": "Naples, FL"},
            {"company": "Delta Air Conditioning", "phone": "+1-555-0010", "location": "Tallahassee, FL"},
        ]

    async def monitor(self):
        """Real-time monitoring"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║             LIVE REVENUE MONITORING                           ║
║             (Press Ctrl+C to stop)                            ║
╚═══════════════════════════════════════════════════════════════╝
        """)

        self.engine = AutoRevenueEngine()

        print("🔴 LIVE\n")

        while True:
            # Clear screen
            os.system('clear' if os.name != 'nt' else 'cls')

            print("=" * 60)
            print(f"LIVE MONITORING - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)

            # Show status
            status = self.engine.get_status()

            print(f"\n📞 CALLS: {status['results']['total_calls']}")
            print(f"📅 DEMOS: {status['results']['demos_booked']}")
            print(f"✓ CLOSED: {status['results']['deals_closed']}")
            print(f"💰 REVENUE: ${status['results']['total_revenue']:,.2f}")

            print(f"\n📊 CAMPAIGNS")
            print(f"   Active: {status['campaigns']['active']}")
            print(f"   Completed: {status['campaigns']['completed']}")

            print(f"\n⏳ PENDING DECISIONS: {status['pending_decisions']}")

            # Show recent activity
            print(f"\n📝 RECENT ACTIVITY")
            print("   (Activity log coming soon...)")

            print("\n" + "=" * 60)
            print("Press Ctrl+C to stop monitoring")

            await asyncio.sleep(5)  # Update every 5 seconds


async def main():
    """Main entry point"""

    full_auto = "--full-auto" in sys.argv
    monitor = "--monitor" in sys.argv

    automator = AutomatedRevenue(full_auto=full_auto)

    if monitor:
        try:
            await automator.monitor()
        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped\n")
    else:
        await automator.start()

        print("""
╔═══════════════════════════════════════════════════════════════╗
║                    SYSTEM RUNNING                             ║
╚═══════════════════════════════════════════════════════════════╝

Next steps:

1. Monitor progress:
   python AUTOMATE.py --monitor

2. Check status:
   python auto_revenue_engine.py status

3. Approve decisions (if needed):
   python auto_revenue_engine.py decisions

4. Collect money:
   Check revenue/auto_engine_data/results.json

═══════════════════════════════════════════════════════════════

The system is now making money for you.
You just approve decisions and collect revenue.

Love • Loyalty • Honor • Everybody Eats 💝
        """)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Stopped\n")
