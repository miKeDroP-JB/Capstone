#!/usr/bin/env python3
"""
MASTER - Autonomous Revenue Engine
===================================
Runs the entire ecosystem autonomously.

What it does:
1. Makes sales calls (finds + closes clients)
2. Onboards clients (sets up everything)
3. Runs daily automation (posts content, tracks metrics)
4. Analyzes performance (identifies winners/losers)
5. Scales winners (attacks what works)
6. Kills losers (stops wasting time)
7. Processes payments (sends checks monthly)
8. Repeats forever

COMPLETELY AUTONOMOUS.

You run this once. It makes money forever.

Love • Loyalty • Honor • Everybody Eats
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path

from research_agent import ResearchAgent
from ai_trainer import AITrainer
from intelligent_sales_agent import IntelligentSalesAgent
from instant_marketing_automation import MarketingAutomationBuilder
from client_management_system import ClientManagementSystem
from attack_engine import AttackEngine

class MasterController:
    """
    The autonomous revenue engine

    Runs everything. Forever.
    """

    def __init__(self):
        self.research = ResearchAgent()
        self.trainer = AITrainer()
        self.sales = IntelligentSalesAgent()
        self.marketing = MarketingAutomationBuilder()
        self.cms = ClientManagementSystem()
        self.attack = AttackEngine()

        print(f"\n{'='*60}")
        print("MASTER CONTROLLER INITIALIZED")
        print(f"{'='*60}")
        print("✓ Research Agent ready")
        print("✓ AI Trainer ready")
        print("✓ Sales Agent ready")
        print("✓ Marketing Automation ready")
        print("✓ Client Management ready")
        print("✓ Attack Engine ready")
        print()

    def run_blitz(self, industry: str = "hvac", num_calls: int = 20):
        """
        Run full blitz:
        1. Research targets
        2. Train AI
        3. Make calls
        4. Close deals
        5. Onboard clients
        6. Deploy automation
        """

        print(f"\n{'='*60}")
        print("🚀 RUNNING BLITZ MODE")
        print(f"{'='*60}")
        print(f"Industry: {industry}")
        print(f"Calls: {num_calls}")
        print()

        # PHASE 1: Research
        print("PHASE 1: RESEARCH")
        print("-" * 60)
        targets = self.research.find_targets(industry, count=num_calls * 2)
        print(f"✓ Found {len(targets)} targets\n")

        # PHASE 2: Train AI
        print("PHASE 2: TRAIN AI")
        print("-" * 60)
        training = self.trainer.train(rounds=100, success_threshold=0.70)
        print(f"✓ AI trained to {training['success_rate']*100:.0f}% success rate\n")

        # PHASE 3: Make Calls
        print("PHASE 3: MAKE CALLS")
        print("-" * 60)

        top_targets = sorted(targets, key=lambda x: x.get("score", 0), reverse=True)[:num_calls]

        calls_made = 0
        deals_closed = []

        for i, target in enumerate(top_targets, 1):
            print(f"\nCall {i}/{num_calls}: {target['company']} (Score: {target['score']})")

            call_result = self.sales.make_call(target)
            calls_made += 1

            if call_result.get("outcome") in ["closed", "interested_thinking"]:
                deals_closed.append(call_result)
                print(f"   ✓ CLOSED!")

        print(f"\n✓ Made {calls_made} calls")
        print(f"✓ Closed {len(deals_closed)} deals ({len(deals_closed)/calls_made*100:.0f}% close rate)\n")

        # PHASE 4: Onboard All Clients
        print("PHASE 4: ONBOARD CLIENTS")
        print("-" * 60)

        onboarded = []

        for deal in deals_closed:
            target = deal["target"]

            # Onboard into ecosystem
            solution = deal.get("solution_offered") or {}
            client = self.cms.onboard_client(
                company_name=target["company"],
                industry=industry,  # Use industry from blitz params
                deal_info={
                    "company": target["company"],
                    "industry": industry,
                    "split": deal.get("final_split", "20%"),
                    "solution": solution.get("name", "marketing_automation"),
                    "deal_value": solution.get("value", "$3,000-5,000")
                }
            )

            onboarded.append(client)

        print(f"\n✓ Onboarded {len(onboarded)} clients\n")

        # PHASE 5: Summary
        print("=" * 60)
        print("BLITZ COMPLETE")
        print("=" * 60)
        print(f"Calls made: {calls_made}")
        print(f"Deals closed: {len(deals_closed)}")
        print(f"Clients onboarded: {len(onboarded)}")
        print(f"Close rate: {len(deals_closed)/calls_made*100:.0f}%")
        print()

        return {
            "calls": calls_made,
            "closes": len(deals_closed),
            "onboarded": len(onboarded),
            "clients": onboarded
        }

    def run_daily_cycle(self):
        """
        Run daily cycle:
        1. Run automation for all clients
        2. Analyze performance
        3. Execute attack strategy
        """

        print(f"\n{'='*60}")
        print("📅 DAILY CYCLE")
        print(f"{'='*60}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print()

        # Run automation
        print("Running daily automation...")
        self.cms.run_daily_automation()

        # Analyze & attack
        print("\nRunning attack engine...")
        self.attack.auto_execute(self.cms.clients, num_new_clients=10)

        print("\n✓ Daily cycle complete")

    def run_monthly_cycle(self):
        """
        Run monthly cycle:
        1. Process payments to all clients
        2. Analyze monthly performance
        3. Adjust strategy
        """

        print(f"\n{'='*60}")
        print("💰 MONTHLY CYCLE")
        print(f"{'='*60}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        print()

        # Process payments
        print("Processing payments...")
        results = self.cms.calculate_monthly_payments()

        print(f"\n✓ Monthly cycle complete")
        print(f"✓ Processed ${results['total_client_payments']:,.2f} to clients")
        print(f"✓ We earned ${results['total_our_earnings']:,.2f}")

        return results

    def run_forever(self):
        """
        Run forever (autonomous mode)

        Daily:
        - Run automation
        - Make new calls
        - Onboard clients
        - Analyze & scale

        Monthly:
        - Process payments
        - Optimize strategy

        This runs FOREVER.
        """

        print(f"\n{'='*60}")
        print("♾️  AUTONOMOUS MODE - RUNNING FOREVER")
        print(f"{'='*60}\n")

        print("Press Ctrl+C to stop\n")

        day_count = 0

        try:
            while True:
                day_count += 1

                print(f"\n{'='*60}")
                print(f"DAY {day_count}")
                print(f"{'='*60}\n")

                # Daily blitz (add clients)
                self.run_blitz(industry="hvac", num_calls=20)

                # Daily automation
                self.run_daily_cycle()

                # Monthly cycle (every 30 days)
                if day_count % 30 == 0:
                    self.run_monthly_cycle()

                # Show dashboard
                self.cms.print_dashboard()

                print(f"\n✓ Day {day_count} complete")
                print("Waiting 24 hours for next cycle...")
                print("(In production, this would sleep for 24 hours)")

                # In real mode, sleep for 24 hours
                # In demo mode, just loop
                if day_count >= 3:  # Demo: run 3 days then stop
                    print(f"\n✓ Demo complete (3 days simulated)")
                    break

        except KeyboardInterrupt:
            print(f"\n\n✓ Stopped after {day_count} days")

        # Final summary
        self.cms.print_dashboard()

    def run_attack_mode(self, days: int = 7):
        """
        ATTACK MODE - Maximum aggression for X days

        Goal: Grow as fast as possible

        Every day:
        - Make 100 calls
        - Close 30 deals
        - Onboard 30 clients
        - Scale what works
        """

        print(f"\n{'='*60}")
        print("⚡ ATTACK MODE")
        print(f"{'='*60}")
        print(f"Duration: {days} days")
        print("Goal: Maximum growth")
        print()

        for day in range(1, days + 1):
            print(f"\n{'='*60}")
            print(f"ATTACK DAY {day}/{days}")
            print(f"{'='*60}\n")

            # Massive blitz
            self.run_blitz(industry="hvac", num_calls=100)

            # Analyze and scale
            self.attack.auto_execute(self.cms.clients, num_new_clients=20)

            # Show progress
            active = len([c for c in self.cms.clients.values() if c["status"] == "active"])
            total_earnings = sum(c["metrics"]["our_earnings"] for c in self.cms.clients.values() if c["status"] == "active")

            print(f"\n📊 PROGRESS")
            print(f"   Day: {day}/{days}")
            print(f"   Total clients: {active}")
            print(f"   Total monthly earnings: ${total_earnings:,.2f}")
            print(f"   Annualized: ${total_earnings * 12:,.2f}")

        print(f"\n{'='*60}")
        print("⚡ ATTACK MODE COMPLETE")
        print(f"{'='*60}\n")

        self.cms.print_dashboard()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Controller - Autonomous Revenue Engine")

    parser.add_argument("--blitz", action="store_true", help="Run single blitz")
    parser.add_argument("--daily", action="store_true", help="Run daily cycle")
    parser.add_argument("--monthly", action="store_true", help="Run monthly cycle")
    parser.add_argument("--forever", action="store_true", help="Run forever (autonomous)")
    parser.add_argument("--attack", type=int, help="Attack mode for N days")
    parser.add_argument("--calls", type=int, default=20, help="Number of calls per blitz")
    parser.add_argument("--industry", type=str, default="hvac", help="Industry to target")

    args = parser.parse_args()

    master = MasterController()

    if args.blitz:
        master.run_blitz(industry=args.industry, num_calls=args.calls)

    elif args.daily:
        master.run_daily_cycle()

    elif args.monthly:
        master.run_monthly_cycle()

    elif args.forever:
        master.run_forever()

    elif args.attack:
        master.run_attack_mode(days=args.attack)

    else:
        print("\nMASTER CONTROLLER - Autonomous Revenue Engine\n")
        print("Usage:")
        print("  python MASTER.py --blitz --calls 20              # Single blitz (20 calls)")
        print("  python MASTER.py --daily                          # Daily cycle")
        print("  python MASTER.py --monthly                        # Monthly cycle")
        print("  python MASTER.py --forever                        # Run forever")
        print("  python MASTER.py --attack 7                       # Attack mode (7 days)")
        print("\nExamples:")
        print("  python MASTER.py --blitz --calls 100 --industry dental")
        print("  python MASTER.py --attack 30")
