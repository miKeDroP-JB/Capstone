"""
VAPI Agent Sparring System - Orchestration Module

Automates the complete sparring training loop:
1. Selects prospect types based on training progress
2. Initiates agent-to-agent calls via VAPI
3. Captures transcripts
4. Scores with referee
5. Updates meta-brain
6. Tracks certification progress
"""

import random
import time
import json
from typing import Dict, List, Optional
from datetime import datetime
from sparring_referee import SparringReferee


class VapiClient:
    """
    Mock VAPI client - replace with actual VAPI SDK when available
    In production, use: from vapi import VapiClient
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        print(f"[MOCK] VapiClient initialized with key: {api_key[:10]}...")

    def create_call(
        self,
        assistant_id: str,
        customer_number: str,
        max_duration: int = 300
    ) -> 'MockCall':
        print(f"[MOCK] Creating call: {assistant_id} -> {customer_number}")
        return MockCall(assistant_id, customer_number, max_duration)

    def get_call(self, call_id: str) -> 'MockCall':
        print(f"[MOCK] Getting call status: {call_id}")
        return MockCall("", "", 0, status="completed")


class MockCall:
    """Mock call object for testing"""

    def __init__(
        self,
        assistant_id: str,
        customer_number: str,
        max_duration: int,
        status: str = "in_progress"
    ):
        self.id = f"call_{datetime.now().timestamp()}"
        self.assistant_id = assistant_id
        self.customer_number = customer_number
        self.max_duration = max_duration
        self.status = status
        self.transcript = self._generate_mock_transcript()

    def _generate_mock_transcript(self) -> str:
        """Generate realistic mock transcript for testing"""
        return """Sales Agent: Hey! Thanks for taking my call. I'm calling because we're doing something pretty wild right now - I can actually clone your voice and build you a working AI agent while we're on this call. Takes about 5 minutes. Have you got a second to see how it works?

Prospect: I'm not interested in sales calls.

Sales Agent: I totally get it - and this isn't really a sales call in the traditional sense. What if I told you I could prove this works in the next 60 seconds? Would you give me one minute before hanging up?

Prospect: One minute.

Sales Agent: Perfect. What business are you in?

Prospect: Real estate.

Sales Agent: Great. How many leads do you need to follow up with every week?

Prospect: Probably 50-100.

Sales Agent: And how many of those do you actually get to personally?

Prospect: Maybe 20-30 if I'm lucky.

Sales Agent: So you're leaving 70 leads on the table every week. At even a 5% conversion rate, that's 3-4 deals you're missing every week. What's a deal worth to you?

Prospect: Commission is usually around $8,000-12,000.

Sales Agent: So you're potentially leaving $30-40K on the table every week just because you can't follow up with everyone. What if I could build you an AI agent that sounds exactly like you, follows up with every single lead within 5 minutes, books appointments directly to your calendar, and you only pay if it actually books appointments? Would that be worth 5 more minutes?

Prospect: Yeah, I'm listening. How does this work?

Sales Agent: I can demo it right now. I'll clone your voice on this call - takes about 90 seconds. Then I'll deploy a test agent and you'll hear it making a call. If you like what you hear, we book a full setup call. If not, no harm done. Ready?

Prospect: Sure, go ahead.

Sales Agent: Awesome. I'm going to ask you to read a few sentences so the system can capture your voice...

[Voice cloning process happens]

Sales Agent: Done! The agent is deploying now. Let me play you a sample of it making an outbound call to one of your leads...

[Demo plays]

Prospect: Wow, that actually sounds really good. What's the pricing?

Sales Agent: So here's the deal - and this is why I wanted to show you first instead of just talking about it. The setup is $500 one-time. Then it's performance-based: if the agent books less than $5,000 worth of appointments in the first month, the $500 is refunded. You literally can't lose.

Prospect: And what about ongoing costs?

Sales Agent: $0.10 per call minute, which averages $1-3 per appointment booked. So if it books you 20 appointments in a month, you're paying maybe $40 in call time to get $160K+ in pipeline.

Prospect: That's actually pretty reasonable. What's the next step?

Sales Agent: I'm going to send you a calendar link right now. Book a 30-minute setup call with me - we'll clone your voice properly, connect it to your CRM, and have it live within 24 hours. Sound good?

Prospect: Yeah, send it over.

Sales Agent: Perfect! Link coming to your email in 30 seconds. And hey, congrats on being open-minded enough to actually listen - most people hang up and keep leaving money on the table. Talk soon!

