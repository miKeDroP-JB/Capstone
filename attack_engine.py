#!/usr/bin/env python3
"""
ATTACK ENGINE - Infinitely Scalable, Always Attacking
======================================================
Identifies what works and SCALES IT IMMEDIATELY.
Kills what doesn't work FAST.
Always in proactive attack mode, never reactive.

How it works:
1. Monitor ALL metrics across ALL clients
2. Identify patterns (what industries/offers/channels convert best)
3. ATTACK winners immediately (10X investment)
4. KILL losers immediately (stop wasting time)
5. Move FAST, pivot FASTER
6. Infinitely scalable

This is the BRAIN.

Love • Loyalty • Honor • Everybody Eats
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import statistics

class AttackEngine:
    """The brain that identifies winners and scales them"""

    def __init__(self):
        self.data_dir = Path("attack_data")
        self.data_dir.mkdir(exist_ok=True)

        self.strategy_file = self.data_dir / "attack_strategy.json"
        self.wins_file = self.data_dir / "wins.json"
        self.kills_file = self.data_dir / "kills.json"

        self.attack_strategy = self._load_attack_strategy()
        self.wins = self._load_wins()
        self.kills = self._load_kills()

    def _load_attack_strategy(self) -> Dict:
        """Load current attack strategy"""
        if self.strategy_file.exists():
            with open(self.strategy_file) as f:
                return json.load(f)
        return {
            "current_focus": [],
            "attack_targets": [],
            "kill_list": [],
            "scale_opportunities": []
        }

    def _save_attack_strategy(self):
        """Save attack strategy"""
        with open(self.strategy_file, 'w') as f:
            json.dump(self.attack_strategy, f, indent=2)

    def _load_wins(self) -> List:
        """Load wins"""
        if self.wins_file.exists():
            with open(self.wins_file) as f:
                return json.load(f)
        return []

    def _save_wins(self):
        """Save wins"""
        with open(self.wins_file, 'w') as f:
            json.dump(self.wins, f, indent=2)

    def _load_kills(self) -> List:
        """Load kills"""
        if self.kills_file.exists():
            with open(self.kills_file) as f:
                return json.load(f)
        return []

    def _save_kills(self):
        """Save kills"""
        with open(self.kills_file, 'w') as f:
            json.dump(self.kills, f, indent=2)

    def analyze_ecosystem(self, clients: Dict) -> Dict:
        """
        Analyze entire ecosystem to identify what's working

        Returns:
        - Top performing industries
        - Top performing offers
        - Top performing channels
        - Underperforming segments (to kill)
        - Scale opportunities
        """
        print(f"\n{'='*60}")
        print("ATTACK ENGINE - ANALYZING ECOSYSTEM")
        print(f"{'='*60}\n")

        active_clients = {k: v for k, v in clients.items() if v["status"] == "active"}

        if not active_clients:
            print("❌ No active clients to analyze")
            return {}

        # Group by industry
        industry_performance = defaultdict(lambda: {
            "revenue": 0,
            "leads": 0,
            "clients": 0,
            "avg_revenue_per_client": 0
        })

        # Group by offer type
        offer_performance = defaultdict(lambda: {
            "revenue": 0,
            "leads": 0,
            "clients": 0,
            "close_rate": 0
        })

        # Analyze each client
        for client_id, client in active_clients.items():
            industry = client["industry"]
            offer = client["package_type"]
            metrics = client["metrics"]

            # Industry stats
            industry_performance[industry]["revenue"] += metrics["revenue_generated"]
            industry_performance[industry]["leads"] += metrics["leads_generated"]
            industry_performance[industry]["clients"] += 1

            # Offer stats
            offer_performance[offer]["revenue"] += metrics["revenue_generated"]
            offer_performance[offer]["leads"] += metrics["leads_generated"]
            offer_performance[offer]["clients"] += 1

        # Calculate averages
        for industry in industry_performance:
            if industry_performance[industry]["clients"] > 0:
                industry_performance[industry]["avg_revenue_per_client"] = \
                    industry_performance[industry]["revenue"] / industry_performance[industry]["clients"]

        # Identify WINNERS (top performers)
        winners = self._identify_winners(industry_performance, offer_performance)

        # Identify LOSERS (kill these)
        losers = self._identify_losers(industry_performance, offer_performance)

        # Identify SCALE OPPORTUNITIES
        scale_ops = self._identify_scale_opportunities(winners, active_clients)

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_clients": len(active_clients),
            "industry_performance": dict(industry_performance),
            "offer_performance": dict(offer_performance),
            "winners": winners,
            "losers": losers,
            "scale_opportunities": scale_ops
        }

        self._print_analysis(analysis)

        return analysis

    def _identify_winners(self, industry_perf: Dict, offer_perf: Dict) -> Dict:
        """Identify top performers to ATTACK"""

        winners = {
            "industries": [],
            "offers": []
        }

        # Top industries by revenue per client
        if industry_perf:
            sorted_industries = sorted(
                industry_perf.items(),
                key=lambda x: x[1]["avg_revenue_per_client"],
                reverse=True
            )

            # Top 20% are winners
            num_winners = max(1, len(sorted_industries) // 5)
            for industry, stats in sorted_industries[:num_winners]:
                winners["industries"].append({
                    "name": industry,
                    "revenue_per_client": stats["avg_revenue_per_client"],
                    "total_revenue": stats["revenue"],
                    "action": "ATTACK - Scale 10X"
                })

        # Top offers by revenue
        if offer_perf:
            sorted_offers = sorted(
                offer_perf.items(),
                key=lambda x: x[1]["revenue"],
                reverse=True
            )

            for offer, stats in sorted_offers[:2]:  # Top 2 offers
                winners["offers"].append({
                    "name": offer,
                    "total_revenue": stats["revenue"],
                    "clients": stats["clients"],
                    "action": "ATTACK - Scale 10X"
                })

        return winners

    def _identify_losers(self, industry_perf: Dict, offer_perf: Dict) -> Dict:
        """Identify underperformers to KILL"""

        losers = {
            "industries": [],
            "offers": []
        }

        # Bottom industries by revenue per client
        if len(industry_perf) > 2:  # Only if we have enough data
            sorted_industries = sorted(
                industry_perf.items(),
                key=lambda x: x[1]["avg_revenue_per_client"]
            )

            # Bottom 20% are losers
            num_losers = max(1, len(sorted_industries) // 5)
            for industry, stats in sorted_industries[:num_losers]:
                losers["industries"].append({
                    "name": industry,
                    "revenue_per_client": stats["avg_revenue_per_client"],
                    "action": "KILL - Stop onboarding"
                })

        return losers

    def _identify_scale_opportunities(self, winners: Dict, clients: Dict) -> List:
        """Identify immediate scale opportunities"""

        opportunities = []

        # For each winning industry
        for industry_win in winners.get("industries", []):
            industry_name = industry_win["name"]
            revenue_per_client = industry_win["revenue_per_client"]

            # How many clients in this industry?
            current_count = sum(1 for c in clients.values() if c["industry"] == industry_name)

            opportunities.append({
                "type": "SCALE_INDUSTRY",
                "industry": industry_name,
                "current_clients": current_count,
                "revenue_per_client": revenue_per_client,
                "action": f"Add 10 more {industry_name} clients IMMEDIATELY",
                "projected_revenue": revenue_per_client * 10,
                "timeline": "7 days"
            })

        # For each winning offer
        for offer_win in winners.get("offers", []):
            offer_name = offer_win["name"]

            opportunities.append({
                "type": "SCALE_OFFER",
                "offer": offer_name,
                "current_clients": offer_win["clients"],
                "action": f"Push {offer_name} to ALL new clients",
                "timeline": "Immediate"
            })

        return opportunities

    def _print_analysis(self, analysis: Dict):
        """Print analysis results"""

        print("🎯 INDUSTRY PERFORMANCE")
        for industry, stats in analysis["industry_performance"].items():
            print(f"\n   {industry.upper()}")
            print(f"      Clients: {stats['clients']}")
            print(f"      Total revenue: ${stats['revenue']:,.2f}")
            print(f"      Revenue per client: ${stats['avg_revenue_per_client']:,.2f}")

        print(f"\n\n{'='*60}")
        print("🏆 WINNERS - ATTACK THESE")
        print(f"{'='*60}")

        for industry in analysis["winners"].get("industries", []):
            print(f"\n✓ {industry['name'].upper()}")
            print(f"   Revenue per client: ${industry['revenue_per_client']:,.2f}")
            print(f"   → {industry['action']}")

        if analysis["losers"]["industries"]:
            print(f"\n\n{'='*60}")
            print("❌ LOSERS - KILL THESE")
            print(f"{'='*60}")

            for industry in analysis["losers"]["industries"]:
                print(f"\n✗ {industry['name'].upper()}")
                print(f"   Revenue per client: ${industry['revenue_per_client']:,.2f}")
                print(f"   → {industry['action']}")

        print(f"\n\n{'='*60}")
        print("🚀 SCALE OPPORTUNITIES - DO NOW")
        print(f"{'='*60}")

        for i, opp in enumerate(analysis["scale_opportunities"], 1):
            print(f"\n{i}. {opp['type']}")
            if opp['type'] == "SCALE_INDUSTRY":
                print(f"   Industry: {opp['industry']}")
                print(f"   Current: {opp['current_clients']} clients")
                print(f"   Action: {opp['action']}")
                print(f"   Projected revenue: ${opp['projected_revenue']:,.2f}")
                print(f"   Timeline: {opp['timeline']}")
            else:
                print(f"   Offer: {opp['offer']}")
                print(f"   Action: {opp['action']}")

    def execute_attack_strategy(self, analysis: Dict, num_new_clients: int = 10) -> Dict:
        """
        Execute the attack strategy

        Takes analysis and IMMEDIATELY:
        1. Scale winning industries (add clients)
        2. Kill losing industries (stop onboarding)
        3. Push winning offers to all clients
        4. Move FAST
        """

        print(f"\n\n{'='*60}")
        print("⚡ EXECUTING ATTACK STRATEGY")
        print(f"{'='*60}\n")

        execution_plan = {
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }

        # ACTION 1: Scale winning industries
        print("🎯 ACTION 1: SCALE WINNERS\n")

        for opp in analysis["scale_opportunities"]:
            if opp["type"] == "SCALE_INDUSTRY":
                action = {
                    "type": "ADD_CLIENTS",
                    "industry": opp["industry"],
                    "target_count": num_new_clients,
                    "timeline": "7 days",
                    "status": "READY_TO_EXECUTE"
                }

                print(f"   ✓ Targeting {num_new_clients} new {opp['industry']} clients")
                print(f"   ✓ Expected revenue: ${opp['revenue_per_client'] * num_new_clients:,.2f}")

                execution_plan["actions"].append(action)

        # ACTION 2: Kill losers
        if analysis["losers"]["industries"]:
            print(f"\n❌ ACTION 2: KILL LOSERS\n")

            for loser in analysis["losers"]["industries"]:
                action = {
                    "type": "STOP_ONBOARDING",
                    "industry": loser["name"],
                    "reason": f"Low revenue per client (${loser['revenue_per_client']:,.2f})",
                    "status": "IMMEDIATE"
                }

                print(f"   ✗ STOP onboarding {loser['name']} clients")
                print(f"   ✗ Focus resources on winners")

                execution_plan["actions"].append(action)

        # ACTION 3: Auto-scale
        print(f"\n🚀 ACTION 3: AUTO-SCALE\n")

        print(f"   ✓ Research {num_new_clients} targets in winning industries")
        print(f"   ✓ Train agents on winning patterns")
        print(f"   ✓ Make {num_new_clients * 3} calls (30% close rate)")
        print(f"   ✓ Onboard {num_new_clients} new clients")
        print(f"   ✓ Timeline: 7 days")

        auto_scale_action = {
            "type": "AUTO_SCALE",
            "steps": [
                f"Research {num_new_clients * 2} targets",
                f"Make {num_new_clients * 3} calls",
                f"Close {num_new_clients} deals",
                "Onboard all clients",
                "Deploy automation"
            ],
            "timeline": "7 days",
            "status": "READY"
        }

        execution_plan["actions"].append(auto_scale_action)

        # Save execution plan
        execution_file = self.data_dir / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(execution_file, 'w') as f:
            json.dump(execution_plan, f, indent=2)

        print(f"\n✓ Attack strategy saved: {execution_file}")

        return execution_plan

    def auto_execute(self, clients: Dict, num_new_clients: int = 10):
        """
        Full auto-execution

        1. Analyze ecosystem
        2. Identify winners
        3. Kill losers
        4. Scale winners IMMEDIATELY
        5. Repeat daily
        """

        print(f"\n{'='*60}")
        print("🤖 AUTO-EXECUTE MODE")
        print(f"{'='*60}")
        print("Analyzing → Identifying → Scaling → Attacking")
        print()

        # Step 1: Analyze
        analysis = self.analyze_ecosystem(clients)

        if not analysis:
            print("❌ No data to analyze yet")
            return

        # Step 2: Execute
        execution = self.execute_attack_strategy(analysis, num_new_clients)

        # Step 3: Calculate impact
        print(f"\n{'='*60}")
        print("📊 PROJECTED IMPACT")
        print(f"{'='*60}\n")

        current_monthly = sum(
            c["metrics"]["our_earnings"]
            for c in clients.values()
            if c["status"] == "active"
        )

        # Assume new clients perform at average of winners
        if analysis["winners"]["industries"]:
            avg_winner_revenue = statistics.mean([
                w["revenue_per_client"] * 0.20  # Our 20% share
                for w in analysis["winners"]["industries"]
            ])

            projected_new_monthly = avg_winner_revenue * num_new_clients
            projected_total = current_monthly + projected_new_monthly

            print(f"Current monthly: ${current_monthly:,.2f}")
            print(f"New clients ({num_new_clients}): ${projected_new_monthly:,.2f}")
            print(f"Projected total: ${projected_total:,.2f}")
            print(f"Growth: {((projected_total / current_monthly - 1) * 100) if current_monthly > 0 else 0:.0f}%")

            # Extrapolate
            print(f"\n🚀 SCALE TRAJECTORY (repeating weekly)")
            week_1 = projected_total
            week_2 = week_1 + projected_new_monthly
            week_3 = week_2 + projected_new_monthly
            week_4 = week_3 + projected_new_monthly

            print(f"   Week 1: ${week_1:,.2f}/month")
            print(f"   Week 2: ${week_2:,.2f}/month")
            print(f"   Week 3: ${week_3:,.2f}/month")
            print(f"   Week 4: ${week_4:,.2f}/month")

            print(f"\n💰 If we add {num_new_clients} clients/week for 4 weeks:")
            print(f"   Total clients: {len(clients) + (num_new_clients * 4)}")
            print(f"   Monthly revenue: ${week_4:,.2f}")
            print(f"   Annual run rate: ${week_4 * 12:,.2f}")

        print(f"\n{'='*60}")
        print("⚡ ATTACK MODE: ENGAGED")
        print(f"{'='*60}")
        print("✓ Winners identified")
        print("✓ Losers killed")
        print("✓ Scale strategy ready")
        print("✓ Always attacking, never reacting")
        print()

        return execution


if __name__ == "__main__":
    import argparse
    from client_management_system import ClientManagementSystem

    parser = argparse.ArgumentParser(description="Attack Engine - Scale what works, kill what doesn't")
    parser.add_argument("--analyze", action="store_true", help="Analyze ecosystem")
    parser.add_argument("--execute", action="store_true", help="Execute attack strategy")
    parser.add_argument("--auto", action="store_true", help="Full auto-execute")
    parser.add_argument("--scale", type=int, default=10, help="Number of new clients to add")

    args = parser.parse_args()

    # Load clients
    cms = ClientManagementSystem()

    engine = AttackEngine()

    if args.analyze:
        engine.analyze_ecosystem(cms.clients)

    elif args.execute:
        analysis = engine.analyze_ecosystem(cms.clients)
        if analysis:
            engine.execute_attack_strategy(analysis, args.scale)

    elif args.auto:
        engine.auto_execute(cms.clients, args.scale)

    else:
        print("Attack Engine")
        print("\nUsage:")
        print("  python attack_engine.py --analyze")
        print("  python attack_engine.py --execute --scale 10")
        print("  python attack_engine.py --auto --scale 20")
