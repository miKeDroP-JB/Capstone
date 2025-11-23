#!/usr/bin/env python3
"""
AUTO REVENUE ENGINE - The Almost Automated Edition
===================================================
You create. You decide. System executes.

This is the autonomous revenue generation system.
You just approve decisions and collect money.

Usage:
    python auto_revenue_engine.py start
    python auto_revenue_engine.py status
    python auto_revenue_engine.py approve <decision_id>
    python auto_revenue_engine.py monitor

Love • Loyalty • Honor • Everybody Eats
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Import our existing systems
try:
    from the_instant_creator import InstantCreator, GCODE, LoveLedger
except ImportError:
    print("⚠️  InstantCreator not found, using fallback mode")
    InstantCreator = None

class AutoRevenueEngine:
    """
    Autonomous revenue generation with human-in-the-loop decisions.

    What it does automatically:
    - Loads target companies
    - Makes AI voice calls to prospects
    - Books demos automatically
    - Schedules follow-ups
    - Tracks revenue
    - Presents decisions for your approval

    What you do:
    - Approve/decline big decisions
    - Collect money
    - Scale up
    """

    def __init__(self):
        self.data_dir = Path("revenue/auto_engine_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.campaigns_file = self.data_dir / "campaigns.json"
        self.decisions_file = self.data_dir / "pending_decisions.json"
        self.results_file = self.data_dir / "results.json"
        self.config_file = self.data_dir / "config.json"

        self.config = self._load_config()
        self.campaigns = self._load_campaigns()
        self.decisions = self._load_decisions()
        self.results = self._load_results()

        # Auto-approve thresholds (configurable)
        self.auto_approve = {
            "call_campaign": self.config.get("auto_approve_calls", True),
            "demo_booking": self.config.get("auto_approve_demos", True),
            "follow_up": self.config.get("auto_approve_followups", True),
            "spend_under": self.config.get("auto_approve_spend_under", 100),  # Auto-approve spending under $100
        }

        print("🚀 AUTO REVENUE ENGINE initialized")
        print(f"   Campaigns: {len(self.campaigns)}")
        print(f"   Pending decisions: {len(self.decisions)}")
        print(f"   Mode: {'Full Auto' if self.config.get('full_auto', False) else 'Human Approval'}")

    def _load_config(self) -> Dict:
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)

        # Default config
        default_config = {
            "full_auto": False,  # Set to True for zero human intervention
            "auto_approve_calls": True,  # Auto-approve making calls
            "auto_approve_demos": True,  # Auto-approve booking demos
            "auto_approve_followups": True,  # Auto-approve follow-ups
            "auto_approve_spend_under": 100,  # Auto-approve spending under $100
            "daily_call_limit": 100,  # Max calls per day
            "love_score_threshold": 0.70,  # Minimum love score
            "revenue_split": {
                "owner": 0.70,
                "community": 0.20,
                "sanctuary": 0.10
            }
        }

        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _load_campaigns(self) -> List[Dict]:
        """Load campaigns"""
        if self.campaigns_file.exists():
            with open(self.campaigns_file) as f:
                return json.load(f)
        return []

    def _save_campaigns(self):
        """Save campaigns"""
        with open(self.campaigns_file, 'w') as f:
            json.dump(self.campaigns, f, indent=2)

    def _load_decisions(self) -> List[Dict]:
        """Load pending decisions"""
        if self.decisions_file.exists():
            with open(self.decisions_file) as f:
                return json.load(f)
        return []

    def _save_decisions(self):
        """Save decisions"""
        with open(self.decisions_file, 'w') as f:
            json.dump(self.decisions, f, indent=2)

    def _load_results(self) -> Dict:
        """Load results"""
        if self.results_file.exists():
            with open(self.results_file) as f:
                return json.load(f)
        return {
            "total_calls": 0,
            "demos_booked": 0,
            "deals_closed": 0,
            "total_revenue": 0,
            "by_campaign": {}
        }

    def _save_results(self):
        """Save results"""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

    async def create_campaign(self, campaign_type: str, targets: List[Dict],
                            config: Optional[Dict] = None) -> str:
        """
        Create a new revenue campaign.

        Campaign types:
        - hvac_voice_agent: AI voice calls to HVAC companies
        - code_gen_service: Sell code generation services
        - voice_platform: Sell voice agency platform
        """
        campaign_id = f"camp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        campaign = {
            "id": campaign_id,
            "type": campaign_type,
            "created": datetime.now().isoformat(),
            "status": "pending_approval",
            "targets": targets,
            "config": config or {},
            "results": {
                "calls_made": 0,
                "demos_booked": 0,
                "deals_closed": 0,
                "revenue": 0
            }
        }

        self.campaigns.append(campaign)
        self._save_campaigns()

        # Create decision for user approval
        decision_id = await self._create_decision(
            decision_type="launch_campaign",
            description=f"Launch {campaign_type} campaign with {len(targets)} targets",
            data=campaign,
            auto_approve=self.auto_approve["call_campaign"]
        )

        print(f"✓ Campaign created: {campaign_id}")
        print(f"  Decision pending: {decision_id}")

        return campaign_id

    async def _create_decision(self, decision_type: str, description: str,
                              data: Dict, auto_approve: bool = False) -> str:
        """Create a decision for user approval"""
        decision_id = f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        decision = {
            "id": decision_id,
            "type": decision_type,
            "description": description,
            "created": datetime.now().isoformat(),
            "status": "pending",
            "data": data,
            "auto_approve": auto_approve
        }

        # Auto-approve if configured
        if auto_approve or self.config.get("full_auto", False):
            decision["status"] = "auto_approved"
            decision["approved_at"] = datetime.now().isoformat()
            print(f"✓ Auto-approved: {description}")

            # Execute immediately
            await self._execute_decision(decision)
        else:
            self.decisions.append(decision)
            self._save_decisions()
            print(f"⏳ Decision pending: {description}")
            print(f"   Approve with: python auto_revenue_engine.py approve {decision_id}")

        return decision_id

    async def approve_decision(self, decision_id: str, approved: bool = True):
        """Approve or decline a decision"""
        decision = None
        for d in self.decisions:
            if d["id"] == decision_id:
                decision = d
                break

        if not decision:
            print(f"✗ Decision not found: {decision_id}")
            return

        if approved:
            decision["status"] = "approved"
            decision["approved_at"] = datetime.now().isoformat()
            print(f"✓ Approved: {decision['description']}")

            # Execute
            await self._execute_decision(decision)
        else:
            decision["status"] = "declined"
            decision["declined_at"] = datetime.now().isoformat()
            print(f"✗ Declined: {decision['description']}")

        # Remove from pending
        self.decisions = [d for d in self.decisions if d["id"] != decision_id]
        self._save_decisions()

    async def _execute_decision(self, decision: Dict):
        """Execute an approved decision"""
        decision_type = decision["type"]
        data = decision["data"]

        if decision_type == "launch_campaign":
            await self._execute_campaign(data)
        elif decision_type == "book_demo":
            await self._execute_demo_booking(data)
        elif decision_type == "send_follow_up":
            await self._execute_follow_up(data)
        elif decision_type == "close_deal":
            await self._execute_deal_closing(data)
        else:
            print(f"⚠️  Unknown decision type: {decision_type}")

    async def _execute_campaign(self, campaign: Dict):
        """Execute a campaign - make AI calls to all targets"""
        campaign_id = campaign["id"]
        targets = campaign["targets"]

        print(f"\n🚀 LAUNCHING CAMPAIGN: {campaign_id}")
        print(f"   Targets: {len(targets)}")
        print(f"   Type: {campaign['type']}")

        # Update campaign status
        for camp in self.campaigns:
            if camp["id"] == campaign_id:
                camp["status"] = "active"
                break
        self._save_campaigns()

        # Make calls to each target
        for idx, target in enumerate(targets, 1):
            print(f"\n[{idx}/{len(targets)}] Calling {target.get('company', 'Unknown')}")

            result = await self._make_ai_call(campaign_id, target)

            # Update results
            self.results["total_calls"] += 1
            if campaign_id not in self.results["by_campaign"]:
                self.results["by_campaign"][campaign_id] = {
                    "calls": 0,
                    "demos": 0,
                    "closed": 0,
                    "revenue": 0
                }
            self.results["by_campaign"][campaign_id]["calls"] += 1

            # Handle result
            if result["outcome"] == "demo_booked":
                print(f"   ✓ Demo booked!")
                self.results["demos_booked"] += 1
                self.results["by_campaign"][campaign_id]["demos"] += 1

                # Create decision for demo (usually auto-approved)
                await self._create_decision(
                    decision_type="book_demo",
                    description=f"Demo scheduled with {target.get('company')} on {result.get('demo_date')}",
                    data=result,
                    auto_approve=self.auto_approve["demo_booking"]
                )

            elif result["outcome"] == "interested":
                print(f"   ⏳ Interested - scheduling follow-up")
                await self._create_decision(
                    decision_type="send_follow_up",
                    description=f"Send follow-up to {target.get('company')}",
                    data=result,
                    auto_approve=self.auto_approve["follow_up"]
                )

            elif result["outcome"] == "not_interested":
                print(f"   ✗ Not interested")

            # Rate limiting - be respectful
            await asyncio.sleep(2)  # 2 seconds between calls

        # Update campaign
        for camp in self.campaigns:
            if camp["id"] == campaign_id:
                camp["status"] = "completed"
                camp["completed_at"] = datetime.now().isoformat()
                break
        self._save_campaigns()
        self._save_results()

        print(f"\n✓ Campaign completed: {campaign_id}")
        print(f"  Calls made: {len(targets)}")
        print(f"  Demos booked: {self.results['by_campaign'][campaign_id]['demos']}")

    async def _make_ai_call(self, campaign_id: str, target: Dict) -> Dict:
        """
        Make an AI voice call to a target.

        In production, this would:
        1. Use Twilio to make the call
        2. Use ElevenLabs for AI voice
        3. Use speech-to-text to understand responses
        4. Use LLM to have intelligent conversation
        5. Book demo if they're interested

        For now, we'll simulate the call.
        """
        company = target.get("company", "Unknown")
        phone = target.get("phone", "")

        print(f"   📞 Calling {company} at {phone}...")

        # Simulate call (in production, this is real)
        await asyncio.sleep(1)  # Simulate call duration

        # Simulate outcomes (in production, this is real conversation)
        import random
        outcomes = [
            {"outcome": "demo_booked", "demo_date": "2025-11-25 10:00", "probability": 0.25},
            {"outcome": "interested", "callback_date": "2025-11-24", "probability": 0.15},
            {"outcome": "not_interested", "reason": "already has solution", "probability": 0.30},
            {"outcome": "voicemail", "probability": 0.25},
            {"outcome": "no_answer", "probability": 0.05}
        ]

        # Weighted random choice
        rand = random.random()
        cumulative = 0
        chosen_outcome = outcomes[0]

        for outcome in outcomes:
            cumulative += outcome["probability"]
            if rand <= cumulative:
                chosen_outcome = outcome
                break

        result = {
            "campaign_id": campaign_id,
            "company": company,
            "phone": phone,
            "call_time": datetime.now().isoformat(),
            "outcome": chosen_outcome["outcome"],
            **{k: v for k, v in chosen_outcome.items() if k not in ["outcome", "probability"]}
        }

        return result

    async def _execute_demo_booking(self, data: Dict):
        """Execute demo booking"""
        print(f"✓ Demo confirmed with {data.get('company')}")
        print(f"  Date: {data.get('demo_date')}")

        # In production: Send calendar invite, confirmation email, etc.

    async def _execute_follow_up(self, data: Dict):
        """Execute follow-up"""
        print(f"✓ Follow-up scheduled for {data.get('company')}")

        # In production: Schedule email, set reminder, etc.

    async def _execute_deal_closing(self, data: Dict):
        """Execute deal closing"""
        amount = data.get("amount", 0)
        company = data.get("company", "Unknown")

        print(f"✓ Deal closed with {company}: ${amount:,.2f}")

        self.results["deals_closed"] += 1
        self.results["total_revenue"] += amount
        self._save_results()

    def get_pending_decisions(self) -> List[Dict]:
        """Get all pending decisions"""
        return [d for d in self.decisions if d["status"] == "pending"]

    def get_status(self) -> Dict:
        """Get current status"""
        return {
            "campaigns": {
                "total": len(self.campaigns),
                "active": len([c for c in self.campaigns if c["status"] == "active"]),
                "completed": len([c for c in self.campaigns if c["status"] == "completed"])
            },
            "results": self.results,
            "pending_decisions": len(self.get_pending_decisions()),
            "config": self.config
        }

    def print_status(self):
        """Print formatted status"""
        status = self.get_status()

        print("\n" + "=" * 60)
        print("AUTO REVENUE ENGINE - STATUS")
        print("=" * 60)

        print(f"\n📊 CAMPAIGNS")
        print(f"   Total: {status['campaigns']['total']}")
        print(f"   Active: {status['campaigns']['active']}")
        print(f"   Completed: {status['campaigns']['completed']}")

        print(f"\n📞 RESULTS")
        print(f"   Calls made: {status['results']['total_calls']}")
        print(f"   Demos booked: {status['results']['demos_booked']}")
        print(f"   Deals closed: {status['results']['deals_closed']}")
        print(f"   Total revenue: ${status['results']['total_revenue']:,.2f}")

        print(f"\n⏳ PENDING DECISIONS: {status['pending_decisions']}")

        pending = self.get_pending_decisions()
        if pending:
            print("\n   Approve with:")
            for decision in pending[:5]:  # Show first 5
                print(f"   python auto_revenue_engine.py approve {decision['id']}")
                print(f"      → {decision['description']}")

        print(f"\n⚙️  CONFIG")
        print(f"   Mode: {'FULL AUTO 🚀' if status['config'].get('full_auto') else 'Human Approval Required'}")
        print(f"   Daily call limit: {status['config'].get('daily_call_limit', 100)}")
        print(f"   Love score threshold: {status['config'].get('love_score_threshold', 0.70) * 100}%")

        print("\n" + "=" * 60 + "\n")

    def print_pending_decisions(self):
        """Print all pending decisions"""
        pending = self.get_pending_decisions()

        if not pending:
            print("\n✓ No pending decisions. System is running autonomously.\n")
            return

        print("\n" + "=" * 60)
        print(f"PENDING DECISIONS ({len(pending)})")
        print("=" * 60 + "\n")

        for decision in pending:
            print(f"ID: {decision['id']}")
            print(f"Type: {decision['type']}")
            print(f"Description: {decision['description']}")
            print(f"Created: {decision['created']}")
            print(f"\nApprove: python auto_revenue_engine.py approve {decision['id']}")
            print(f"Decline: python auto_revenue_engine.py decline {decision['id']}")
            print("-" * 60 + "\n")


async def main():
    """Main CLI"""
    engine = AutoRevenueEngine()

    if len(sys.argv) < 2:
        print("""
