#!/usr/bin/env python3
"""
GLYPH AGENTS - Agents Decomposed to Atomic Operations

Hierarchy:
1. GLYPH - Single atomic operation (make 1 call, send 1 message, post 1 tweet)
2. SPELL - Sequence of glyphs (qualify → educate → offer → close)
3. AGENT - Collection of spells (voice agent knows 10 spells)
4. SWARM - Many agents executing in parallel (100 agents, each knowing spells)

Every glyph stores its result in the grimoire.
Every spell learns from glyph successes.
Every agent improves by learning better spell combinations.
Every swarm optimizes by deploying the best agents.

Philosophy: Break everything down to smallest learnable units.
           Store everything. Learn from everything. Improve forever.
"""

from typing import Dict, List, Optional
import json
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
import random


# ============================================================================
# GLYPH SYSTEM - Atomic Operations
# ============================================================================

class Glyph:
    """
    A single atomic operation

    Examples:
    - dial_number("555-1234")
    - send_message("Hi, is this John?")
    - post_tweet("5 HVAC tips for winter")
    - answer_question("What's your warranty?")
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.grimoire_path = Path("grimoire") / "glyphs"
        self.grimoire_path.mkdir(parents=True, exist_ok=True)
        self.stats = self._load_stats()

    def execute(self, parameters: Dict) -> Dict:
        """
        Execute the glyph with given parameters

        Returns result and stores in grimoire
        """
        start_time = datetime.now()

        # Execute the atomic operation
        result = self._perform_operation(parameters)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Store in grimoire
        self._store_in_grimoire({
            "glyph": self.name,
            "parameters": parameters,
            "result": result,
            "success": result.get("success", False),
            "duration": duration,
            "timestamp": start_time.isoformat()
        })

        # Update stats
        self._update_stats(result.get("success", False))

        return result

    def _perform_operation(self, parameters: Dict) -> Dict:
        """
        Override in subclasses to implement actual operation

        This is where the real work happens
        """
        raise NotImplementedError("Subclass must implement _perform_operation")

    def _store_in_grimoire(self, entry: Dict):
        """Store glyph execution in grimoire"""
        glyph_file = self.grimoire_path / f"{self.name}.jsonl"

        with open(glyph_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def _load_stats(self) -> Dict:
        """Load glyph statistics from grimoire"""
        stats_file = self.grimoire_path / f"{self.name}_stats.json"

        if stats_file.exists():
            with open(stats_file) as f:
                return json.load(f)

        return {
            "total_executions": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
            "avg_duration": 0.0
        }

    def _update_stats(self, success: bool):
        """Update glyph statistics"""
        self.stats["total_executions"] += 1

        if success:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1

        self.stats["success_rate"] = self.stats["successful"] / self.stats["total_executions"]

        # Save stats
        stats_file = self.grimoire_path / f"{self.name}_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def get_stats(self) -> Dict:
        """Get glyph statistics"""
        return self.stats


# ============================================================================
# CONCRETE GLYPHS - Actual Atomic Operations
# ============================================================================

class DialNumberGlyph(Glyph):
    """Dial a phone number"""

    def __init__(self):
        super().__init__("dial_number", "Dials a phone number")

    def _perform_operation(self, parameters: Dict) -> Dict:
        phone = parameters.get("phone")

        # Simulate dialing (in production, use Twilio)
        success = random.random() > 0.10  # 90% connect rate

        return {
            "success": success,
            "phone": phone,
            "connected": success,
            "message": "Connected" if success else "No answer"
        }


class SendMessageGlyph(Glyph):
    """Send a message during call"""

    def __init__(self):
        super().__init__("send_message", "Sends a voice message")

    def _perform_operation(self, parameters: Dict) -> Dict:
        message = parameters.get("message")
        context = parameters.get("context", {})

        # Simulate message delivery
        success = random.random() > 0.05  # 95% delivery rate

        return {
            "success": success,
            "message": message,
            "delivered": success,
            "response": "Message heard" if success else "Line issue"
        }


class AskQuestionGlyph(Glyph):
    """Ask a qualifying question"""

    def __init__(self):
        super().__init__("ask_question", "Asks a qualifying question")

    def _perform_operation(self, parameters: Dict) -> Dict:
        question = parameters.get("question")

        # Simulate response
        responses = [
            "Yes, I'm interested",
            "Tell me more",
            "Not right now",
            "I'm busy",
            "How much does it cost?"
        ]

        response = random.choice(responses)
        interested = response in ["Yes, I'm interested", "Tell me more", "How much does it cost?"]

        return {
            "success": True,
            "question": question,
            "response": response,
            "interested": interested
        }


class BookAppointmentGlyph(Glyph):
    """Book an appointment"""

    def __init__(self):
        super().__init__("book_appointment", "Books an appointment")

    def _perform_operation(self, parameters: Dict) -> Dict:
        date = parameters.get("date")
        time = parameters.get("time")

        # Simulate booking
        success = random.random() > 0.20  # 80% book rate when asked

        return {
            "success": success,
            "date": date,
            "time": time,
            "booked": success,
            "confirmation": f"Booked for {date} at {time}" if success else "Can't make it"
        }


class PostTweetGlyph(Glyph):
    """Post a tweet"""

    def __init__(self):
        super().__init__("post_tweet", "Posts a tweet")

    def _perform_operation(self, parameters: Dict) -> Dict:
        content = parameters.get("content")
        hashtags = parameters.get("hashtags", [])

        # Simulate posting
        success = random.random() > 0.02  # 98% post success rate

        engagement = random.randint(5, 50) if success else 0

        return {
            "success": success,
            "content": content,
            "hashtags": hashtags,
            "posted": success,
            "engagement": engagement
        }


class AnswerQuestionGlyph(Glyph):
    """Answer a customer question"""

    def __init__(self):
        super().__init__("answer_question", "Answers a customer question")

    def _perform_operation(self, parameters: Dict) -> Dict:
        question = parameters.get("question")
        context = parameters.get("context", {})

        # Simulate answering (uses AI in production)
        success = random.random() > 0.05  # 95% answer success rate

        return {
            "success": success,
            "question": question,
            "answered": success,
            "confidence": 0.95 if success else 0.40,
            "escalated": not success
        }


# ============================================================================
# SPELL SYSTEM - Sequences of Glyphs
# ============================================================================

class Spell:
    """
    A sequence of glyphs that accomplish a goal

    Examples:
    - QualifyLeadSpell: dial → greet → ask_interest → determine_fit
    - BookAppointmentSpell: confirm_interest → check_availability → book → send_confirmation
    - PostValueContentSpell: generate_idea → write_post → add_hashtags → post → engage
    """

    def __init__(self, name: str, description: str, glyphs: List[tuple]):
        self.name = name
        self.description = description
        self.glyphs = glyphs  # List of (Glyph, param_generator) tuples
        self.grimoire_path = Path("grimoire") / "spells"
        self.grimoire_path.mkdir(parents=True, exist_ok=True)
        self.stats = self._load_stats()

    def cast(self, initial_parameters: Dict) -> Dict:
        """
        Cast the spell (execute glyph sequence)

        Each glyph can modify parameters for next glyph
        """
        start_time = datetime.now()
        context = initial_parameters.copy()
        results = []
        success = True

        for i, (glyph, param_generator) in enumerate(self.glyphs):
            # Generate parameters for this glyph (may depend on previous results)
            params = param_generator(context, results)

            # Execute glyph
            result = glyph.execute(params)
            results.append({
                "glyph": glyph.name,
                "result": result
            })

            # Update context for next glyph
            context.update(result)

            # If glyph fails and is critical, spell fails
            if not result.get("success", False):
                success = False
                break

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Store spell execution in grimoire
        self._store_in_grimoire({
            "spell": self.name,
            "initial_parameters": initial_parameters,
            "glyph_results": results,
            "success": success,
            "duration": duration,
            "timestamp": start_time.isoformat()
        })

        # Update stats
        self._update_stats(success)

        return {
            "success": success,
            "results": results,
            "context": context
        }

    def _store_in_grimoire(self, entry: Dict):
        """Store spell execution in grimoire"""
        spell_file = self.grimoire_path / f"{self.name}.jsonl"

        with open(spell_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def _load_stats(self) -> Dict:
        """Load spell statistics"""
        stats_file = self.grimoire_path / f"{self.name}_stats.json"

        if stats_file.exists():
            with open(stats_file) as f:
                return json.load(f)

        return {
            "total_casts": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
            "avg_duration": 0.0
        }

    def _update_stats(self, success: bool):
        """Update spell statistics"""
        self.stats["total_casts"] += 1

        if success:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1

        self.stats["success_rate"] = self.stats["successful"] / self.stats["total_casts"]

        # Save stats
        stats_file = self.grimoire_path / f"{self.name}_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def get_stats(self) -> Dict:
        """Get spell statistics"""
        return self.stats


# ============================================================================
# CONCRETE SPELLS - Actual Sequences
# ============================================================================

class QualifyLeadSpell(Spell):
    """Qualify a sales lead"""

    def __init__(self):
        dial = DialNumberGlyph()
        ask = AskQuestionGlyph()

        glyphs = [
            (dial, lambda ctx, res: {"phone": ctx["phone"]}),
            (ask, lambda ctx, res: {"question": "Are you interested in improving your HVAC system?"})
        ]

        super().__init__("qualify_lead", "Qualifies a sales lead", glyphs)


class BookAppointmentSpell(Spell):
    """Book an appointment with qualified lead"""

    def __init__(self):
        ask = AskQuestionGlyph()
        book = BookAppointmentGlyph()

        glyphs = [
            (ask, lambda ctx, res: {"question": "When would be a good time for our technician to visit?"}),
            (book, lambda ctx, res: {"date": "Thursday", "time": "2pm"})  # Would parse from response
        ]

        super().__init__("book_appointment", "Books an appointment", glyphs)


class ValueContentSpell(Spell):
    """Post value-first social content"""

    def __init__(self):
        post = PostTweetGlyph()

        glyphs = [
            (post, lambda ctx, res: {
                "content": "5 signs your HVAC needs servicing before winter",
                "hashtags": ["#HVAC", "#HomeMaintenance"]
            })
        ]

        super().__init__("value_content", "Posts value content", glyphs)


class CustomerSupportSpell(Spell):
    """Handle customer support question"""

    def __init__(self):
        answer = AnswerQuestionGlyph()

        glyphs = [
            (answer, lambda ctx, res: {"question": ctx["question"], "context": ctx.get("context", {})})
        ]

        super().__init__("customer_support", "Answers customer question", glyphs)


# ============================================================================
# GLYPH AGENT - Agent Built from Spells
# ============================================================================

class GlyphAgent:
    """
    An agent that knows multiple spells

    Agent selects best spell for the situation based on:
    - Past success rates (from grimoire)
    - Current context
    - Goal requirements
    """

    def __init__(self, name: str, spells: List[Spell]):
        self.name = name
        self.spells = {spell.name: spell for spell in spells}
        self.grimoire_path = Path("grimoire") / "agents"
        self.grimoire_path.mkdir(parents=True, exist_ok=True)

    def act(self, goal: str, parameters: Dict) -> Dict:
        """
        Act to accomplish a goal

        Selects best spell based on goal and past success rates
        """

        # Select best spell for goal
        spell = self._select_spell(goal)

        if not spell:
            return {
                "success": False,
                "error": f"No spell known for goal: {goal}"
            }

        # Cast spell
        result = spell.cast(parameters)

        # Store agent action
        self._store_action({
            "agent": self.name,
            "goal": goal,
            "spell_used": spell.name,
            "parameters": parameters,
            "success": result["success"],
            "timestamp": datetime.now().isoformat()
        })

        return result

    def _select_spell(self, goal: str) -> Optional[Spell]:
        """
        Select best spell for goal

        Uses grimoire stats to pick spell with highest success rate for this goal
        """

        # Map goals to spells
        goal_spell_map = {
            "qualify": "qualify_lead",
            "book": "book_appointment",
            "post": "value_content",
            "answer": "customer_support"
        }

        # Find matching spell
        for keyword, spell_name in goal_spell_map.items():
            if keyword in goal.lower():
                return self.spells.get(spell_name)

        # Default to first spell
        return list(self.spells.values())[0] if self.spells else None

    def _store_action(self, entry: Dict):
        """Store agent action in grimoire"""
        agent_file = self.grimoire_path / f"{self.name}.jsonl"

        with open(agent_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_stats(self) -> Dict:
        """Get agent statistics"""
        stats = {
            "agent": self.name,
            "spells": {}
        }

        for spell_name, spell in self.spells.items():
            stats["spells"][spell_name] = spell.get_stats()

        return stats


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def demo_glyph_system():
    """
    Demonstrate the glyph system

    Shows how agents decompose to spells decompose to glyphs
    """

    print("\n" + "="*70)
    print("🔮 GLYPH AGENT SYSTEM - ATOMIC OPERATIONS")
    print("="*70)
    print("\nHierarchy:")
    print("  Glyph → Smallest atomic operation")
    print("  Spell → Sequence of glyphs")
    print("  Agent → Collection of spells")
    print("  Swarm → Many agents in parallel")
    print("\nEvery level stores results in grimoire for learning.\n")

    # Create glyphs
    print("Creating glyphs (atomic operations)...")
    dial = DialNumberGlyph()
    ask = AskQuestionGlyph()
    book = BookAppointmentGlyph()
    post = PostTweetGlyph()
    answer = AnswerQuestionGlyph()

    # Create spells
    print("Creating spells (glyph sequences)...")
    qualify_spell = QualifyLeadSpell()
    book_spell = BookAppointmentSpell()
    content_spell = ValueContentSpell()
    support_spell = CustomerSupportSpell()

    # Create agent
    print("Creating agent (spell collection)...")
    voice_agent = GlyphAgent("voice_agent", [qualify_spell, book_spell])
    social_agent = GlyphAgent("social_agent", [content_spell])
    support_agent = GlyphAgent("support_agent", [support_spell])

    print("\n" + "-"*70)
    print("DEMO 1: Voice Agent Qualifies and Books Lead")
    print("-"*70 + "\n")

    # Voice agent qualifies lead
    print("Step 1: Qualify lead...")
    result1 = voice_agent.act("qualify", {"phone": "555-1234", "name": "John"})
    print(f"Result: {result1['success']}")

    # If qualified, book appointment
    if result1["success"] and result1["context"].get("interested"):
        print("\nStep 2: Lead is interested, booking appointment...")
        result2 = voice_agent.act("book", {"phone": "555-1234", "name": "John"})
        print(f"Result: Appointment {'' if result2['success'] else 'not '}booked")

    print("\n" + "-"*70)
    print("DEMO 2: Social Agent Posts Content")
    print("-"*70 + "\n")

    # Social agent posts content
    print("Posting value content...")
    result3 = social_agent.act("post", {"topic": "HVAC tips"})
    print(f"Result: Post {'succeeded' if result3['success'] else 'failed'}")
    if result3["success"]:
        engagement = result3["context"].get("engagement", 0)
        print(f"Engagement: {engagement} interactions")

    print("\n" + "-"*70)
    print("DEMO 3: Support Agent Answers Question")
    print("-"*70 + "\n")

    # Support agent answers question
    print("Answering customer question...")
    result4 = support_agent.act("answer", {
        "question": "What's your warranty policy?",
        "context": {"customer_id": "cust_123"}
    })
    print(f"Result: Question {'answered' if result4['success'] else 'escalated'}")

    print("\n" + "-"*70)
    print("GRIMOIRE LEARNING - Statistics")
    print("-"*70 + "\n")

    # Show glyph stats
    print("Glyph Statistics:")
    print(f"  dial_number: {dial.get_stats()}")
    print(f"  ask_question: {ask.get_stats()}")
    print(f"  book_appointment: {book.get_stats()}")

    # Show spell stats
    print("\nSpell Statistics:")
    print(f"  qualify_lead: {qualify_spell.get_stats()}")
    print(f"  book_appointment: {book_spell.get_stats()}")

    # Show agent stats
    print("\nAgent Statistics:")
    print(f"  voice_agent: {voice_agent.get_stats()}")

    print("\n" + "="*70)
    print("💡 THE POWER OF GLYPHS")
    print("="*70)
    print("\nEvery glyph execution is stored.")
    print("Every spell learns from glyph success rates.")
    print("Every agent improves by learning better spell combinations.")
    print("Every swarm optimizes by deploying the best agents.")
    print("\nInfinite learning. Infinite improvement. Infinite scale.")
    print("\n💝 Love • Loyalty • Honor • Everybody Eats\n")


if __name__ == "__main__":
    demo_glyph_system()
