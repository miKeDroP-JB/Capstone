#!/usr/bin/env python3
"""
SALES BRAIN - AI Sales Intelligence Engine
Handles conversations, objections, scripts, and sentiment.

The brain that knows HVAC better than any human could.
Never forgets. Never gets tired. Always on script.

Love - Loyalty - Honor - Everybody Eats
"""

import asyncio
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

class ConversationState(Enum):
    """Current state of the sales conversation"""
    INTRO = "intro"
    DISCOVERY = "discovery"
    PITCH = "pitch"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    BOOKING = "booking"
    FOLLOWUP = "followup"
    ENDED = "ended"


class Sentiment(Enum):
    """Detected sentiment"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


class ObjectionType(Enum):
    """Types of sales objections"""
    PRICE = "price"
    TIMING = "timing"
    TRUST = "trust"
    NEED = "need"
    AUTHORITY = "authority"
    COMPETITION = "competition"
    STATUS_QUO = "status_quo"


@dataclass
class Objection:
    """A sales objection with handling strategies"""
    type: ObjectionType
    pattern: str  # Regex pattern to detect
    examples: List[str]
    responses: List[str]  # Multiple response options
    followup: str


@dataclass
class Script:
    """A sales script segment"""
    id: str
    name: str
    state: ConversationState
    text: str
    variables: List[str]  # Placeholders to fill
    branches: Dict[str, str]  # condition -> next_script_id
    ai_prompt: str = ""  # Prompt for AI to generate variations


@dataclass
class ConversationTurn:
    """A single turn in the conversation"""
    speaker: str  # "agent" or "prospect"
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    sentiment: Sentiment = Sentiment.NEUTRAL
    detected_objection: Optional[ObjectionType] = None
    intent: str = ""


@dataclass
class Conversation:
    """Full conversation history"""
    id: str
    lead_id: str
    lead_name: str
    industry: str
    state: ConversationState = ConversationState.INTRO
    turns: List[ConversationTurn] = field(default_factory=list)
    objections_raised: List[ObjectionType] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    outcome: str = ""  # "booked", "callback", "not_interested", "voicemail"
    notes: str = ""


# ═══════════════════════════════════════════════════════════════
# HVAC-SPECIFIC KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════

HVAC_KNOWLEDGE = {
    "services": {
        "ac_repair": {
            "name": "AC Repair",
            "common_issues": ["not cooling", "making noise", "leaking", "high bills"],
            "urgency": "high",
            "average_ticket": "$150-500",
        },
        "ac_installation": {
            "name": "AC Installation",
            "common_needs": ["old unit", "new construction", "upgrade"],
            "urgency": "medium",
            "average_ticket": "$3,000-7,000",
        },
        "heating_repair": {
            "name": "Heating Repair",
            "common_issues": ["no heat", "strange smells", "pilot light", "thermostat"],
            "urgency": "high",
            "average_ticket": "$150-500",
        },
        "maintenance": {
            "name": "HVAC Maintenance",
            "benefits": ["prevent breakdowns", "lower bills", "extend life"],
            "urgency": "low",
            "average_ticket": "$100-200",
        },
    },
    "seasons": {
        "summer": {
            "peak_services": ["ac_repair", "ac_installation"],
            "urgency_multiplier": 1.5,
            "common_complaints": ["AC not cooling", "high electric bills", "humidity"],
        },
        "winter": {
            "peak_services": ["heating_repair"],
            "urgency_multiplier": 1.5,
            "common_complaints": ["No heat", "furnace noise", "cold spots"],
        },
        "spring": {
            "peak_services": ["maintenance", "ac_installation"],
            "urgency_multiplier": 1.0,
            "selling_points": ["Get ready for summer", "Prevent breakdowns"],
        },
        "fall": {
            "peak_services": ["maintenance", "heating_repair"],
            "urgency_multiplier": 1.0,
            "selling_points": ["Get ready for winter", "Heating tune-up"],
        },
    },
    "objection_knowledge": {
        "price": "HVAC repairs cost more when they become emergencies. Prevention saves money.",
        "timing": "We offer flexible scheduling including evenings and weekends.",
        "trust": "We're licensed, bonded, insured with a 100% satisfaction guarantee.",
        "competition": "We focus on quality and standing behind our work, not being the cheapest.",
    },
}


# ═══════════════════════════════════════════════════════════════
# OBJECTION LIBRARY
# ═══════════════════════════════════════════════════════════════

OBJECTIONS: Dict[ObjectionType, Objection] = {
    ObjectionType.PRICE: Objection(
        type=ObjectionType.PRICE,
        pattern=r"(too expensive|cost|price|afford|budget|money|cheap)",
        examples=[
            "How much does this cost?",
            "That's too expensive",
            "We don't have the budget",
            "Can you do it cheaper?",
        ],
        responses=[
            "I totally understand. Here's the thing - you only pay if we deliver results. We take 10% of what we generate, you keep 90%. If we don't make you money, you don't pay. Fair?",
            "Price is definitely important. That's why we structured it so there's zero risk to you. We only get paid when you get paid. Can I show you how that works?",
            "I hear you. Most of our clients felt the same way until they realized they were already losing money on missed calls. We're not a cost - we're revenue you're not currently capturing.",
        ],
        followup="What if I could show you how this pays for itself in the first week?",
    ),

    ObjectionType.TIMING: Objection(
        type=ObjectionType.TIMING,
        pattern=r"(busy|not now|later|bad time|call back|next month|next year)",
        examples=[
            "Now's not a good time",
            "We're really busy right now",
            "Call me back next month",
            "We're in our busy season",
        ],
        responses=[
            "I totally get it - busy season means more calls you're missing. That's exactly why this makes sense now. The AI handles calls while you focus on the work. Make sense?",
            "Perfect - busy is actually the best time to set this up. While you're slammed, the AI is booking appointments for your slow season. Should I show you how quick the setup is?",
            "I hear you. Quick question though - if you're busy, who's answering the phone when you're on a job site?",
        ],
        followup="What if we could have this running by tomorrow without any work on your end?",
    ),

    ObjectionType.TRUST: Objection(
        type=ObjectionType.TRUST,
        pattern=r"(trust|believe|scam|legit|real|proof|guarantee)",
        examples=[
            "How do I know this is legit?",
            "I've been burned before",
            "Do you have any proof this works?",
            "What's the guarantee?",
        ],
        responses=[
            "Smart to be skeptical. Here's what I can offer: a free 3-day trial. No credit card, no commitment. You hear the calls, see the results, then decide. Fair enough?",
            "I respect that. We have case studies I can send, but honestly? Just try it for 3 days free. If it's not amazing, we shake hands and part friends.",
            "That's exactly the right question. We're so confident it works that we don't ask for payment until you've seen results. Zero risk on your end.",
        ],
        followup="Want me to set up that free trial so you can see it yourself?",
    ),

    ObjectionType.NEED: Objection(
        type=ObjectionType.NEED,
        pattern=r"(don't need|already have|we're fine|not interested|no need)",
        examples=[
            "We don't need that",
            "We already have someone answering phones",
            "We're doing fine without it",
            "Not interested",
        ],
        responses=[
            "Totally understand. Quick question - what happens to calls that come in after 5pm or when your team is on job sites?",
            "Got it. Out of curiosity, do you know how many calls you missed last month? Most HVAC companies don't realize it's 30-40%.",
            "Fair enough. Mind if I ask - when a homeowner's AC breaks at 10pm, where does that lead go? To you or your competitor who answers?",
        ],
        followup="What if I could show you exactly how many leads you're missing? No obligation, just data.",
    ),

    ObjectionType.AUTHORITY: Objection(
        type=ObjectionType.AUTHORITY,
        pattern=r"(partner|owner|boss|wife|husband|talk to|decide|decision)",
        examples=[
            "I need to talk to my partner",
            "I'm not the decision maker",
            "Let me check with my wife",
            "The owner isn't here",
        ],
        responses=[
            "Absolutely, makes sense. When do you think you'll connect with them? I can send over some info they can review and we can do a quick call together.",
            "Totally understand. Would it help if I was on the call to answer any questions they might have? I can explain the no-risk trial.",
            "Smart to include them. What do you think their biggest concern would be? Maybe I can address it now so you have answers for them.",
        ],
        followup="Can we schedule a time when you're both available? Even just 10 minutes.",
    ),

    ObjectionType.COMPETITION: Objection(
        type=ObjectionType.COMPETITION,
        pattern=r"(competitor|other company|already using|someone else|different service)",
        examples=[
            "We're already using another service",
            "Your competitor called yesterday",
            "We have something similar",
        ],
        responses=[
            "Good, so you already see the value. Quick question - what made you go with them, and how's it working out?",
            "Nice, you're ahead of most companies then. Mind if I ask what you're paying and what results you're getting? Just to compare.",
            "Smart move having something in place. Most of our clients switched from competitors because of our results-based pricing. You only pay when you get paid.",
        ],
        followup="Would you be open to a side-by-side comparison? No pressure, just data.",
    ),

    ObjectionType.STATUS_QUO: Objection(
        type=ObjectionType.STATUS_QUO,
        pattern=r"(been doing|always done|works for us|happy with|current)",
        examples=[
            "We've always done it this way",
            "Our current system works fine",
            "We're happy with how things are",
        ],
        responses=[
            "I respect that - if it ain't broke, right? But here's the thing - your competitors are starting to use AI. The question isn't if you'll need this, but when.",
            "Makes sense. Out of curiosity though - are you capturing every single lead, or is some revenue slipping through the cracks?",
            "Totally get it. The companies dominating right now aren't the ones doing things the old way though. Want to at least see what's possible?",
        ],
        followup="What would need to change for you to consider something new?",
    ),
}


# ═══════════════════════════════════════════════════════════════
# SCRIPTS LIBRARY
# ═══════════════════════════════════════════════════════════════

HVAC_SCRIPTS: Dict[str, Script] = {
    "intro_cold": Script(
        id="intro_cold",
        name="Cold Call Intro",
        state=ConversationState.INTRO,
        text="""Hey {first_name}, this is {agent_name}. I know I'm calling out of the blue, and I apologize for that - but I just finished building something that's gonna change how HVAC companies get customers, and I wanted to offer it to a few pilots in {city} before we open it up. Got 2 minutes?""",
        variables=["first_name", "agent_name", "city"],
        branches={
            "yes": "pitch_main",
            "no": "soft_close",
            "busy": "callback_request",
        },
    ),

    "pitch_main": Script(
        id="pitch_main",
        name="Main Pitch",
        state=ConversationState.PITCH,
        text="""Here's what I built: An AI sales rep that finds homeowners in {city} who need HVAC work and calls them automatically. It books appointments or closes sales directly into your calendar.

