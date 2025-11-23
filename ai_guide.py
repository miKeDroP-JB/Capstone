#!/usr/bin/env python3
"""
YOUR AI BUSINESS GUIDE
======================
Interactive guide that walks you through building your empire.
Ask questions, get guidance, focus on loving people.
"""
import asyncio
from datetime import datetime
from pathlib import Path
import json

# Import your systems
from ai_connectors import AIOrchestrator
from the_instant_creator import InstantCreator, GCODE, LoveLedger


class AIBusinessGuide:
    """
    Your personal AI guide to building a love-driven business empire.

    I'm here to:
    - Answer your questions
    - Guide you through each step
    - Help you understand Love Scores
    - Explain what to do next
    - Keep you focused on love
    """

    def __init__(self):
        self.ai = AIOrchestrator()
        self.creator = InstantCreator()
        self.love_ledger = LoveLedger()

        # Track where user is in their journey
        self.progress_file = Path("your_progress.json")
        self.progress = self._load_progress()

        print("""
╔═══════════════════════════════════════════════════════════════╗
║                  YOUR AI BUSINESS GUIDE                       ║
║                                                               ║
║  Hi! I'm here to walk you through building your empire.      ║
║  Ask me anything. I'm here to help you succeed.              ║
║                                                               ║
║  Love • Loyalty • Honor • Everybody Eats                     ║
╚═══════════════════════════════════════════════════════════════╝
""")

    def _load_progress(self):
        """Load user's progress"""
        if self.progress_file.exists():
            return json.loads(self.progress_file.read_text())

        # Default progress
        return {
            "day": 0,
            "systems_created": 0,
            "first_revenue": False,
            "first_customer": False,
            "total_revenue": 0,
            "community_contributed": 0,
            "average_love_score": 0,
            "milestones": [],
            "started_at": datetime.now().isoformat()
        }

    def _save_progress(self):
        """Save user's progress"""
        self.progress_file.write_text(json.dumps(self.progress, indent=2))

    def _update_milestone(self, milestone: str):
        """Track milestone achievement"""
        if milestone not in self.progress["milestones"]:
            self.progress["milestones"].append({
                "name": milestone,
                "achieved_at": datetime.now().isoformat()
            })
            self._save_progress()
            print(f"\n🎉 MILESTONE ACHIEVED: {milestone}")

    async def greet(self):
        """Greet user based on their progress"""
        if self.progress["day"] == 0:
            print("""
Welcome! I can see this is your first time here.

I'm going to walk you through everything step by step.
Don't worry - I'll make it simple.

Here's what we'll do today (Day 1):
  1. Test your system (2 minutes)
  2. Understand what you have (5 minutes)
  3. Create your first test system (3 minutes)
  4. Check your Love Score
  5. Celebrate! 🎉

Ready? Let's start.

First, let's test your system to make sure everything works.
Run this command:

  python3 test_instant_creator.py

Then come back and tell me what happened.
""")
        else:
            days = self.progress["day"]
            systems = self.progress["systems_created"]
            revenue = self.progress["total_revenue"]

            print(f"""
Welcome back! You're on Day {days}.

Progress so far:
  💼 Systems Created: {systems}
  💰 Revenue Generated: ${revenue:,.2f}
  💝 Community Share: ${self.progress['community_contributed']:,.2f}
  🎯 Milestones: {len(self.progress['milestones'])}

What would you like to do today?
  1. Create a new system
  2. Review my Love Scores
  3. Get advice on what to build
  4. Understand something better
  5. Ask a specific question

Just type your question or tell me what you need help with.
""")

    async def answer_question(self, question: str):
        """Answer user's question using AI"""

        # Build context
        context = f"""You are an AI business guide helping someone build a love-driven business empire.

Their progress:
- Day: {self.progress['day']}
- Systems Created: {self.progress['systems_created']}
- Revenue: ${self.progress['total_revenue']}
- First Customer: {self.progress['first_customer']}
- Milestones: {len(self.progress['milestones'])}

Current Love Ledger:
{json.dumps(self.love_ledger.get_total_love(), indent=2)}

Core principles:
- Love is the real currency (Love Score = Value Created + Regeneration / Extraction + 1)
- GCODE protection (blocks harmful ideas)
- Everybody Eats (33%+ to community)
- 70%+ Love Score = Net Positive (approved)

User's question: {question}

Provide a helpful, encouraging answer that:
1. Addresses their specific question
2. Gives actionable next steps
3. Relates to their current progress
4. Focuses on love as the primary metric
5. Is warm, supportive, and clear

Keep it concise (3-5 paragraphs max).
"""

        # Get AI response
        result = await self.ai.generate(
            context,
            task_type="strategy",
            complexity=0.7,
            max_tokens=500
        )

        if result.get("success"):
            return result["content"]
        else:
            return self._fallback_answer(question)

    def _fallback_answer(self, question: str) -> str:
        """Fallback answers if AI is unavailable"""

        q = question.lower()

        # Common questions
        if "what should i build" in q or "what to build" in q:
            return """Great question! Here's how to decide:

1. What problem do you see people struggling with?
2. Can you help them solve it?
3. Can you give back 33%+ to community?

If yes to all three, build it!

Examples:
- See elders lonely? → Build voice AI companion
- See businesses wasting money on HVAC? → Build savings agent
- See kids struggling with math? → Build learning game

Start with what you CARE about. Love Score follows naturally."""

        elif "love score" in q:
            return """Love Score = (Value Created + Regeneration) / (Extraction + 1)

In plain English:
- How much do you HELP people? (Value)
- How much do you GIVE BACK? (Regeneration)
- How much do you TAKE? (Extraction)

Goal: Give more than you take = High Love Score

70%+ = Net Positive (approved)
85%+ = High Love (excellent)
95%+ = Exceptional Love (pure giving)

To improve: Help more people, give back more, take less."""

        elif "blocked" in q or "gcode" in q:
            return """GCODE blocked your idea because it detected:
- Deception or manipulation
- Harm to people
- Exploitation
- Pure extraction (no giving back)

This is PROTECTING you from building something harmful.

To fix: Add regeneration to your idea.

Example:
❌ "Build system to extract maximum money"
✅ "Build system that helps people and shares 33% with community"

Love first, money follows."""

        elif "first customer" in q or "first sale" in q:
            return """Getting your first customer:

1. Build something that solves a REAL problem
2. Find 10 people who have that problem
3. Offer to help them (free trial if needed)
4. Deliver value
5. Ask for payment

Don't overthink it. Just help someone.

For B2B: Call 10 businesses, pitch your solution
For B2C: Post in relevant communities, offer free trial

One real customer proves your system works.
Then it's just: Repeat 10x, 100x, 1000x."""

        elif "money" in q or "revenue" in q or "profit" in q:
            return """Money comes from helping people.

The formula:
1. Find people with a problem
2. Solve their problem (create value)
3. Charge fair price for the value
4. Give 33%+ to community
5. Repeat

Price guide:
- B2B: $100-500/month or 10% of savings
- B2C: $10-50/month with free tier
- Enterprise: $1000+/month

Start small ($100/month from 1 customer).
Scale up (100 customers = $10k/month).

Love Score tells you if your pricing is fair.
<70% = Taking too much, lower prices or give more back."""

        elif "scale" in q or "grow" in q:
            return """Scaling is simple: Repeat what works.

Week 1: 1 customer = $100
Week 2: 10 customers = $1k
Month 2: 50 customers = $5k
Month 3: 100 customers = $10k
Month 6: 500 customers = $50k
Year 1: 1000+ customers = $100k+

How:
1. Build system that works (Week 1)
2. Replicate 10x (Week 2-4)
3. Automate acquisition (Month 2)
4. Let it compound (Months 3-12)

Your system improves 1% daily.
After 365 days = 37.8x better.
That's compound magic."""

        else:
            return f"""Good question! Let me help you think through this.

Based on where you are (Day {self.progress['day']}, {self.progress['systems_created']} systems created):

If Day 1-7: Focus on learning the system and creating your first revenue system
If Week 2-4: Focus on getting first 10 customers and proving your model
If Month 2+: Focus on systematizing and scaling what works

The core principle: Love first, money follows.

Ask yourself:
1. Does this help people? (Value)
2. Am I giving back? (Regeneration)
3. Is it sustainable? (Love Score >70%)

Want me to be more specific? Ask me your question in more detail."""

    async def suggest_next_step(self):
        """Suggest what user should do next based on progress"""

        day = self.progress["day"]
        systems = self.progress["systems_created"]
        has_revenue = self.progress["first_revenue"]
        has_customer = self.progress["first_customer"]

        print("\n" + "="*60)
        print("YOUR NEXT STEP")
        print("="*60 + "\n")

        if day == 0:
            print("""Step 1: Test Your System (2 minutes)

Run this command:
  python3 test_instant_creator.py

Expected result: ✅ ALL TESTS PASSED!

This confirms your system is working and ready to create.

After you see all tests pass, come back and tell me!
""")

        elif systems == 0:
            print("""Step 2: Create Your First System (3 minutes)

Try this example:
  python CREATE.py "Build AI learning game for kids"

Watch what happens:
  ✅ GCODE checks if it's helpful
  ⚔️ AI tournament picks best approach
  🔨 System generates code
  💝 Love Score is calculated
  💾 System saved to file

Then check your Love Score:
  cat love_ledger.json

Want help deciding what to build? Just ask me!
""")

        elif not has_customer:
            print(f"""Step 3: Get Your First Customer

You've built {systems} system(s). Now let's get them used!

For B2B (like HVAC agent):
  1. Make list of 10 potential customers
  2. Research their pain points
  3. Call and pitch: "I can help you [solve problem]"
  4. Offer free trial or demo
  5. Get 1 person using it

For B2C (like learning game):
  1. Post in relevant communities
  2. Offer free access for feedback
  3. Get 10-20 test users
  4. Collect feedback
  5. Improve based on learnings

Goal: ONE person using your system by end of day.

Quality > Quantity at this stage.
""")

        elif not has_revenue:
            print("""Step 4: Make Your First Dollar

You have a customer! Now let's get paid.

If B2B:
  - Send invoice: $100-500 for first month
  - Or bill after results: 10% of savings
  - Use Stripe/PayPal/check

If B2C:
  - Ask test users if they'd pay $10-20/month
  - 1-2 will say yes
  - Set up subscription

Goal: Make $1-500 this week.

Not about getting rich yet.
About proving people will PAY for value you create.

Once you make $1, you know the path to $1M.
""")

        elif self.progress["total_revenue"] < 1000:
            print(f"""Step 5: Get to $1000/month

Current revenue: ${self.progress['total_revenue']}/month

Path to $1k:
  - 10 customers @ $100/month = $1k
  - 20 customers @ $50/month = $1k
  - 5 customers @ $200/month = $1k

Replicate what worked:
  1. You got 1 customer → How?
  2. Repeat that process 10x
  3. Let system improve daily (1% compound)

Also:
  - Create customer acquisition system
  - Build automatic onboarding
  - Set up automatic billing

Voice these improvements to the system!
""")

        elif self.progress["total_revenue"] < 10000:
            print(f"""Step 6: Scale to $10k/month

Current revenue: ${self.progress['total_revenue']}/month

You've proven your model works.
Now it's pure multiplication.

Path to $10k:
  - 100 customers @ $100/month = $10k
  - 50 customers @ $200/month = $10k
  - 20 customers @ $500/month = $10k

Focus on:
  1. Automated customer acquisition
  2. Self-serve onboarding
  3. AI-powered support
  4. Keeping Love Score >70%

Build these systems:
  python CREATE.py "Build customer acquisition system for [your business]"
  python CREATE.py "Build onboarding automation for [your business]"

You're building an empire now. 🚀
""")

        else:
            print(f"""You're Crushing It! 🎉

Revenue: ${self.progress['total_revenue']}/month
Community: ${self.progress['community_contributed']}/month

Next level:
  - Scale to $100k/month
  - Build team of AI agents
  - Create multiple revenue streams
  - Help 10,000+ people

Your system is 37.8x better after 1 year (1% daily compound).

Keep focusing on:
  1. Helping more people (Value)
  2. Giving back more (Regeneration)
  3. Maintaining Love Score >70%
  4. Letting system compound

You've proven love is the real currency.
Now scale that love to the world. 💝
""")

    async def interactive_session(self):
        """Run interactive Q&A session"""

        await self.greet()

        print("\n" + "="*60)
        print("I'm listening. What do you need help with?")
        print("="*60)
        print("\nType your question (or 'next' for next step, 'quit' to exit):\n")

        while True:
            try:
                question = input("> ").strip()

                if not question:
                    continue

                if question.lower() in ['quit', 'exit', 'bye']:
                    print("\n💝 Keep building with love! Come back anytime.\n")
                    break

                if question.lower() in ['next', 'next step', 'what next']:
                    await self.suggest_next_step()
                    print("\nAnything else I can help with?\n")
                    continue

                if question.lower() in ['progress', 'status', 'where am i']:
                    self._show_progress()
                    print("\nWhat else can I help with?\n")
                    continue

                # Answer the question
                print("\n💭 Let me think about that...\n")
                answer = await self.answer_question(question)
                print(answer)
                print("\n" + "-"*60)
                print("Does that help? Ask me anything else!\n")

            except KeyboardInterrupt:
                print("\n\n💝 Keep building with love! Come back anytime.\n")
                break
            except Exception as e:
                print(f"\n❌ Oops, something went wrong: {e}")
                print("Try asking your question differently?\n")

    def _show_progress(self):
        """Show user's current progress"""
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                     YOUR PROGRESS                             ║
╚═══════════════════════════════════════════════════════════════╝

📅 Day: {self.progress['day']}
💼 Systems Created: {self.progress['systems_created']}
💰 Total Revenue: ${self.progress['total_revenue']:,.2f}
💝 Community Share: ${self.progress['community_contributed']:,.2f}
👥 First Customer: {'✅ Yes' if self.progress['first_customer'] else '❌ Not yet'}
💵 First Revenue: {'✅ Yes' if self.progress['first_revenue'] else '❌ Not yet'}

🎯 Milestones Achieved: {len(self.progress['milestones'])}
{''.join([f"   ✅ {m['name']}" for m in self.progress['milestones'][:5]])}

Love Ledger:
{json.dumps(self.love_ledger.get_total_love(), indent=2)}

Keep going! Every day you're building something that helps people. 💝
""")


# =============================================================================
# RUN GUIDE
# =============================================================================

async def main():
    """Run the AI guide"""
    guide = AIBusinessGuide()
    await guide.interactive_session()


if __name__ == "__main__":
    print("\n🚀 Starting Your AI Business Guide...\n")
    asyncio.run(main())
