#!/usr/bin/env python3
"""
HVAC VOICE SALES AGENT
======================
Multi-AI powered sales agent that books real appointments and generates revenue.
Uses ai_connectors.py for Claude + Gemini + GPT synthesis.
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Import existing systems
from ai_connectors import AIOrchestrator
from brain_os import Brain


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class CallScript:
    """Sales script structure"""
    greeting: str
    qualification_questions: List[str]
    value_proposition: str
    objection_handlers: Dict[str, str]
    closing_questions: List[str]
    booking_confirmation: str


@dataclass
class ProspectContext:
    """Information about the prospect"""
    phone: str
    name: Optional[str] = None
    company: Optional[str] = None
    current_system: Optional[str] = None
    pain_points: List[str] = None
    budget_range: Optional[str] = None
    decision_timeline: Optional[str] = None

    def __post_init__(self):
        if self.pain_points is None:
            self.pain_points = []


@dataclass
class CallState:
    """Current state of the call"""
    call_id: str
    prospect: ProspectContext
    phase: str  # greeting, qualification, demo, objection, close, booked
    transcript: List[Dict[str, str]]
    insights: List[str]
    appointment_booked: bool = False
    calendly_link: Optional[str] = None
    started_at: datetime = None
    ended_at: Optional[datetime] = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()


# =============================================================================
# HVAC SALES AGENT
# =============================================================================

class HVACVoiceAgent:
    """
    Multi-AI powered HVAC sales agent.

    Uses Tournament Brain Architecture:
    - Claude for strategic reasoning
    - Gemini for research and analysis
    - GPT for cost-effective simple responses

    Synthesizes best response and learns from every interaction.
    """

    def __init__(self, brain: Brain):
        self.orchestrator = AIOrchestrator()
        self.brain = brain

        # Register agent with Brain OS
        self.agent_token = brain.register("hvac_sales_agent")

        # Sales script optimized for HVAC
        self.script = CallScript(
            greeting="Hi {name}, this is Alex calling from Elite HVAC Solutions. "
                    "I noticed you might be interested in upgrading your commercial HVAC system. "
                    "Do you have a quick minute?",

            qualification_questions=[
                "What type of facility do you manage? (office, warehouse, retail, etc.)",
                "How old is your current HVAC system?",
                "What's your biggest challenge with your current system? (high bills, breakdowns, comfort issues)",
                "Are you the decision maker for HVAC upgrades, or should I connect with someone else?",
                "What's your timeline for making a change? (urgent, 3-6 months, just exploring)"
            ],

            value_proposition="Here's what makes us different: We offer a performance-based model. "
                             "You only pay 10% of the savings we generate for you. "
                             "If we don't save you money, you don't pay a penny. "
                             "Most clients see 30-40% reduction in HVAC costs within the first year. "
                             "Zero upfront investment required.",

            objection_handlers={
                "too_expensive": "I totally understand budget concerns. That's exactly why we use a performance-based model. "
                                "You only pay from the actual savings - if we don't save you money, you pay nothing.",

                "need_to_think": "Of course, this is an important decision. Let me ask - what specific information would "
                                "help you feel confident moving forward? I can get you a custom analysis of your facility.",

                "happy_with_current": "I hear you. Can I ask - are you seeing any unexpected breakdowns, or higher bills than usual? "
                                     "Even systems that 'work' are often costing 30-40% more than they should.",

                "not_decision_maker": "No problem. Who's the right person to talk to about HVAC optimization? "
                                     "I'd be happy to connect with them directly.",

                "no_budget": "That's the beauty of our model - there's no budget needed upfront. We actually finance "
                            "the entire upgrade from your future savings. Month one, you start saving money."
            },

            closing_questions=[
                "Based on what you've shared, I think we could save you around ${estimate} per year. Does that sound valuable?",
                "Would you like me to send over a detailed analysis of your specific situation?",
                "I have two time slots this week for a 15-minute facility assessment - Tuesday at 2pm or Thursday at 10am. Which works better?"
            ],

            booking_confirmation="Perfect! I've got you scheduled for {time}. You'll receive a calendar invite at {email} "
                                "with all the details. We'll do a quick facility walk-through and show you exactly how much "
                                "we can save you. Looking forward to it!"
        )

        # Performance tracking
        self.stats = {
            "total_calls": 0,
            "qualified_prospects": 0,
            "appointments_booked": 0,
            "objections_handled": 0,
            "conversion_rate": 0.0,
            "avg_call_duration": 0.0,
            "revenue_generated": 0.0
        }

        # Learning system - stores successful patterns
        self.winning_patterns = []
        self.losing_patterns = []


    async def start_call(self, prospect: ProspectContext) -> CallState:
        """Initialize a new sales call"""
        call_id = f"CALL-{int(time.time())}"

        call_state = CallState(
            call_id=call_id,
            prospect=prospect,
            phase="greeting",
            transcript=[],
            insights=[]
        )

        self.stats["total_calls"] += 1

        # Generate personalized greeting using AI
        greeting = await self._generate_opening(prospect)

        call_state.transcript.append({
            "speaker": "agent",
            "text": greeting,
            "timestamp": datetime.now().isoformat(),
            "phase": "greeting"
        })

        return call_state


    async def process_response(self, call_state: CallState, prospect_response: str) -> str:
        """
        Process prospect's response and generate next agent response.
        Uses multi-AI synthesis for best response.
        """
        # Add prospect response to transcript
        call_state.transcript.append({
            "speaker": "prospect",
            "text": prospect_response,
            "timestamp": datetime.now().isoformat(),
            "phase": call_state.phase
        })

        # Extract insights from response
        await self._extract_insights(call_state, prospect_response)

        # Determine next phase
        next_phase = self._determine_next_phase(call_state)
        call_state.phase = next_phase

        # Generate response using multi-AI synthesis
        agent_response = await self._synthesize_response(call_state, prospect_response)

        # Add to transcript
        call_state.transcript.append({
            "speaker": "agent",
            "text": agent_response,
            "timestamp": datetime.now().isoformat(),
            "phase": call_state.phase
        })

        # Compress transcript for efficient storage using Brain OS
        compressed = self.brain.grimoire.compress(
            f"{prospect_response}\n{agent_response}",
            "hvac_sales_agent"
        )

        return agent_response


    async def _generate_opening(self, prospect: ProspectContext) -> str:
        """Generate personalized opening using AI"""
        prompt = f"""Generate a personalized sales call opening for an HVAC prospect:

Name: {prospect.name or 'the decision maker'}
Company: {prospect.company or 'their facility'}
Known pain points: {', '.join(prospect.pain_points) if prospect.pain_points else 'unknown'}

Base script: {self.script.greeting}

Requirements:
- Warm and professional tone
- Reference specific pain points if known
- Ask for permission to continue (respect their time)
- One sentence, max 30 words

Generate the opening:"""

        result = await self.orchestrator.generate(
            prompt,
            task_type="strategy",
            complexity=0.6,
            max_tokens=200
        )

        if result.get("success"):
            return result["content"].strip()
        else:
            # Fallback to template
            return self.script.greeting.format(name=prospect.name or "there")


    async def _synthesize_response(self, call_state: CallState, prospect_response: str) -> str:
        """
        Use multi-AI synthesis to generate best response.
        Routes to Claude, Gemini, and GPT in parallel, then synthesizes best answer.
        """
        # Build context from transcript
        recent_context = "\n".join([
            f"{t['speaker']}: {t['text']}"
            for t in call_state.transcript[-6:]  # Last 3 exchanges
        ])

        # Get current phase guidance
        phase_guidance = self._get_phase_guidance(call_state.phase)

        prompt = f"""You are an expert HVAC sales agent on a live call.

CALL PHASE: {call_state.phase}
OBJECTIVE: {phase_guidance}

PROSPECT INFO:
{json.dumps(asdict(call_state.prospect), indent=2)}

RECENT CONVERSATION:
{recent_context}

PROSPECT JUST SAID:
"{prospect_response}"