Prospect: Thanks, appreciate it."""


class SparringOrchestrator:
    """
    Main orchestration class for automated sparring training
    """

    def __init__(self, vapi_api_key: str, anthropic_api_key: Optional[str] = None):
        self.vapi = VapiClient(api_key=vapi_api_key)
        self.referee = SparringReferee(api_key=anthropic_api_key)

        # Agent IDs from VAPI (fill these in after creating agents in VAPI dashboard)
        self.sales_agent_id = "SALES_AGENT_ID"  # TODO: Replace with actual VAPI agent ID
        self.prospect_agents = {
            "Eager Eddie": "EDDIE_AGENT_ID",
            "Skeptical Sarah": "SARAH_AGENT_ID",
            "Price Paul": "PAUL_AGENT_ID",
            "Busy Barbara": "BARBARA_AGENT_ID",
            "Technical Tom": "TOM_AGENT_ID",
            "Comparison Charlie": "CHARLIE_AGENT_ID",
            "Hostile Henry": "HENRY_AGENT_ID"
        }

        self.score_history = []
        self.cycle_count = 0
        self.training_start_time = datetime.now()

    def configure_agent_ids(
        self,
        sales_agent_id: str,
        prospect_agents: Dict[str, str]
    ):
        """
        Configure VAPI agent IDs after they've been created

        Args:
            sales_agent_id: VAPI ID for the sales agent
            prospect_agents: Dictionary mapping prospect names to VAPI IDs
        """
        self.sales_agent_id = sales_agent_id
        self.prospect_agents = prospect_agents

    def select_prospect_type(self) -> str:
        """
        Intelligently select prospect type based on training progress

        Returns:
            Prospect type name
        """

        # Early training (cycles 1-10): Easier prospects
        if self.cycle_count < 10:
            prospects = ["Eager Eddie", "Technical Tom"]
            return random.choice(prospects)

        # Mid training (cycles 11-30): Mixed difficulty
        elif self.cycle_count < 30:
            prospects = list(self.prospect_agents.keys())[:-1]  # Exclude Hostile Henry
            return random.choice(prospects)

        # Advanced training (cycles 31+): All prospects including hardest
        else:
            # Weight harder prospects more heavily
            prospects = list(self.prospect_agents.keys())
            weights = [1, 2, 2, 2, 2, 2, 3]  # Henry gets 3x weight
            return random.choices(prospects, weights=weights)[0]

    def run_sparring_cycle(self) -> bool:
        """
        Executes one complete sparring cycle

        Returns:
            True if agent is certified, False otherwise
        """

        # Select prospect
        prospect_type = self.select_prospect_type()
        prospect_agent_id = self.prospect_agents.get(prospect_type, "MOCK_ID")

        print(f"\n{'='*60}")
        print(f"SPARRING CYCLE #{self.cycle_count + 1}")
        print(f"Opponent: {prospect_type}")
        print(f"Time elapsed: {(datetime.now() - self.training_start_time).total_seconds() / 60:.1f} minutes")
        print(f"{'='*60}\n")

        # Initiate call
        print("📞 Initiating agent-to-agent call...")
        call = self.vapi.create_call(
            assistant_id=self.sales_agent_id,
            customer_number=prospect_agent_id,
            max_duration=300  # 5 minute max
        )

        # Wait for call to complete
        print("⏳ Call in progress...")
        max_wait = 60  # Maximum 60 seconds wait for mock
        waited = 0

        while call.status != "completed" and waited < max_wait:
            time.sleep(2)
            waited += 2
            call = self.vapi.get_call(call.id)
            print(f"   Status: {call.status} ({waited}s)")

        if call.status != "completed":
            print("⚠️  Call timeout - using partial transcript")

        # Get transcript
        transcript = call.transcript
        print(f"\n📝 Transcript captured ({len(transcript)} characters)")

        # Referee analysis
        print("\n🔍 Analyzing call with referee...")
        analysis = self.referee.analyze_call(
            transcript=transcript,
            prospect_type=prospect_type,
            call_id=f"spar_{self.cycle_count + 1:03d}"
        )

        # Update meta-brain
        print("🧠 Updating meta-brain...")
        self.referee.update_meta_brain(analysis, transcript)

        # Track score
        total_score = analysis.get('total_score', 0)
        self.score_history.append(total_score)

        # Print results
        self._print_results(analysis, prospect_type)

        # Check certification
        cert_status = self.referee.check_certification(self.score_history)

        if cert_status["certified"]:
            self._print_certification(cert_status)
            return True
        else:
            self._print_progress(cert_status)

        self.cycle_count += 1
        return False

    def run_until_certified(self, max_cycles: int = 100) -> bool:
        """
        Runs sparring cycles until agent is certified or max cycles reached

        Args:
            max_cycles: Maximum number of training cycles

        Returns:
            True if certified, False if max cycles reached
        """

        print("\n" + "="*60)
        print("SPARRING TRAINING INITIATED")
        print(f"Target: {self.referee.certification_threshold}+ points average over {self.referee.required_consecutive_passes} consecutive calls")
        print(f"Max cycles: {max_cycles}")
        print("="*60 + "\n")

        while self.cycle_count < max_cycles:
            certified = self.run_sparring_cycle()

            if certified:
                self._print_training_complete()
                return True

            # Brief pause between cycles
            print("\n⏸️  Pausing 5 seconds before next cycle...\n")
            time.sleep(5)

        # Max cycles reached without certification
        self._print_training_incomplete(max_cycles)
        return False

    def generate_final_report(self) -> Dict:
        """
        Generates comprehensive final training report

        Returns:
            Report dictionary
        """

        base_report = self.referee.generate_performance_report()

        final_report = {
            **base_report,
            "training_duration_minutes": (datetime.now() - self.training_start_time).total_seconds() / 60,
            "total_cycles": self.cycle_count,
            "final_scores": self.score_history[-10:] if len(self.score_history) >= 10 else self.score_history,
            "certification_status": self.referee.check_certification(self.score_history)
        }

        return final_report

    # Private helper methods for pretty printing

    def _print_results(self, analysis: Dict, prospect_type: str):
        """Print cycle results"""
        print(f"\n📊 RESULTS:")
        print(f"   Score: {analysis.get('total_score', 'N/A')}/50")
        print(f"   Would Convert: {analysis.get('would_convert', 'N/A')} ({analysis.get('confidence_percent', 'N/A')}% confidence)")

        print(f"\n✅ Winning Patterns:")
        for pattern in analysis.get("winning_patterns", []):
            print(f"   - {pattern}")

        print(f"\n❌ Losing Patterns:")
        for pattern in analysis.get("losing_patterns", []):
            print(f"   - {pattern}")

        if analysis.get('script_adjustments'):
            print(f"\n💡 Suggested Adjustments:")
            for adj in analysis['script_adjustments'][:3]:
                print(f"   - {adj}")

    def _print_progress(self, cert_status: Dict):
        """Print progress toward certification"""
        print(f"\n⏳ CERTIFICATION PROGRESS:")
        print(f"   {cert_status.get('reason', 'Unknown')}")
        print(f"   Average: {cert_status.get('average_score', 0):.1f}/50")

        if 'gap' in cert_status:
            print(f"   Gap to threshold: {cert_status['gap']:.1f} points")

        if 'scores_needed' in cert_status:
            print(f"   Scores needed: {cert_status['scores_needed']}")

    def _print_certification(self, cert_status: Dict):
        """Print certification success"""
        print(f"\n🎯 {cert_status.get('message', 'CERTIFIED')}")
        print(f"\n{'='*60}")
        print("AGENT READY FOR PRODUCTION DEPLOYMENT")
        print(f"{'='*60}")

    def _print_training_complete(self):
        """Print training completion message"""
        duration = (datetime.now() - self.training_start_time).total_seconds() / 60

        print(f"\n🚀 TRAINING COMPLETE - AGENT CERTIFIED FOR DEPLOYMENT")
        print(f"\n📈 FINAL STATS:")
        print(f"   Total cycles: {self.cycle_count}")
        print(f"   Training duration: {duration:.1f} minutes")
        print(f"   Final average: {sum(self.score_history[-10:])/min(10, len(self.score_history)):.1f}/50")
        print(f"   Peak score: {max(self.score_history)}/50")

    def _print_training_incomplete(self, max_cycles: int):
        """Print training incomplete message"""
        print(f"\n⚠️  Reached max cycles ({max_cycles}) without certification")

        if len(self.score_history) >= 10:
            avg = sum(self.score_history[-10:]) / 10
            print(f"   Final 10-call average: {avg:.1f}/50")
            print(f"   Gap to certification: {self.referee.certification_threshold - avg:.1f} points")

        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   - Review meta-brain losing patterns")
        print(f"   - Adjust sales agent prompt based on feedback")
        print(f"   - Consider extending training with more cycles")


# CLI Interface
if __name__ == "__main__":
    import sys

    print("="*60)
    print("VAPI AGENT SPARRING SYSTEM")
    print("="*60)

    # Initialize orchestrator
    orchestrator = SparringOrchestrator(
        vapi_api_key="your_vapi_key_here",
        anthropic_api_key=None  # Uses ANTHROPIC_API_KEY env var
    )

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "single":
            # Run single cycle for testing
            print("\n🧪 Running single test cycle...")
            orchestrator.run_sparring_cycle()

        elif sys.argv[1] == "train":
            # Run full training
            max_cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            orchestrator.run_until_certified(max_cycles=max_cycles)

            # Generate final report
            report = orchestrator.generate_final_report()
            print("\n📄 Saving final report...")

            with open("final_training_report.json", "w") as f:
                json.dump(report, f, indent=2)

            print("✅ Report saved to: final_training_report.json")

        elif sys.argv[1] == "report":
            # Generate report from existing data
            report = orchestrator.referee.generate_performance_report()
            print(json.dumps(report, indent=2))

    else:
        print("\nUsage:")
        print("  python sparring_orchestrator.py single       # Run one test cycle")
        print("  python sparring_orchestrator.py train [N]    # Train until certified (max N cycles)")
        print("  python sparring_orchestrator.py report       # Generate performance report")
        print("\nExample:")
        print("  python sparring_orchestrator.py train 50")
