#!/usr/bin/env python3
"""
LIVE CALLING ASSISTANT - Make Real Calls RIGHT NOW
===================================================
Guides you through making real calls to real businesses.

Shows you:
- Who to call next
- What to say (word-for-word scripts)
- How to handle objections
- How to close
- How to collect payment

Tracks everything in real-time.

Love • Loyalty • Honor • Everybody Eats
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class LiveCallingAssistant:
    """Assists with making real calls"""

    def __init__(self):
        self.data_dir = Path("live_calls")
        self.data_dir.mkdir(exist_ok=True)

        self.calls_file = self.data_dir / "call_log.json"
        self.calls = self._load_calls()

        self.session_file = self.data_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.session = {
            "start_time": datetime.now().isoformat(),
            "calls_made": 0,
            "calls_closed": 0,
            "revenue": 0,
            "calls": []
        }

    def _load_calls(self) -> List[Dict]:
        """Load call history"""
        if self.calls_file.exists():
            with open(self.calls_file) as f:
                return json.load(f)
        return []

    def _save_calls(self):
        """Save calls"""
        with open(self.calls_file, 'w') as f:
            json.dump(self.calls, f, indent=2)

        with open(self.session_file, 'w') as f:
            json.dump(self.session, f, indent=2)

    def start_session(self, businesses: List[Dict]):
        """Start calling session"""
        print(f"\n{'='*60}")
        print("🚀 LIVE CALLING SESSION")
        print(f"{'='*60}")
        print(f"Targets: {len(businesses)} businesses")
        print(f"Goal: Close 30%+ ({int(len(businesses) * 0.3)}+ closes)")
        print()

        for i, business in enumerate(businesses, 1):
            print(f"\n{'='*60}")
            print(f"CALL #{i}/{len(businesses)}")
            print(f"{'='*60}\n")

            result = self.make_call(business)

            if result:
                self.session["calls"].append(result)
                self.session["calls_made"] += 1

                if result["outcome"] in ["closed", "interested"]:
                    self.session["calls_closed"] += 1
                    self.session["revenue"] += result.get("deal_value", 0)

                self._save_calls()

                # Show progress
                close_rate = (self.session["calls_closed"] / self.session["calls_made"] * 100) if self.session["calls_made"] > 0 else 0

                print(f"\n{'='*60}")
                print(f"SESSION PROGRESS")
                print(f"{'='*60}")
                print(f"Calls made: {self.session['calls_made']}")
                print(f"Closed: {self.session['calls_closed']}")
                print(f"Close rate: {close_rate:.0f}%")
                print(f"Revenue: ${self.session['revenue']:,}")
                print()

                # Ask if they want to continue
                if i < len(businesses):
                    cont = input("Continue to next call? (y/n): ").strip().lower()
                    if cont != 'y':
                        print(f"\n✓ Stopping session after {i} calls")
                        break

        # Final summary
        self.print_session_summary()

    def make_call(self, business: Dict) -> Optional[Dict]:
        """Make a single call"""

        print(f"📞 CALLING: {business['company_name']}")
        print(f"   Phone: {business['phone']}")
        print(f"   Address: {business.get('address', 'N/A')}")
        print(f"   Website: {business.get('website', 'NONE')}")
        print()

        # Show what to say
        print(f"{'='*60}")
        print("SCRIPT - SAY THIS:")
        print(f"{'='*60}\n")

        print('💬 OPENING (First 15 seconds):')
        print()
        print('   "Hi, this is [YOUR NAME]. I help HVAC companies like yours')
        print('   get 20-30% more customers using AI automation - with zero')
        print('   upfront cost. You only pay if it works. Do you have 60 seconds?"')
        print()

        # Wait for user to make the call
        input("Press ENTER when you've dialed and are ready to talk...")

        # Track the call
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "business": business,
            "outcome": None,
            "need_discovered": None,
            "solution_offered": None,
            "deal_value": 0,
            "notes": ""
        }

        print()
        print("📝 WHAT HAPPENED?")
        print()
        print("1. No answer / Voicemail")
        print("2. Not interested / Hung up")
        print("3. Interested / Wants to hear more")
        print("4. CLOSED / Ready to move forward")
        print()

        outcome_choice = input("Select outcome (1-4): ").strip()

        if outcome_choice == "1":
            call_record["outcome"] = "no_answer"
            print("\n✓ Logged as no answer. Try calling back later.")

        elif outcome_choice == "2":
            call_record["outcome"] = "not_interested"
            notes = input("Any notes? (objection, reason, etc.): ")
            call_record["notes"] = notes
            print("\n✓ Logged as not interested. Next!")

        elif outcome_choice == "3":
            call_record["outcome"] = "interested"
            print("\n🎯 THEY'RE INTERESTED!")
            print()
            print("ASK DISCOVERY QUESTIONS:")
            print()
            print('Q1: "What\'s your biggest challenge with getting new customers?"')
            print('Q2: "How are you currently handling bookings?"')
            print('Q3: "What takes up most of your time that you wish was automated?"')
            print()

            need = input("What need did you discover? ")
            call_record["need_discovered"] = need

            print()
            print("OFFER SOLUTION:")
            print()
            print(f'   "Perfect! I can build you a [{need.upper()} SOLUTION]')
            print(f'   in about [3-4 HOURS].')
            print()
            print('   "Here\'s the deal - normally this costs $3,000-5,000, but I')
            print('   have a better model: I build it FREE. You pay nothing upfront.')
            print('   Then I get 20% of what it makes you. You keep 80%."')
            print()
            print('   "Fair?"')
            print()

            ready = input("Did they agree to move forward? (y/n): ").strip().lower()

            if ready == 'y':
                call_record["outcome"] = "closed"
                call_record["solution_offered"] = f"{need} solution"
                call_record["deal_value"] = 3000  # Conservative estimate
                print("\n🎉 CLOSED! Great job!")
            else:
                follow_up = input("Schedule follow-up? (y/n): ").strip().lower()
                if follow_up == 'y':
                    call_record["outcome"] = "follow_up_scheduled"
                    date = input("Follow-up date: ")
                    call_record["notes"] = f"Follow-up: {date}"

        elif outcome_choice == "4":
            call_record["outcome"] = "closed"
            print("\n🎉 AWESOME! You closed the deal!")
            print()

            need = input("What solution did you offer? ")
            call_record["solution_offered"] = need

            value = input("Deal value? (press enter for $3000): ").strip()
            call_record["deal_value"] = int(value) if value else 3000

            print()
            print("NEXT STEPS TO COLLECT PAYMENT:")
            print()
            print("1. Send Stripe payment link (if charging setup fee)")
            print("2. Or send agreement (for performance-based)")
            print("3. Get their email")
            print("4. Onboard them into the system")
            print()

            email = input("Their email: ").strip()
            call_record["email"] = email

            print(f"\n✓ Email saved: {email}")
            print(f"✓ Deal value: ${call_record['deal_value']:,}")

        # Save
        self.calls.append(call_record)
        return call_record

    def print_session_summary(self):
        """Print session summary"""
        print(f"\n{'='*60}")
        print("📊 SESSION SUMMARY")
        print(f"{'='*60}\n")

        print(f"Total calls: {self.session['calls_made']}")
        print(f"Closed deals: {self.session['calls_closed']}")
        print(f"Close rate: {(self.session['calls_closed'] / self.session['calls_made'] * 100) if self.session['calls_made'] > 0 else 0:.0f}%")
        print(f"Total revenue: ${self.session['revenue']:,}")
        print(f"Your cut (20%): ${self.session['revenue'] * 0.20:,.0f}")
        print()

        # Breakdown
        print("OUTCOMES:")
        outcomes = {}
        for call in self.session['calls']:
            outcome = call['outcome']
            outcomes[outcome] = outcomes.get(outcome, 0) + 1

        for outcome, count in outcomes.items():
            print(f"  {outcome}: {count}")

        print()
        print(f"✓ Session saved: {self.session_file}")
        print()

        if self.session['calls_closed'] > 0:
            print("🎉 NEXT STEPS:")
            print("1. Send payment links / agreements to closed deals")
            print("2. Onboard them into client management system")
            print("3. Build and deliver their solutions")
            print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Live Calling Assistant")
    parser.add_argument("--businesses", type=str, help="Path to businesses JSON file")
    parser.add_argument("--demo", action="store_true", help="Run demo")

    args = parser.parse_args()

    assistant = LiveCallingAssistant()

    if args.businesses:
        with open(args.businesses) as f:
            businesses = json.load(f)

        assistant.start_session(businesses)

    elif args.demo:
        # Demo with fake business
        demo_businesses = [
            {
                "company_name": "ABC HVAC Company",
                "phone": "555-1234",
                "address": "123 Main St, Tampa FL",
                "website": "NONE",
                "needs": ["website", "online booking"]
            }
        ]

        assistant.start_session(demo_businesses)

    else:
        print("Live Calling Assistant")
        print("\nUsage:")
        print("  python live_calling_assistant.py --businesses real_businesses/ready_to_call_xxx.json")
        print("  python live_calling_assistant.py --demo")