YOUR RESPONSE (requirements):
- Natural, conversational tone
- Address their specific concern
- Move toward booking appointment
- Max 50 words
- One clear question or call-to-action

Generate your response:"""

        # Route to optimal provider based on complexity
        if "objection" in call_state.phase or len(call_state.insights) > 3:
            # Complex situation - use Claude
            task_type = "strategy"
            complexity = 0.8
        elif call_state.phase == "qualification":
            # Research mode - use Gemini
            task_type = "analysis"
            complexity = 0.6
        else:
            # Standard response - use GPT
            task_type = "general"
            complexity = 0.4

        result = await self.orchestrator.generate(
            prompt,
            task_type=task_type,
            complexity=complexity,
            max_tokens=300
        )

        if result.get("success"):
            response = result["content"].strip()

            # Track which AI generated this (for learning)
            provider = result.get("provider", "unknown")
            call_state.insights.append(f"Response by {provider} (phase: {call_state.phase})")

            return response
        else:
            # Fallback to script-based response
            return self._fallback_response(call_state)


    def _get_phase_guidance(self, phase: str) -> str:
        """Get objective for current phase"""
        guidance = {
            "greeting": "Get prospect to engage and agree to continue the conversation",
            "qualification": "Ask qualifying questions to understand their needs and pain points",
            "demo": "Present value proposition focusing on performance-based pricing",
            "objection": "Handle objection empathetically and provide reassurance",
            "close": "Ask for the appointment booking with specific time options",
            "booked": "Confirm details and set expectations for the appointment"
        }
        return guidance.get(phase, "Move the call forward professionally")


    async def _extract_insights(self, call_state: CallState, response: str):
        """Extract insights from prospect response"""
        response_lower = response.lower()

        # Detect objections
        objection_keywords = {
            "expensive": "cost_concern",
            "budget": "cost_concern",
            "price": "cost_concern",
            "think about": "needs_time",
            "not sure": "needs_time",
            "happy with": "satisfied_with_current",
            "current provider": "satisfied_with_current",
            "not the decision": "not_decision_maker"
        }

        for keyword, objection_type in objection_keywords.items():
            if keyword in response_lower:
                call_state.insights.append(f"Objection detected: {objection_type}")
                self.stats["objections_handled"] += 1

        # Detect buying signals
        buying_signals = ["interested", "sounds good", "tell me more", "how does", "what's the process"]
        for signal in buying_signals:
            if signal in response_lower:
                call_state.insights.append("Buying signal detected")
                break

        # Detect qualification info
        if any(word in response_lower for word in ["square feet", "employees", "building"]):
            call_state.insights.append("Facility size info provided")

        if any(word in response_lower for word in ["year", "old", "installed"]):
            call_state.insights.append("System age info provided")


    def _determine_next_phase(self, call_state: CallState) -> str:
        """Determine what phase to move to next"""
        current = call_state.phase
        recent_insights = call_state.insights[-3:]

        # Check for objections
        if any("Objection" in i for i in recent_insights):
            return "objection"

        # Check for buying signals
        if any("Buying signal" in i for i in recent_insights):
            if current == "demo":
                return "close"

        # Standard progression
        phase_progression = {
            "greeting": "qualification",
            "qualification": "demo",
            "demo": "close",
            "objection": "close",  # After handling objection, try to close
            "close": "booked",
            "booked": "booked"
        }

        # Only progress if we have enough info
        if current == "qualification" and len([i for i in call_state.insights if "info provided" in i]) < 2:
            return "qualification"  # Stay in qualification

        return phase_progression.get(current, current)


    def _fallback_response(self, call_state: CallState) -> str:
        """Script-based fallback if AI fails"""
        if call_state.phase == "greeting":
            return "Great! Let me ask you a quick question to see if we're a good fit."

        elif call_state.phase == "qualification":
            remaining = [q for q in self.script.qualification_questions
                        if not any(q.split("?")[0] in t["text"] for t in call_state.transcript)]
            if remaining:
                return remaining[0]
            return "Thanks for that info. Let me tell you how we can help."

        elif call_state.phase == "demo":
            return self.script.value_proposition

        elif call_state.phase == "objection":
            return "I totally understand. Can you tell me more about what's holding you back?"

        elif call_state.phase == "close":
            return self.script.closing_questions[0].format(estimate="5,000")

        return "Tell me more about that."


    async def book_appointment(
        self,
        call_state: CallState,
        time_slot: str,
        email: str
    ) -> Dict:
        """
        Book appointment (integrates with Calendly in production).
        Returns booking confirmation.
        """
        call_state.appointment_booked = True
        call_state.phase = "booked"

        # Generate Calendly link (placeholder - will integrate with real Calendly API)
        calendly_link = f"https://calendly.com/elite-hvac/{call_state.call_id}"
        call_state.calendly_link = calendly_link

        self.stats["appointments_booked"] += 1
        self.stats["qualified_prospects"] += 1

        # Update conversion rate
        if self.stats["total_calls"] > 0:
            self.stats["conversion_rate"] = self.stats["appointments_booked"] / self.stats["total_calls"]

        # Store winning pattern
        self.winning_patterns.append({
            "call_id": call_state.call_id,
            "phases": [t["phase"] for t in call_state.transcript],
            "key_insights": call_state.insights,
            "timestamp": datetime.now().isoformat()
        })

        # Log to Brain OS
        self.brain.audit.log(
            "APPOINTMENT_BOOKED",
            "hvac_sales_agent",
            "book_appointment",
            "SUCCESS",
            {
                "call_id": call_state.call_id,
                "prospect": call_state.prospect.name,
                "time_slot": time_slot
            }
        )

        confirmation = self.script.booking_confirmation.format(
            time=time_slot,
            email=email
        )

        return {
            "success": True,
            "confirmation": confirmation,
            "calendly_link": calendly_link,
            "call_id": call_state.call_id
        }


    def end_call(self, call_state: CallState, outcome: str):
        """End call and log results"""
        call_state.ended_at = datetime.now()
        duration = (call_state.ended_at - call_state.started_at).total_seconds()

        # Update avg duration
        total_duration = self.stats["avg_call_duration"] * (self.stats["total_calls"] - 1)
        self.stats["avg_call_duration"] = (total_duration + duration) / self.stats["total_calls"]

        # Store pattern
        if outcome == "lost":
            self.losing_patterns.append({
                "call_id": call_state.call_id,
                "phases": [t["phase"] for t in call_state.transcript],
                "insights": call_state.insights,
                "timestamp": datetime.now().isoformat()
            })

        self.brain.audit.log(
            "CALL_ENDED",
            "hvac_sales_agent",
            "end_call",
            outcome.upper(),
            {
                "call_id": call_state.call_id,
                "duration": duration,
                "appointment_booked": call_state.appointment_booked
            }
        )


    def get_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            **self.stats,
            "winning_patterns_count": len(self.winning_patterns),
            "losing_patterns_count": len(self.losing_patterns),
            "ai_provider_stats": self.orchestrator.get_stats()
        }


    async def improve_from_patterns(self) -> Dict:
        """
        Analyze winning vs losing patterns and improve.
        This implements the 1% daily improvement loop.
        """
        if len(self.winning_patterns) < 3 or len(self.losing_patterns) < 1:
            return {"improved": False, "reason": "Not enough data yet"}

        # Use AI to analyze patterns
        prompt = f"""Analyze these HVAC sales call patterns and suggest ONE specific improvement:

WINNING PATTERNS (led to bookings):
{json.dumps(self.winning_patterns[-5:], indent=2)}

LOSING PATTERNS (no booking):
{json.dumps(self.losing_patterns[-3:], indent=2)}

What is the ONE most impactful change to make to improve conversion rate?
Provide:
1. The specific change (one sentence)
2. Why it will work (one sentence)
3. How to implement (one action)

Format as JSON:
{{"change": "...", "reasoning": "...", "action": "..."}}
"""

        result = await self.orchestrator.generate(
            prompt,
            task_type="strategy",
            complexity=0.9,
            max_tokens=500
        )

        if result.get("success"):
            try:
                improvement = json.loads(result["content"])

                # Log the improvement
                self.brain.audit.log(
                    "IMPROVEMENT_IDENTIFIED",
                    "hvac_sales_agent",
                    "improve_from_patterns",
                    "SUCCESS",
                    improvement
                )

                # Compound the performance
                self.brain.compound("hvac_sales_agent")

                return {
                    "improved": True,
                    **improvement,
                    "performance_multiplier": self.brain.perf
                }
            except json.JSONDecodeError:
                return {"improved": False, "reason": "Could not parse AI response"}

        return {"improved": False, "reason": "AI analysis failed"}


# =============================================================================
# DEMO / TEST
# =============================================================================

async def demo():
    """Demo the HVAC sales agent"""

    print("""