It knows HVAC better than any human - every objection, every competitor, the whole industry. Doesn't eat, doesn't sleep, doesn't take holidays. Works 24/7 if you want.

Here's the deal: Small monthly retainer to keep everyone committed. But everything - including the retainer - comes out of a 10% commission on what the system generates. You keep 90%.

End of 30 days, we send you a check for thousands, minus our 10%. I've got 3 pilot spots left. You want one?""",
        variables=["city"],
        branches={
            "yes": "booking",
            "objection": "handle_objection",
            "question": "answer_question",
        },
    ),

    "trial_offer": Script(
        id="trial_offer",
        name="Free Trial Offer",
        state=ConversationState.CLOSING,
        text="""Tell you what - let's do a free 3-day trial. No credit card, no commitment, no strings. Let the AI make some calls, you hear the quality, see the appointments booked. If you don't absolutely love it, we shake hands and part friends. Fair?""",
        variables=[],
        branches={
            "yes": "booking",
            "no": "final_attempt",
        },
    ),

    "booking": Script(
        id="booking",
        name="Booking Confirmation",
        state=ConversationState.BOOKING,
        text="""Perfect! Let me get you set up. What email should I send the onboarding to? And what's the best number for the AI to forward hot leads to?""",
        variables=[],
        branches={
            "info_given": "confirmation",
        },
    ),

    "confirmation": Script(
        id="confirmation",
        name="Close Confirmation",
        state=ConversationState.ENDED,
        text="""Awesome {first_name}. You're gonna love this. I'm sending everything now - look for an email from 0RB. Any questions before I let you go?

Welcome aboard. Let's make you some money.""",
        variables=["first_name"],
        branches={},
    ),
}


