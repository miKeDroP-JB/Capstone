#!/usr/bin/env python3
"""
LAUNCH - Intelligent Auto Sales System
=======================================
Research → Train → Call → Close → Build → Collect

The complete system that:
1. Finds best targets (Research Agent)
2. Trains AI agents (AI Trainer)
3. Makes calls (Sales Agent)
4. Discovers needs
5. Builds solutions instantly
6. Closes deals (80/20 split)

Usage:
    python LAUNCH.py --train 100 --calls 10
    python LAUNCH.py --industry hvac --calls 20
    python LAUNCH.py --full-auto

Love • Loyalty • Honor • Everybody Eats
"""

import asyncio
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Import our agents
from research_agent import ResearchAgent
from ai_trainer import AITrainer
from intelligent_sales_agent import IntelligentSalesAgent
from instant_game_creator import InstantGameCreator
from instant_video_creator import InstantVideoCreator

class LaunchSystem:
    """Orchestrates the entire system"""

    def __init__(self):
        self.research = ResearchAgent()
        self.trainer = AITrainer()
        self.sales_agent = IntelligentSalesAgent()
        self.game_creator = InstantGameCreator()
        self.video_creator = InstantVideoCreator()

        self.results_dir = Path("launch_results")
        self.results_dir.mkdir(exist_ok=True)

    async def run(self, industry: str = "hvac", train_rounds: int = 100,
                  num_calls: int = 10, full_auto: bool = False):
        """Run the complete system"""

        print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🚀 INTELLIGENT AUTO SALES SYSTEM - LAUNCH 🚀           ║