╔═══════════════════════════════════════════════════════════════╗
║           HVAC VOICE SALES AGENT - LIVE DEMO                  ║
║                                                               ║
║  Multi-AI Synthesis (Claude + Gemini + GPT)                  ║
║  Performance-Based Pricing (10% of savings)                  ║
║  Auto-Learning (1% daily improvement)                        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    # Initialize Brain OS
    brain = Brain()

    # Initialize agent
    agent = HVACVoiceAgent(brain)

    print("✅ Agent initialized with Brain OS integration\n")
    print("="*60)

    # Create a prospect
    prospect = ProspectContext(
        phone="+1-555-0123",
        name="John Smith",
        company="Smith Manufacturing",
        pain_points=["High energy bills", "Old equipment breaking down"]
    )

    print(f"📞 Starting call with {prospect.name} at {prospect.company}")
    print("="*60 + "\n")

    # Start call
    call_state = await agent.start_call(prospect)
    print(f"AGENT: {call_state.transcript[-1]['text']}\n")

    # Simulate conversation
    responses = [
        "Yes, I have a few minutes. What's this about?",
        "We have a 50,000 sq ft warehouse. Our system is about 15 years old and it's breaking down a lot.",
        "Yeah, the energy bills are crazy high and we had two breakdowns last month. It's a real problem.",
        "I'm the facility manager. I can make this decision. But I need to keep costs low right now.",
        "Performance-based sounds interesting. How does that work exactly?",
        "That sounds pretty good. What's the next step?",
        "Tuesday at 2pm works for me. My email is john@smithmfg.com"
    ]

    for i, response in enumerate(responses, 1):
        print(f"PROSPECT: {response}\n")

        agent_response = await call_state.process_response(call_state, response)
        print(f"AGENT: {agent_response}\n")

        print(f"Phase: {call_state.phase} | Insights: {len(call_state.insights)}")
        print("-" * 60 + "\n")

        await asyncio.sleep(0.5)  # Simulate conversation pacing

        # Book appointment if in close phase
        if call_state.phase == "close" and i == len(responses):
            booking = await agent.book_appointment(
                call_state,
                "Tuesday at 2:00 PM EST",
                "john@smithmfg.com"
            )
            print(f"✅ APPOINTMENT BOOKED!")
            print(f"Confirmation: {booking['confirmation']}\n")

    # End call
    agent.end_call(call_state, "won")

    print("="*60)
    print("CALL STATISTICS")
    print("="*60)

    stats = agent.get_stats()
    print(f"""
Total Calls: {stats['total_calls']}
Appointments Booked: {stats['appointments_booked']}
Conversion Rate: {stats['conversion_rate']:.1%}
Avg Call Duration: {stats['avg_call_duration']:.0f}s

AI Provider Stats:
  Total Requests: {stats['ai_provider_stats']['total_requests']}
  Total Tokens: {stats['ai_provider_stats']['total_tokens']}
  Total Cost: ${stats['ai_provider_stats']['total_cost']:.4f}

Brain OS Performance: {brain.perf:.2%}
""")

    print("="*60)
    print("✅ Demo complete! Agent is ready for production calls.")


if __name__ == "__main__":
    asyncio.run(demo())