# ═══════════════════════════════════════════════════════════════
# SALES BRAIN
# ═══════════════════════════════════════════════════════════════

class SalesBrain:
    """
    The AI sales brain.
    Handles conversations, detects objections, selects responses.
    Knows HVAC better than any human.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.knowledge = HVAC_KNOWLEDGE
        self.objections = OBJECTIONS
        self.scripts = HVAC_SCRIPTS
        self.conversations: Dict[str, Conversation] = {}

    # ═══════════════════════════════════════════════════════════
    # CONVERSATION MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def start_conversation(
        self,
        lead_id: str,
        lead_name: str,
        industry: str = "hvac",
    ) -> Conversation:
        """Start a new sales conversation"""
        conv_id = f"conv_{lead_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        conversation = Conversation(
            id=conv_id,
            lead_id=lead_id,
            lead_name=lead_name,
            industry=industry,
        )

        self.conversations[conv_id] = conversation
        return conversation

    def add_turn(
        self,
        conversation: Conversation,
        speaker: str,
        text: str,
    ) -> ConversationTurn:
        """Add a turn to the conversation"""
        # Analyze the turn
        sentiment = self._analyze_sentiment(text)
        objection = self._detect_objection(text)
        intent = self._detect_intent(text)

        turn = ConversationTurn(
            speaker=speaker,
            text=text,
            sentiment=sentiment,
            detected_objection=objection,
            intent=intent,
        )

        conversation.turns.append(turn)

        if objection and objection not in conversation.objections_raised:
            conversation.objections_raised.append(objection)

        return turn

    def end_conversation(
        self,
        conversation: Conversation,
        outcome: str,
        notes: str = "",
    ):
        """End a conversation with outcome"""
        conversation.ended_at = datetime.now()
        conversation.outcome = outcome
        conversation.notes = notes
        conversation.state = ConversationState.ENDED

    # ═══════════════════════════════════════════════════════════
    # RESPONSE GENERATION
    # ═══════════════════════════════════════════════════════════

    def get_response(
        self,
        conversation: Conversation,
        prospect_input: str,
        context: Dict[str, Any] = None,
    ) -> Tuple[str, ConversationState]:
        """
        Generate the best response to prospect input.
        Returns (response_text, new_state)
        """
        context = context or {}

        # Add the prospect's turn
        turn = self.add_turn(conversation, "prospect", prospect_input)

        # Check for objection
        if turn.detected_objection:
            response = self._handle_objection(turn.detected_objection)
            conversation.state = ConversationState.OBJECTION_HANDLING
            return response, conversation.state

        # Check for booking signals
        if self._is_buying_signal(prospect_input):
            conversation.state = ConversationState.BOOKING
            script = self.scripts["booking"]
            return script.text, conversation.state

        # Check for positive response
        if turn.sentiment in [Sentiment.POSITIVE, Sentiment.VERY_POSITIVE]:
            return self._advance_conversation(conversation, context)

        # Check for negative/ending signals
        if self._is_ending_signal(prospect_input):
            # Try trial offer before giving up
            if "trial" not in [t.text for t in conversation.turns]:
                script = self.scripts["trial_offer"]
                return script.text, ConversationState.CLOSING

        # Default: continue with current state
        return self._get_state_response(conversation, context)

    def _handle_objection(self, objection_type: ObjectionType) -> str:
        """Get response for specific objection"""
        objection = self.objections.get(objection_type)
        if objection:
            # Rotate through responses
            import random
            response = random.choice(objection.responses)
            return f"{response}\n\n{objection.followup}"
        return "I understand your concern. Tell me more about that."

    def _advance_conversation(
        self,
        conversation: Conversation,
        context: Dict[str, Any],
    ) -> Tuple[str, ConversationState]:
        """Move conversation to next stage"""
        state_progression = {
            ConversationState.INTRO: ConversationState.PITCH,
            ConversationState.PITCH: ConversationState.CLOSING,
            ConversationState.OBJECTION_HANDLING: ConversationState.CLOSING,
            ConversationState.CLOSING: ConversationState.BOOKING,
            ConversationState.BOOKING: ConversationState.ENDED,
        }

        next_state = state_progression.get(conversation.state, conversation.state)
        conversation.state = next_state

        return self._get_state_response(conversation, context)

    def _get_state_response(
        self,
        conversation: Conversation,
        context: Dict[str, Any],
    ) -> Tuple[str, ConversationState]:
        """Get response based on current state"""
        state_scripts = {
            ConversationState.INTRO: "intro_cold",
            ConversationState.PITCH: "pitch_main",
            ConversationState.CLOSING: "trial_offer",
            ConversationState.BOOKING: "booking",
            ConversationState.ENDED: "confirmation",
        }

        script_id = state_scripts.get(conversation.state)
        if script_id and script_id in self.scripts:
            script = self.scripts[script_id]
            text = self._fill_script_variables(script.text, context)
            return text, conversation.state

        return "Tell me more about your business.", conversation.state

    def _fill_script_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Fill in script variables from context"""
        for key, value in context.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    # ═══════════════════════════════════════════════════════════
    # ANALYSIS
    # ═══════════════════════════════════════════════════════════

    def _analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of text"""
        text_lower = text.lower()

        very_positive = ["absolutely", "definitely", "love", "perfect", "amazing", "yes please", "sign me up"]
        positive = ["yes", "sure", "okay", "sounds good", "interested", "tell me more"]
        negative = ["no", "not interested", "busy", "don't", "can't", "won't"]
        very_negative = ["stop", "don't call", "remove", "scam", "hang up", "go away"]

        if any(word in text_lower for word in very_positive):
            return Sentiment.VERY_POSITIVE
        elif any(word in text_lower for word in very_negative):
            return Sentiment.VERY_NEGATIVE
        elif any(word in text_lower for word in positive):
            return Sentiment.POSITIVE
        elif any(word in text_lower for word in negative):
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL

    def _detect_objection(self, text: str) -> Optional[ObjectionType]:
        """Detect objection type from text"""
        text_lower = text.lower()

        for obj_type, objection in self.objections.items():
            if re.search(objection.pattern, text_lower):
                return obj_type

        return None

    def _detect_intent(self, text: str) -> str:
        """Detect prospect's intent"""
        text_lower = text.lower()

        intents = {
            "buy": ["sign up", "let's do it", "i'm in", "start", "book"],
            "question": ["how", "what", "why", "when", "where", "?"],
            "objection": ["but", "however", "concern", "worried"],
            "end_call": ["goodbye", "bye", "hang up", "not interested", "stop"],
            "callback": ["call back", "later", "another time"],
        }

        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                return intent

        return "unknown"

    def _is_buying_signal(self, text: str) -> bool:
        """Check if text contains buying signals"""
        buying_signals = [
            "sign me up", "let's do it", "i'm in", "sounds good",
            "when can we start", "what do you need from me",
            "send me the info", "let's try it", "i'll do the trial",
        ]
        text_lower = text.lower()
        return any(signal in text_lower for signal in buying_signals)

    def _is_ending_signal(self, text: str) -> bool:
        """Check if prospect wants to end call"""
        ending_signals = [
            "not interested", "no thanks", "goodbye", "stop calling",
            "take me off", "don't call", "bye",
        ]
        text_lower = text.lower()
        return any(signal in text_lower for signal in ending_signals)

    # ═══════════════════════════════════════════════════════════
    # AI-POWERED RESPONSES (Optional enhancement)
    # ═══════════════════════════════════════════════════════════

    async def generate_ai_response(
        self,
        conversation: Conversation,
        prospect_input: str,
        context: Dict[str, Any] = None,
    ) -> str:
        """
        Generate AI-powered dynamic response.
        Uses the knowledge base + conversation history.
        """
        if not self.api_key:
            # Fall back to scripted response
            response, _ = self.get_response(conversation, prospect_input, context)
            return response

        # Build prompt with context
        system_prompt = f"""You are an expert HVAC AI sales agent. You're calling to sell AI-powered appointment setting and sales services.

KNOWLEDGE:
{json.dumps(self.knowledge, indent=2)}

OBJECTION HANDLING:
{json.dumps({k.value: {"responses": v.responses, "followup": v.followup} for k, v in self.objections.items()}, indent=2)}

CONVERSATION SO FAR:
{self._format_conversation_history(conversation)}

RULES:
1. Be conversational and friendly, not salesy
2. Ask questions to understand their situation
3. Handle objections with empathy then redirect
4. Always try to get to the trial offer before giving up
5. Keep responses under 3 sentences when possible
6. Use their name when you have it

GOAL: Book a demo or get them to try the 3-day free trial."""

        # In production: Call OpenAI API
        # For now: return scripted response
        response, _ = self.get_response(conversation, prospect_input, context)
        return response

    def _format_conversation_history(self, conversation: Conversation) -> str:
        """Format conversation history for AI prompt"""
        history = []
        for turn in conversation.turns[-10:]:  # Last 10 turns
            speaker = "Agent" if turn.speaker == "agent" else "Prospect"
            history.append(f"{speaker}: {turn.text}")
        return "\n".join(history)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    """Interactive demo of the sales brain"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                       SALES BRAIN                             ║
║                                                               ║
║   AI-powered HVAC sales conversation engine                   ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    brain = SalesBrain()

    # Start conversation
    conversation = brain.start_conversation(
        lead_id="test_001",
        lead_name="John's HVAC",
    )

    context = {
        "first_name": "John",
        "agent_name": "Alex",
        "city": "Phoenix",
    }

    # Get intro
    response, state = brain.get_response(conversation, "Hello?", context)
    brain.add_turn(conversation, "agent", response)

    print(f"[AGENT]: {response}")
    print(f"[STATE]: {state.value}")
    print()

    # Interactive loop
    while conversation.state != ConversationState.ENDED:
        try:
            user_input = input("[PROSPECT]: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            response, state = brain.get_response(conversation, user_input, context)
            brain.add_turn(conversation, "agent", response)

            print(f"\n[AGENT]: {response}")
            print(f"[STATE]: {state.value}")
            print()

        except KeyboardInterrupt:
            break

    print("\n[CONVERSATION ENDED]")
    print(f"Objections raised: {[o.value for o in conversation.objections_raised]}")
    print(f"Total turns: {len(conversation.turns)}")


if __name__ == "__main__":
    main()
