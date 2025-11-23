#!/usr/bin/env python3
"""
GO NOW - Execute Speed Strategy
================================
Move FAST before the window closes.

This script runs the complete 24-hour blitz:
1. Train AI to perfection (1000 rounds)
2. Research 500 targets (5 industries)
3. Make 100 calls TODAY
4. Close 30 deals
5. Generate $1,000-2,000 revenue

Usage:
    python GO_NOW.py --blitz        # Full 24-hour blitz
    python GO_NOW.py --train        # Just training (1000 rounds)
    python GO_NOW.py --calls 100    # Just calls

Love • Loyalty • Honor • Everybody Eats
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path

from ai_trainer import AITrainer
from research_agent import ResearchAgent
from LAUNCH import LaunchSystem

class SpeedExecutor:
    """Execute the speed strategy"""

    def __init__(self):
        self.trainer = AITrainer()
        self.research = ResearchAgent()
        self.launcher = LaunchSystem()

    async def execute_blitz(self):
        """Execute full 24-hour blitz"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║                    GO NOW - SPEED BLITZ                        ║
║                                                                ║
║         Move Fast Before The Window Closes                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

Timeline: Next 24 hours
Target: $1,000-2,000 revenue TODAY
Calls: 100
Expected Closes: 30
Close Rate Target: 30%

Starting in 3 seconds...
        """)

        await asyncio.sleep(3)

        # PHASE 1: TRAIN TO PERFECTION
        print("\n" + "="*60)
        print("PHASE 1: AI TRAINING (1000 rounds)")
        print("="*60)
        print("Target: 80%+ success rate")
        print("Time: ~10-15 minutes")
        print()

        training_result = self.trainer.train(rounds=1000, success_threshold=0.80)

        if training_result["success_rate"] >= 0.80:
            print(f"\n✓ TRAINING COMPLETE: {training_result['success_rate']*100:.1f}% success rate")
            print("✓ AI agents ready for production!")
        else:
            print(f"\n⚠️  Training below target: {training_result['success_rate']*100:.1f}%")
            print("   Proceeding anyway - will improve during real calls")

        # PHASE 2: RESEARCH BLITZ
        print("\n" + "="*60)
        print("PHASE 2: MULTI-INDUSTRY RESEARCH")
        print("="*60)
        print("Industries: HVAC, Dental, Restaurant, Auto, Real Estate")
        print("Targets per industry: 100")
        print("Total targets: 500")
        print()

        industries = ["hvac", "dental", "restaurant", "auto", "realestate"]
        all_targets = []

        for industry in industries:
            print(f"\n🔍 Researching {industry.upper()}...")
            targets = self.research.find_targets(industry, count=100)
            all_targets.extend(targets[:20])  # Top 20 from each
            print(f"   ✓ {len(targets)} targets found, top 20 selected")

        print(f"\n✓ RESEARCH COMPLETE: {len(all_targets)} high-value targets ready")

        # PHASE 3: CALLING BLITZ
        print("\n" + "="*60)
        print("PHASE 3: 100 CALLS BLITZ")
        print("="*60)
        print(f"Targets: {len(all_targets)}")
        print("Expected close rate: 30%")
        print("Expected closes: 30")
        print("Expected revenue: $9,000 (30 × $300)")
        print("Our cut (20%): $1,800")
        print("Our cut (10% after bargaining): $900-1,800")
        print()

        input("Press ENTER to start calling blitz (or Ctrl+C to abort)...")

        # Make the calls
        results = await self.launcher.run(
            industry="multi",  # Multi-industry
            train_rounds=0,  # Already trained
            num_calls=min(100, len(all_targets)),
            full_auto=True
        )

        # PHASE 4: SUMMARY
        print("\n" + "="*60)
        print("24-HOUR BLITZ COMPLETE")
        print("="*60)

        print(f"\n📊 RESULTS:")
        print(f"   Calls made: {results['phases']['calling']['calls_made']}")
        print(f"   Closes: {results['phases']['calling']['closes']}")
        print(f"   Close rate: {results['phases']['calling']['close_rate']:.1f}%")
        print(f"   Revenue: ${results['revenue']['estimated_total']:,}")
        print(f"   Our cut (20%): ${results['revenue']['our_cut_20%']:,}")

        print(f"\n💰 MONEY MADE TODAY:")
        print(f"   ${results['revenue']['our_cut_20%']:,}")

        print(f"\n📈 PROJECTION:")
        daily_revenue = results['revenue']['our_cut_20%']
        weekly_revenue = daily_revenue * 7
        monthly_revenue = daily_revenue * 30

        print(f"   Daily (at this rate): ${daily_revenue:,.0f}")
        print(f"   Weekly: ${weekly_revenue:,.0f}")
        print(f"   Monthly: ${monthly_revenue:,.0f}")

        if monthly_revenue >= 50000:
            print(f"\n✓ ON TRACK FOR $500K+ IN 90 DAYS")
        else:
            print(f"\n⚠️  Need to scale to hit $500k target")
            print(f"   Target daily: $5,500 (currently ${daily_revenue:,.0f})")

        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Deliver solutions to {results['phases']['calling']['closes']} closed deals")
        print(f"   2. Collect payments (send invoices)")
        print(f"   3. Hire team (callers + developers)")
        print(f"   4. Scale to 500 calls/day")

        print("\n" + "="*60)
        print("Love • Loyalty • Honor • Everybody Eats 💝")
        print("="*60 + "\n")

        return results

    async def train_only(self, rounds: int = 1000):
        """Just run training"""
        print(f"\n🤖 Training AI agents ({rounds} rounds)...")
        result = self.trainer.train(rounds=rounds, success_threshold=0.80)
        self.trainer.print_best_patterns()
        return result

    async def research_only(self, industry: str, count: int = 100):
        """Just run research"""
        print(f"\n🔍 Researching {industry} ({count} targets)...")
        targets = self.research.find_targets(industry, count=count)
        self.research.print_top_targets(targets, 20)
        return targets

async def main():
    parser = argparse.ArgumentParser(description="GO NOW - Speed Strategy Executor")
    parser.add_argument("--blitz", action="store_true", help="Run full 24-hour blitz")
    parser.add_argument("--train", action="store_true", help="Just train AI (1000 rounds)")
    parser.add_argument("--research", type=str, help="Just research industry")
    parser.add_argument("--calls", type=int, help="Just make N calls")
    parser.add_argument("--rounds", type=int, default=1000, help="Training rounds")
    args = parser.parse_args()

    executor = SpeedExecutor()

    if args.blitz:
        await executor.execute_blitz()
    elif args.train:
        await executor.train_only(args.rounds)
    elif args.research:
        await executor.research_only(args.research, 100)
    elif args.calls:
        launcher = LaunchSystem()
        await launcher.run(industry="hvac", train_rounds=100, num_calls=args.calls, full_auto=True)
    else:
        print("""
GO NOW - Speed Strategy Executor

Commands:
  --blitz           Run full 24-hour blitz (train + research + 100 calls)
  --train           Train AI to perfection (1000 rounds)
  --research INDUSTRY   Research specific industry
  --calls N         Make N calls immediately

Examples:
  python GO_NOW.py --blitz              # Full 24-hour execution
  python GO_NOW.py --train              # Train AI only
  python GO_NOW.py --research dental    # Research dental industry
  python GO_NOW.py --calls 50           # Make 50 calls now

Recommended: Start with --blitz for fastest results.

THE WINDOW IS CLOSING. MOVE NOW.
        """)

if __name__ == "__main__":
    asyncio.run(main())