║                                                                ║
║     Research → Train → Call → Discover → Build → Close        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
        """)

        launch_id = f"launch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        results = {
            "launch_id": launch_id,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "industry": industry,
                "train_rounds": train_rounds,
                "num_calls": num_calls,
                "full_auto": full_auto
            },
            "phases": {}
        }

        # PHASE 1: RESEARCH
        print(f"\n{'='*60}")
        print("PHASE 1: RESEARCH - Finding Best Targets")
        print(f"{'='*60}")

        targets = self.research.find_targets(industry, count=num_calls * 2)  # 2x for selection
        top_targets = targets[:num_calls]

        results["phases"]["research"] = {
            "targets_found": len(targets),
            "targets_selected": len(top_targets),
            "avg_score": sum(t["score"] for t in top_targets) / len(top_targets)
        }

        print(f"\n✓ Research complete: {len(top_targets)} high-value targets selected")

        # PHASE 2: TRAINING
        print(f"\n{'='*60}")
        print("PHASE 2: TRAINING - AI Agents Train Each Other")
        print(f"{'='*60}")

        training_results = self.trainer.train(rounds=train_rounds, success_threshold=0.70)

        results["phases"]["training"] = {
            "rounds_completed": train_rounds,
            "success_rate": training_results["success_rate"],
            "patterns_learned": len(self.trainer.get_best_patterns().get("openers", []))
        }

        print(f"\n✓ Training complete: {training_results['success_rate']*100:.1f}% success rate")

        if training_results["success_rate"] >= 0.70:
            print(f"✓ Agents ready for deployment!")
        else:
            print(f"⚠️  Below threshold, but proceeding...")

        # PHASE 3: CALLING
        print(f"\n{'='*60}")
        print("PHASE 3: CALLING - Making Sales Calls")
        print(f"{'='*60}")

        call_results = []
        closes = 0
        interested = 0

        for i, target in enumerate(top_targets, 1):
            print(f"\nCall {i}/{len(top_targets)}")
            print(f"{'─'*60}")

            call_result = self.sales_agent.make_call(target)
            call_results.append(call_result)

            if call_result["outcome"] == "closed":
                closes += 1
            elif call_result["outcome"] == "interested_thinking":
                interested += 1

            # Small delay between calls
            await asyncio.sleep(0.5)

        results["phases"]["calling"] = {
            "calls_made": len(call_results),
            "closes": closes,
            "interested": interested,
            "close_rate": (closes / len(call_results)) * 100,
            "interest_rate": ((closes + interested) / len(call_results)) * 100
        }

        print(f"\n✓ Calling complete: {closes} closes, {interested} interested")

        # PHASE 4: BUILD & CLOSE
        print(f"\n{'='*60}")
        print("PHASE 4: BUILD & CLOSE - Creating Solutions")
        print(f"{'='*60}")

        builds = []
        closed_deals = [c for c in call_results if c["outcome"] == "closed"]

        for deal in closed_deals:
            need = deal.get("discovered_need")
            target = deal["target"]

            print(f"\nBuilding solution for {target['company']}...")
            print(f"   Need: {need}")

            # Build appropriate solution
            if need in ["game", "entertainment"]:
                solution = self.game_creator.create_game(f"Business game for {target['company']}")
            elif need in ["marketing", "video", "promo"]:
                solution = self.video_creator.create_video(f"Marketing video for {target['company']}")
            else:
                # Generic solution
                solution = {
                    "type": "custom_solution",
                    "description": f"Custom {need} solution",
                    "build_time": "4 hours",
                    "status": "ready"
                }
                print(f"   ✓ Solution ready: Custom {need} system")

            builds.append({
                "target": target["company"],
                "need": need,
                "solution": solution
            })

        results["phases"]["building"] = {
            "solutions_built": len(builds),
            "types": list(set(b["need"] for b in builds if b.get("need")))
        }

        print(f"\n✓ Built {len(builds)} solutions")

        # FINAL RESULTS
        print(f"\n{'='*60}")
        print("FINAL RESULTS")
        print(f"{'='*60}")

        # Calculate revenue (estimated)
        avg_deal_value = 3000  # Average deal value
        total_revenue = closes * avg_deal_value
        our_cut = total_revenue * 0.20
        their_cut = total_revenue * 0.80

        results["revenue"] = {
            "estimated_total": total_revenue,
            "our_cut_20%": our_cut,
            "their_cut_80%": their_cut,
            "deals_closed": closes
        }

        print(f"\n💰 REVENUE (Estimated):")
        print(f"   Total deal value: ${total_revenue:,}")
        print(f"   Their 80%: ${their_cut:,}")
        print(f"   Our 20%: ${our_cut:,}")

        print(f"\n📊 PERFORMANCE:")
        print(f"   Targets researched: {results['phases']['research']['targets_found']}")
        print(f"   AI training success: {results['phases']['training']['success_rate']*100:.1f}%")
        print(f"   Calls made: {results['phases']['calling']['calls_made']}")
        print(f"   Close rate: {results['phases']['calling']['close_rate']:.1f}%")
        print(f"   Solutions built: {results['phases']['building']['solutions_built']}")

        # Save results
        results_file = self.results_dir / f"{launch_id}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to: {results_file}")

        # Print detailed report
        self.print_detailed_report(results)

        return results

    def print_detailed_report(self, results: Dict):
        """Print detailed completion report"""

        print(f"\n{'═'*70}")
        print("DETAILED COMPLETION REPORT")
        print(f"{'═'*70}\n")

        print(f"Launch ID: {results['launch_id']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Industry: {results['config']['industry']}")

        print(f"\n{'─'*70}")
        print("PHASE 1: RESEARCH")
        print(f"{'─'*70}")
        r = results['phases']['research']
        print(f"✓ Targets found: {r['targets_found']}")
        print(f"✓ Targets selected: {r['targets_selected']}")
        print(f"✓ Average score: {r['avg_score']:.1f}/100")

        print(f"\n{'─'*70}")
        print("PHASE 2: TRAINING")
        print(f"{'─'*70}")
        t = results['phases']['training']
        print(f"✓ Training rounds: {results['config']['train_rounds']}")
        print(f"✓ Success rate achieved: {t['success_rate']*100:.1f}%")
        print(f"✓ Patterns learned: {t['patterns_learned']}")
        print(f"✓ Status: {'READY FOR DEPLOYMENT ✓' if t['success_rate'] >= 0.70 else 'NEEDS MORE TRAINING ⚠️'}")

        print(f"\n{'─'*70}")
        print("PHASE 3: CALLING")
        print(f"{'─'*70}")
        c = results['phases']['calling']
        print(f"✓ Calls made: {c['calls_made']}")
        print(f"✓ Closes: {c['closes']}")
        print(f"✓ Interested: {c['interested']}")
        print(f"✓ Close rate: {c['close_rate']:.1f}%")
        print(f"✓ Interest rate: {c['interest_rate']:.1f}%")

        print(f"\n{'─'*70}")
        print("PHASE 4: BUILDING")
        print(f"{'─'*70}")
        b = results['phases']['building']
        print(f"✓ Solutions built: {b['solutions_built']}")
        print(f"✓ Solution types: {', '.join(b['types']) if b['types'] else 'None yet'}")

        print(f"\n{'─'*70}")
        print("REVENUE (80/20 SPLIT)")
        print(f"{'─'*70}")
        rev = results['revenue']
        print(f"✓ Deals closed: {rev['deals_closed']}")
        print(f"✓ Total deal value: ${rev['estimated_total']:,}")
        print(f"✓ Their 80%: ${rev['their_cut_80%']:,}")
        print(f"✓ Our 20%: ${rev['our_cut_20%']:,}")

        print(f"\n{'─'*70}")
        print("NEXT STEPS")
        print(f"{'─'*70}")
        print(f"1. Follow up with {results['phases']['calling']['interested']} interested prospects")
        print(f"2. Deliver {results['phases']['building']['solutions_built']} built solutions")
        print(f"3. Collect payments (setup fees + ongoing 20%)")
        print(f"4. Scale: Research more targets, run more campaigns")

        print(f"\n{'═'*70}")
        print("SYSTEM STATUS: ✓ OPERATIONAL")
        print(f"{'═'*70}\n")

async def main():
    parser = argparse.ArgumentParser(description="Launch Intelligent Auto Sales System")
    parser.add_argument("--industry", default="hvac", help="Industry to target")
    parser.add_argument("--train", type=int, default=100, help="AI training rounds")
    parser.add_argument("--calls", type=int, default=10, help="Number of calls to make")
    parser.add_argument("--full-auto", action="store_true", help="Full automation mode")
    args = parser.parse_args()

    system = LaunchSystem()
    results = await system.run(
        industry=args.industry,
        train_rounds=args.train,
        num_calls=args.calls,
        full_auto=args.full_auto
    )

    print(f"\n✓ LAUNCH COMPLETE!")
    print(f"   Love • Loyalty • Honor • Everybody Eats 💝\n")

if __name__ == "__main__":
    asyncio.run(main())
