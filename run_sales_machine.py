#!/usr/bin/env python3
"""
🚀 SALES MACHINE - Quick Run Script
====================================
The fastest way to get your AI sales team calling.

SETUP:
------
1. Set environment variables:
   export TWILIO_ACCOUNT_SID="AC..."
   export TWILIO_AUTH_TOKEN="..."
   export TWILIO_PHONE_NUMBER="+1234567890"
   export ELEVENLABS_API_KEY="..."  (optional)
   export DEEPGRAM_API_KEY="..."    (optional)

2. Run:
   python run_sales_machine.py

Or use demo mode (no real calls):
   python run_sales_machine.py --demo

Love - Loyalty - Honor - Everybody Eats
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from sales_machine import SalesMachineOrchestrator, CampaignConfig


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   ███████╗ █████╗ ██╗     ███████╗███████╗    ███╗   ███╗             ║
║   ██╔════╝██╔══██╗██║     ██╔════╝██╔════╝    ████╗ ████║             ║
║   ███████╗███████║██║     █████╗  ███████╗    ██╔████╔██║             ║
║   ╚════██║██╔══██║██║     ██╔══╝  ╚════██║    ██║╚██╔╝██║             ║
║   ███████║██║  ██║███████╗███████╗███████║    ██║ ╚═╝ ██║             ║
║   ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═╝     ╚═╝             ║
║                                                                       ║
║                   🔥 AI-POWERED CALLING SYSTEM 🔥                     ║
║                                                                       ║
║              Love - Loyalty - Honor - Everybody Eats                  ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)


async def run_demo():
    """Run in demo mode - no real calls, just testing the pipeline"""
    print("\n🧪 DEMO MODE - No real calls will be made\n")

    # Demo leads
    demo_leads = [
        {
            "business_name": "Cool Air HVAC",
            "phone": "+1555000001",
            "email": "info@coolair.com",
            "source": "demo"
        },
        {
            "business_name": "Texas Heat Solutions",
            "phone": "+1555000002",
            "email": "contact@texasheat.com",
            "source": "demo"
        },
        {
            "business_name": "Comfort Zone AC",
            "phone": "+1555000003",
            "email": "sales@comfortzone.com",
            "source": "demo"
        },
        {
            "business_name": "Arctic Air Systems",
            "phone": "+1555000004",
            "email": "info@arcticair.com",
            "source": "demo"
        },
        {
            "business_name": "Gulf Coast Cooling",
            "phone": "+1555000005",
            "email": "service@gulfcoast.com",
            "source": "demo"
        }
    ]

    config = CampaignConfig(
        name="HVAC AI Demo Campaign",
        industry="hvac",
        locations=["Houston, TX"]
    )

    machine = SalesMachineOrchestrator(config)

    # Load demo leads
    await machine.load_leads_from_list(demo_leads)

    # Show what would happen
    print("📋 Loaded leads:")
    for lead in demo_leads:
        print(f"   • {lead['business_name']} - {lead['phone']}")

    print("\n🔬 In production mode, we would:")
    print("   1. Research each business (SEO, competitors, pain points)")
    print("   2. Generate custom talking points")
    print("   3. Call each lead with AI conversation")
    print("   4. Handle objections in real-time")
    print("   5. Book appointments or close sales")
    print("   6. Track commissions (10% model)")

    # Simulate stats
    print("\n📊 Simulated campaign stats:")
    print("=" * 40)
    print(f"   Total Leads:      {len(demo_leads)}")
    print(f"   Expected Connect: ~60%")
    print(f"   Expected Convert: ~15%")
    print(f"   Projected Appts:  ~{int(len(demo_leads) * 0.15)}")
    print("=" * 40)

    print("\n✅ Demo complete! Set env vars and run without --demo to go live.")


async def run_production(locations: list, max_calls: int, source: str, csv_path: str = None):
    """Run production campaign"""

    # Verify required env vars
    required = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
    missing = [v for v in required if not os.environ.get(v)]

    if missing:
        print("❌ Missing required environment variables:")
        for v in missing:
            print(f"   • {v}")
        print("\nSet these and try again:")
        print('   export TWILIO_ACCOUNT_SID="AC..."')
        print('   export TWILIO_AUTH_TOKEN="..."')
        print('   export TWILIO_PHONE_NUMBER="+1..."')
        return

    config = CampaignConfig(
        name="HVAC AI Campaign",
        industry="hvac",
        locations=locations,
        calls_per_hour=30,
        max_concurrent_calls=3
    )

    machine = SalesMachineOrchestrator(config)

    # Configure dialer
    machine.configure_dialer(
        twilio_sid=os.environ["TWILIO_ACCOUNT_SID"],
        twilio_token=os.environ["TWILIO_AUTH_TOKEN"],
        twilio_number=os.environ["TWILIO_PHONE_NUMBER"]
    )

    # Configure voice if keys available
    if os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("DEEPGRAM_API_KEY"):
        machine.configure_voice(
            api_keys={
                "elevenlabs": os.environ.get("ELEVENLABS_API_KEY"),
                "deepgram": os.environ.get("DEEPGRAM_API_KEY")
            }
        )

    # Set up callbacks
    async def on_appointment(lead, details):
        print(f"\n🎯 APPOINTMENT SET: {lead.business_name}")
        print(f"   Details: {details}\n")

    async def on_sale(lead, amount, commission):
        print(f"\n💰 SALE CLOSED: {lead.business_name}")
        print(f"   Amount: ${amount:,.2f}")
        print(f"   Commission: ${commission:,.2f}\n")

    machine.set_callbacks(
        on_appointment=on_appointment,
        on_sale=on_sale
    )

    # Run campaign
    await machine.run_campaign(
        leads_source=source,
        csv_path=csv_path,
        max_calls=max_calls,
        do_research=True
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="🚀 Sales Machine - AI Calling System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_sales_machine.py --demo
  python run_sales_machine.py --locations "Houston, TX" "Dallas, TX"
  python run_sales_machine.py --csv leads.csv --max-calls 100
        """
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (no real calls)"
    )

    parser.add_argument(
        "--locations",
        nargs="+",
        default=["Houston, TX"],
        help="Locations to scrape for leads"
    )

    parser.add_argument(
        "--max-calls",
        type=int,
        default=50,
        help="Maximum number of calls to make"
    )

    parser.add_argument(
        "--csv",
        help="Load leads from CSV file instead of scraping"
    )

    args = parser.parse_args()

    print_banner()

    if args.demo:
        asyncio.run(run_demo())
    else:
        source = "csv" if args.csv else "scrape"
        asyncio.run(run_production(
            locations=args.locations,
            max_calls=args.max_calls,
            source=source,
            csv_path=args.csv
        ))


if __name__ == "__main__":
    main()
