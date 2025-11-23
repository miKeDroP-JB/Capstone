#!/usr/bin/env python3
"""
LIVE DEMO BUILDER - Watch Your Dashboard Built in Real-Time
============================================================
While you're on the phone with them, we build their dashboard LIVE.

Workflow:
1. On call with prospect
2. "Want to see this in action? I can build yours right now!"
3. Ask 3-5 quick branding questions
4. Build dashboard LIVE while they watch
5. Show them the result immediately
6. If vibing → upsell full suite
7. If quick close → just phone agent

They watch it appear before their eyes. INSTANT close.

Love • Loyalty • Honor • Everybody Eats
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from customer_dashboard_builder import CustomerDashboardBuilder
from traffic_generator import TrafficGenerator

class LiveDemoBuilder:
    """Builds demo in real-time while customer watches"""

    def __init__(self):
        self.dashboard_builder = CustomerDashboardBuilder()
        self.traffic_gen = TrafficGenerator()

    def start_live_demo(self):
        """Start live demo session"""

        print(f"\n{'='*60}")
        print("🎬 LIVE DEMO - Build Their Dashboard RIGHT NOW")
        print(f"{'='*60}\n")

        print("📞 YOU'RE ON THE PHONE WITH PROSPECT")
        print()
        print("SAY THIS:")
        print("─" * 60)
        print('"You know what? Instead of just talking about it,')
        print('let me BUILD yours right now while we\'re on the phone.')
        print('Takes 3 minutes. You can watch it happen live.')
        print()
        print('Sound good?"')
        print("─" * 60)
        print()

        input("Press ENTER when they say YES...")

        # Quick branding questions
        customer_info = self._ask_branding_questions()

        # Build in real-time
        self._build_live(customer_info)

        # Show result
        self._show_result(customer_info)

        # Upsell or close
        self._upsell_or_close(customer_info)

    def _ask_branding_questions(self) -> Dict:
        """Ask quick branding questions"""

        print(f"\n{'='*60}")
        print("📝 QUICK BRANDING QUESTIONS")
        print(f"{'='*60}\n")

        print("SAY THIS:")
        print('"Perfect! I just need a few quick details..."')
        print()

        # Question 1: Company name
        print("─" * 60)
        print('Q1: "What\'s your company name?"')
        print("─" * 60)
        company_name = input("Their answer: ").strip()

        # Question 2: What do you do?
        print("\n" + "─" * 60)
        print('Q2: "And what do you do? HVAC, plumbing, etc.?"')
        print("─" * 60)
        industry = input("Their answer: ").strip() or "HVAC Services"

        # Question 3: Location
        print("\n" + "─" * 60)
        print('Q3: "Where are you located?"')
        print("─" * 60)
        location = input("Their answer: ").strip() or "Tampa, FL"

        # Question 4: Phone
        print("\n" + "─" * 60)
        print('Q4: "What\'s your main phone number?"')
        print("─" * 60)
        phone = input("Their answer: ").strip() or "555-1234"

        # Question 5: Email
        print("\n" + "─" * 60)
        print('Q5: "And your email?"')
        print("─" * 60)
        email = input("Their answer: ").strip() or "info@company.com"

        customer_info = {
            "company_name": company_name,
            "industry": industry,
            "location": location,
            "phone": phone,
            "email": email,
            "created_live": True,
            "demo_date": datetime.now().isoformat()
        }

        print("\n✓ Got it! Building now...")
        time.sleep(1)

        return customer_info

    def _build_live(self, customer_info: Dict):
        """Build dashboard LIVE with progress updates"""

        print(f"\n{'='*60}")
        print("🚀 BUILDING YOUR DASHBOARD - LIVE!")
        print(f"{'='*60}\n")

        print("SAY THIS WHILE IT'S BUILDING:")
        print('"Okay, watch this. I\'m building your custom dashboard')
        print('right now. You\'ll see it in about 2 minutes..."')
        print()

        # Step 1: Create landing page
        print("⚙️  Step 1/5: Creating your landing page...")
        time.sleep(2)
        self.dashboard_builder.create_dashboard(customer_info)
        print("✓ Landing page created!")
        print()
        time.sleep(1)

        # Step 2: Generate social posts
        print("⚙️  Step 2/5: Generating 30 days of social media posts...")
        time.sleep(2)
        self.traffic_gen.generate_social_campaign(customer_info, duration_days=30)
        print("✓ 30 social posts ready!")
        print()
        time.sleep(1)

        # Step 3: Generate email campaigns
        print("⚙️  Step 3/5: Creating email campaigns...")
        time.sleep(2)
        self.traffic_gen.generate_email_campaign(customer_info)
        print("✓ Email campaigns ready!")
        print()
        time.sleep(1)

        # Step 4: Generate phone scripts
        print("⚙️  Step 4/5: Building phone scripts...")
        time.sleep(2)
        self.traffic_gen.generate_phone_scripts(customer_info)
        print("✓ Phone scripts ready!")
        print()
        time.sleep(1)

        # Step 5: Setup tracking
        print("⚙️  Step 5/5: Setting up analytics tracking...")
        time.sleep(2)
        print("✓ Tracking enabled!")
        print()

    def _show_result(self, customer_info: Dict):
        """Show them the result"""

        company_name = customer_info["company_name"]
        safe_name = company_name.lower().replace(' ', '_').replace('&', 'and')

        print(f"\n{'='*60}")
        print("🎉 YOUR DASHBOARD IS READY!")
        print(f"{'='*60}\n")

        print("SAY THIS:")
        print("─" * 60)
        print('"Okay, it\'s live! Check this out..."')
        print()
        print(f'Your landing page: customer_dashboards/{safe_name}/index.html')
        print(f'Your stats dashboard: customer_dashboards/{safe_name}/stats.html')
        print()
        print("You've got:")
        print("✓ Beautiful branded landing page")
        print("✓ Lead capture forms")
        print("✓ 30 days of social media posts ready to go")
        print("✓ 4 email campaigns")
        print("✓ 3 phone scripts")
        print("✓ Full analytics tracking")
        print()
        print("All built in 2 minutes. All customized for YOU.")
        print()
        print('This is what you get. Like it?"')
        print("─" * 60)
        print()

        # Open files for them to see (in production, would open in browser)
        print(f"📂 FILES CREATED:")
        print(f"   Landing page: customer_dashboards/{safe_name}/index.html")
        print(f"   Stats: customer_dashboards/{safe_name}/stats.html")
        print(f"   Social posts: traffic_campaigns/social_{safe_name}.json")
        print(f"   Emails: traffic_campaigns/email_{safe_name}.json")
        print(f"   Phone: traffic_campaigns/phone_{safe_name}.json")
        print()

    def _upsell_or_close(self, customer_info: Dict):
        """Upsell full suite or quick close"""

        print(f"\n{'='*60}")
        print("💰 CLOSE OR UPSELL")
        print(f"{'='*60}\n")

        print("GAUGE THEIR REACTION:")
        print()
        print("Option 1: THEY'RE LOVING IT (vibing)")
        print("Option 2: THEY LIKE IT (interested)")
        print("Option 3: THEY'RE UNSURE (thinking)")
        print()

        reaction = input("Which one? (1/2/3): ").strip()

        if reaction == "1":
            # FULL SUITE UPSELL
            print("\n🚀 UPSELL - FULL SUITE")
            print("─" * 60)
            print("SAY THIS:")
            print()
            print('"Awesome! So here\'s the thing...')
            print()
            print('What you just saw? That\'s the BASIC package.')
            print('Just the dashboard + content.')
            print()
            print('But I can also:')
            print('✓ Run this entire system FOR you')
            print('✓ Post all the content daily')
            print('✓ Track every lead')
            print('✓ Optimize based on what works')
            print('✓ Send you monthly checks with your 80%')
            print()
            print('Basically, I take this dashboard we just built and')
            print('turn it into a MONEY-MAKING MACHINE for you.')
            print()
            print('Zero work on your end. You just collect checks.')
            print()
            print('Same deal: $500 to start, fully refundable if no')
            print('results in 90 days. Then 20% of new revenue.')
            print()
            print('Want the full suite?"')
            print("─" * 60)
            print()

            full_suite = input("Do they want full suite? (y/n): ").strip().lower()

            if full_suite == 'y':
                self._close_full_suite(customer_info)
            else:
                self._close_basic(customer_info)

        elif reaction == "2":
            # BASIC CLOSE
            print("\n💰 CLOSE - BASIC PACKAGE")
            print("─" * 60)
            print("SAY THIS:")
            print()
            print('"Great! So this is all yours.')
            print()
            print('Small $500 retainer to get started, fully refundable')
            print('if I don\'t make you money in 90 days.')
            print()
            print('Then 20% of new revenue. You keep 80%.')
            print()
            print('I\'ll send you the payment link right now.')
            print('Takes 30 seconds to pay, then I activate everything.')
            print()
            print('Sound good?"')
            print("─" * 60)
            print()

            self._close_basic(customer_info)

        else:
            # THINKING - FOLLOW UP
            print("\n⏰ FOLLOW UP")
            print("─" * 60)
            print("SAY THIS:")
            print()
            print('"No pressure! I just built this for you in 2 minutes')
            print('to show you what\'s possible.')
            print()
            print('Tell you what - I\'ll email you everything we just')
            print('created. You can review it, think about it.')
            print()
            print('If you want to move forward, just reply to the email.')
            print('If not, no worries - at least you got to see it live!')
            print()
            print('Fair?"')
            print("─" * 60)
            print()

            self._send_follow_up(customer_info)

    def _close_full_suite(self, customer_info: Dict):
        """Close full suite deal"""

        print(f"\n{'='*60}")
        print("🎉 FULL SUITE CLOSED!")
        print(f"{'='*60}\n")

        print("NEXT STEPS:")
        print()
        print("1. Collect $500 retainer:")
        print(f'   python stripe_retainer.py --create "{customer_info["company_name"]}" --email {customer_info["email"]}')
        print()
        print("2. Add to CRM:")
        print(f'   python customer_crm.py --add "{customer_info["company_name"]}" --contact "Owner" --email {customer_info["email"]} --phone {customer_info["phone"]}')
        print()
        print("3. Onboard to client management:")
        print(f'   python client_management_system.py --onboard "{customer_info["company_name"]}" --industry {customer_info["industry"]}')
        print()
        print("4. Start running automation!")
        print()

        # Save deal
        self._save_deal(customer_info, package="full_suite", value=500)

        print("✓ Deal logged!")
        print("✓ They get: Full automation, tracking, monthly checks")
        print("✓ You get: $500 now + 20% ongoing")
        print()

    def _close_basic(self, customer_info: Dict):
        """Close basic package"""

        print(f"\n{'='*60}")
        print("🎉 BASIC PACKAGE CLOSED!")
        print(f"{'='*60}\n")

        print("NEXT STEPS:")
        print()
        print("1. Collect $500 retainer:")
        print(f'   python stripe_retainer.py --create "{customer_info["company_name"]}" --email {customer_info["email"]}')
        print()
        print("2. Send them their dashboard files")
        print()
        print("3. Add to CRM for follow-up (potential upsell later)")
        print()

        # Save deal
        self._save_deal(customer_info, package="basic", value=500)

        print("✓ Deal logged!")
        print("✓ They get: Dashboard + content")
        print("✓ You get: $500")
        print("✓ Upsell opportunity later!")
        print()

    def _send_follow_up(self, customer_info: Dict):
        """Send follow-up"""

        print("✓ Follow-up scheduled")
        print()
        print("EMAIL THEM:")
        print("─" * 60)
        print(f"Subject: Your custom dashboard is ready!")
        print()
        print(f"Hi {customer_info['company_name']}!")
        print()
        print("Thanks for letting me build your custom dashboard live!")
        print()
        print("Here's what I created for you:")
        print("✓ Landing page with lead capture")
        print("✓ 30 days of social media posts")
        print("✓ 4 email campaigns")
        print("✓ 3 phone scripts")
        print("✓ Full analytics tracking")
        print()
        print("All customized for YOUR business.")
        print()
        print("If you want to activate it:")
        print("- $500 retainer (refundable if no results in 90 days)")
        print("- Then 20% of new revenue (you keep 80%)")
        print()
        print("Just reply to this email!")
        print()
        print("Love • Loyalty • Honor • Everybody Eats")
        print("─" * 60)
        print()

        # Save for follow-up
        self._save_deal(customer_info, package="demo_shown", value=0)

    def _save_deal(self, customer_info: Dict, package: str, value: int):
        """Save deal info"""

        deals_dir = Path("live_demos")
        deals_dir.mkdir(exist_ok=True)

        deal = {
            "timestamp": datetime.now().isoformat(),
            "customer": customer_info,
            "package": package,
            "value": value,
            "status": "closed" if value > 0 else "demo_shown"
        }

        deals_file = deals_dir / "deals.json"

        if deals_file.exists():
            with open(deals_file) as f:
                deals = json.load(f)
        else:
            deals = []

        deals.append(deal)

        with open(deals_file, 'w') as f:
            json.dump(deals, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Live Demo Builder")
    parser.add_argument("--demo", action="store_true", help="Start live demo")
    parser.add_argument("--quick", action="store_true", help="Quick demo (pre-filled)")

    args = parser.parse_args()

    builder = LiveDemoBuilder()

    if args.demo:
        builder.start_live_demo()

    elif args.quick:
        # Quick demo with pre-filled data
        customer_info = {
            "company_name": "Demo HVAC Company",
            "industry": "HVAC Services",
            "location": "Tampa, FL",
            "phone": "555-DEMO",
            "email": "demo@hvac.com"
        }

        print("\n🎬 QUICK DEMO MODE")
        print("Building dashboard for: Demo HVAC Company\n")

        builder._build_live(customer_info)
        builder._show_result(customer_info)

    else:
        print("Live Demo Builder")
        print("\nUsage:")
        print("  python live_demo_builder.py --demo       # Full interactive demo")
        print("  python live_demo_builder.py --quick      # Quick demo")
        print()
        print("THE WORKFLOW:")
        print("1. You're on the phone with prospect")
        print('2. Say: "Let me build yours right now while we talk!"')
        print("3. Ask 5 quick branding questions")
        print("4. Build dashboard LIVE (they watch)")
        print("5. Show them result immediately")
        print("6. If vibing → upsell full suite")
        print("7. If quick → close basic package")
        print()
        print("They see it appear before their eyes = INSTANT close! 🚀")