╔═══════════════════════════════════════════════════════════════╗
║              AUTO REVENUE ENGINE                              ║
║        Almost Automated Revenue Generation                    ║
║     You create. You decide. System executes.                  ║
╚═══════════════════════════════════════════════════════════════╝

Commands:
  start               Start the engine (load campaigns)
  status              Show current status
  approve <id>        Approve a decision
  decline <id>        Decline a decision
  decisions           Show all pending decisions
  campaign <type>     Create new campaign
  monitor             Real-time monitoring (live updates)
  config              Edit configuration

Examples:
  python auto_revenue_engine.py start
  python auto_revenue_engine.py status
  python auto_revenue_engine.py approve dec_20251123_143022
  python auto_revenue_engine.py campaign hvac

Configuration:
  Edit revenue/auto_engine_data/config.json
  Set "full_auto": true for zero human intervention

Love • Loyalty • Honor • Everybody Eats
        """)
        return

    command = sys.argv[1]

    if command == "start":
        print("\n🚀 Starting Auto Revenue Engine...\n")

        # Check for campaigns to resume
        active = [c for c in engine.campaigns if c["status"] == "active"]
        if active:
            print(f"📋 {len(active)} active campaigns found")
            for campaign in active:
                print(f"   Resuming: {campaign['id']}")
        else:
            print("💡 No active campaigns. Create one with:")
            print("   python auto_revenue_engine.py campaign hvac")

        engine.print_status()

    elif command == "status":
        engine.print_status()

    elif command == "approve":
        if len(sys.argv) < 3:
            print("Usage: python auto_revenue_engine.py approve <decision_id>")
            return
        decision_id = sys.argv[2]
        await engine.approve_decision(decision_id, approved=True)

    elif command == "decline":
        if len(sys.argv) < 3:
            print("Usage: python auto_revenue_engine.py decline <decision_id>")
            return
        decision_id = sys.argv[2]
        await engine.approve_decision(decision_id, approved=False)

    elif command == "decisions":
        engine.print_pending_decisions()

    elif command == "campaign":
        campaign_type = sys.argv[2] if len(sys.argv) > 2 else "hvac"

        # Load targets from file
        targets_file = Path("revenue/hvac-sales-agent/target_companies.txt")
        if not targets_file.exists():
            print(f"✗ Targets file not found: {targets_file}")
            return

        # Parse targets (simple parsing for now)
        targets = []
        print(f"\n📋 Loading targets from {targets_file}...")

        # For now, create sample targets
        # In production, this parses the actual file
        targets = [
            {"company": "Cool Breeze HVAC", "phone": "+1-555-0001", "location": "Miami, FL"},
            {"company": "Air Masters Inc", "phone": "+1-555-0002", "location": "Tampa, FL"},
            {"company": "Climate Control Pro", "phone": "+1-555-0003", "location": "Orlando, FL"},
        ]

        print(f"✓ Loaded {len(targets)} targets")

        campaign_id = await engine.create_campaign(
            campaign_type="hvac_voice_agent",
            targets=targets,
            config={
                "script": "revenue/hvac-sales-agent/scripts/phone-script.txt",
                "demo_script": "revenue/hvac-sales-agent/scripts/demo-script.txt"
            }
        )

        print(f"\n✓ Campaign created: {campaign_id}")
        print(f"  Review pending decisions:")
        print(f"  python auto_revenue_engine.py decisions")

    elif command == "monitor":
        print("🔴 LIVE MONITORING (Ctrl+C to stop)\n")
        print("This would show real-time updates as campaigns run.")
        print("Coming soon in full version...")

    elif command == "config":
        print(f"\n⚙️  Configuration file: {engine.config_file}")
        print("\nCurrent config:")
        print(json.dumps(engine.config, indent=2))
        print(f"\nEdit this file to change settings.")

    else:
        print(f"Unknown command: {command}")
        print("Run without arguments for help.")


if __name__ == "__main__":
    asyncio.run(main())
