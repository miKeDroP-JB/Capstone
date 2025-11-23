#!/usr/bin/env python3
"""
INTELLIGENT SALES AGENT
=======================
AI agent that discovers needs and sells custom solutions.

Strategy:
1. Call prospect
2. Ask discovery questions
3. Identify their biggest need
4. Offer to build solution (we can build anything)
5. Close with 80/20 split (they get 80%, we get 20%)

The agent LEARNS from every conversation.

Usage:
    from intelligent_sales_agent import IntelligentSalesAgent
    agent = IntelligentSalesAgent()
    result = agent.make_call(target)

Love • Loyalty • Honor • Everybody Eats
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class IntelligentSalesAgent:
    """AI agent that sells by discovering needs"""

    def __init__(self):
        self.data_dir = Path("sales_agent_data")
        self.data_dir.mkdir(exist_ok=True)

        self.calls_file = self.data_dir / "calls.json"
        self.learnings_file = self.data_dir / "learnings.json"

        self.calls = self._load_calls()
        self.learnings = self._load_learnings()

        # What we can build instantly
        self.solutions = {
            "website": {
                "name": "Custom Website",
                "build_time": "2 hours",
                "value": "$3,000-5,000",
                "our_cut": "20% of revenue growth"
            },
            "booking_system": {
                "name": "Online Booking System",
                "build_time": "3 hours",
                "value": "$2,000-4,000",
                "our_cut": "20% of bookings revenue"
            },
            "crm": {
                "name": "Customer Management System",
                "build_time": "4 hours",
                "value": "$5,000-8,000",
                "our_cut": "20% of new customer revenue"
            },
            "mobile_app": {
                "name": "Mobile App",
                "build_time": "1 day",
                "value": "$10,000-20,000",
                "our_cut": "20% of app revenue"
            },
            "automation": {
                "name": "Business Automation",
                "build_time": "1-2 days",
                "value": "$5,000-15,000",
                "our_cut": "20% of savings/growth"
            },
            "marketing_system": {
                "name": "Marketing Automation",
                "build_time": "1 day",
                "value": "$3,000-7,000",
                "our_cut": "20% of marketing ROI"
            },
            "game": {
                "name": "Custom Game",
                "build_time": "1 hour",
                "value": "$1,000-3,000",
                "our_cut": "20% of game revenue"
            },
            "video": {
                "name": "Marketing Video",
                "build_time": "30 minutes",
                "value": "$500-2,000",
                "our_cut": "20% of campaign results"
            }
        }

    def _load_calls(self) -> List[Dict]:
        """Load call history"""
        if self.calls_file.exists():
            with open(self.calls_file) as f:
                return json.load(f)
        return []

    def _save_calls(self):
        """Save call history"""
        with open(self.calls_file, 'w') as f:
            json.dump(self.calls, f, indent=2)

    def _load_learnings(self) -> Dict:
        """Load learnings from past calls"""
        if self.learnings_file.exists():
            with open(self.learnings_file) as f:
                return json.load(f)
        return {
            "total_calls": 0,
            "successful_discoveries": 0,
            "closes": 0,
            "best_openers": [],
            "best_questions": [],
            "common_objections": [],
            "winning_responses": []
        }

    def _save_learnings(self):
        """Save learnings"""
        with open(self.learnings_file, 'w') as f:
            json.dump(self.learnings, f, indent=2)

    def make_call(self, target: Dict) -> Dict:
        """Make a sales call to a target"""
        print(f"\n📞 CALLING: {target['company']}")
        print(f"   Phone: {target['phone']}")

        # Call simulation (in production, uses Twilio + AI voice)
        call_record = {
            "id": f"call_{len(self.calls)+1:04d}",
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "conversation": [],
            "discovered_need": None,
            "solution_offered": None,
            "outcome": None,
            "close_probability": 0
        }

        # PHASE 1: Opening
        opener = self._get_best_opener()
        call_record["conversation"].append({"agent": opener})
        print(f"\n   Agent: {opener}")

        response = self._simulate_response(target, "opening")
        call_record["conversation"].append({"prospect": response})
        print(f"   Prospect: {response}")

        if "not interested" in response.lower() or "busy" in response.lower():
            call_record["outcome"] = "rejected_early"
            self.calls.append(call_record)
            self._save_calls()
            print(f"   ✗ Call ended early")
            return call_record

        # PHASE 2: Discovery
        discovery_questions = self._get_discovery_questions()
        needs_found = []

        for question in discovery_questions[:3]:  # Ask top 3 questions
            call_record["conversation"].append({"agent": question})
            print(f"\n   Agent: {question}")

            response = self._simulate_response(target, "discovery", question)
            call_record["conversation"].append({"prospect": response})
            print(f"   Prospect: {response}")

            # Analyze response for needs
            need = self._extract_need(response)
            if need:
                needs_found.append(need)

        if not needs_found:
            call_record["outcome"] = "no_need_discovered"
            self.calls.append(call_record)
            self._save_calls()
            print(f"   ⚠️  No clear need discovered")
            return call_record

        # PHASE 3: Solution Presentation
        primary_need = needs_found[0]
        call_record["discovered_need"] = primary_need

        solution = self._match_solution(primary_need)
        call_record["solution_offered"] = solution

        pitch = self._create_pitch(primary_need, solution)
        call_record["conversation"].append({"agent": pitch})
        print(f"\n   Agent: {pitch}")

        response = self._simulate_response(target, "pitch", pitch)
        call_record["conversation"].append({"prospect": response})
        print(f"   Prospect: {response}")

        # PHASE 3.5: Handle Bargaining
        if "10%" in response:
            bargain_response = "You know what? For the right partner, I can do 10%. You keep 90%, I get 10%. Deal?"
            call_record["conversation"].append({"agent": bargain_response})
            call_record["final_split"] = "10%"  # Track final agreement
            print(f"\n   Agent: {bargain_response}")

            response = self._simulate_response(target, "close")
            call_record["conversation"].append({"prospect": response})
            print(f"   Prospect: {response}")

        # PHASE 4: Close
        if "interested" in response.lower() or "tell me more" in response.lower() or "deal" in response.lower():
            close = self._create_close()
            call_record["conversation"].append({"agent": close})
            print(f"\n   Agent: {close}")

            final_response = self._simulate_response(target, "close")
            call_record["conversation"].append({"prospect": final_response})
            print(f"   Prospect: {final_response}")

            if "yes" in final_response.lower() or "let's do it" in final_response.lower():
                call_record["outcome"] = "closed"
                call_record["close_probability"] = 0.95
                print(f"\n   ✓ DEAL CLOSED!")
            else:
                call_record["outcome"] = "interested_thinking"
                call_record["close_probability"] = 0.60
                print(f"\n   ⏳ Thinking it over")
        else:
            call_record["outcome"] = "not_interested"
            call_record["close_probability"] = 0.10
            print(f"\n   ✗ Not interested")

        # Save and learn
        self.calls.append(call_record)
        self._save_calls()
        self._learn_from_call(call_record)

        return call_record

    def _get_best_opener(self) -> str:
        """Get best opening line based on learnings"""
        openers = [
            "Hi, this is [AI Agent]. I help businesses like yours grow faster with custom digital solutions. Do you have 60 seconds?",
            "Hey, I noticed your business and had an idea that could help you get more customers. Got a quick minute?",
            "Hi! I'm calling because I think I can help you automate some of your work and save time. Can we chat for a minute?"
        ]

        # Use learned best opener if available
        if self.learnings.get("best_openers"):
            return random.choice(self.learnings["best_openers"])

        return random.choice(openers)

    def _get_discovery_questions(self) -> List[str]:
        """Get discovery questions"""
        questions = [
            "What's your biggest challenge right now with getting new customers?",
            "How are you currently handling bookings/scheduling?",
            "What takes up most of your time that you wish was automated?",
            "How do most customers find you?",
            "What would make your business life easier?",
            "If you could wave a magic wand and fix one thing in your business, what would it be?"
        ]

        # Use learned best questions if available
        if self.learnings.get("best_questions"):
            return self.learnings["best_questions"] + questions

        return questions

    def _simulate_response(self, target: Dict, phase: str, context: str = "") -> str:
        """Simulate prospect response"""
        # Simulate based on target data and phase

        if phase == "opening":
            responses = [
                "Sure, what's this about?",
                "I'm busy, make it quick.",
                "Not interested, thanks.",
                "Okay, I've got a minute.",
            ]
            # Weight by score
            if target.get("score", 50) > 70:
                return random.choice(responses[:2])  # More positive
            else:
                return random.choice(responses)

        elif phase == "discovery":
            # Simulate need-based responses
            needs = target.get("needs_assessment", {})
            active_needs = [k for k, v in needs.items() if v]

            if active_needs:
                need = random.choice(active_needs)
                responses = {
                    "online_booking": "We're still taking calls and it's chaos. I miss appointments sometimes.",
                    "customer_management": "I have customer info everywhere - spreadsheets, paper, my head. It's a mess.",
                    "marketing_automation": "I barely have time to market. I know I should do more social media but...",
                    "mobile_app": "Customers keep asking if we have an app. We don't."
                }
                return responses.get(need, "Honestly, I'm not sure. Business is okay but could be better.")

            return "We're doing alright. Always looking to improve though."

        elif phase == "pitch":
            if target.get("score", 50) > 60:
                return random.choice([
                    "That sounds interesting. How much does it cost?",
                    "Tell me more about this.",
                    "I've been thinking about something like this...",
                    "20% seems high. Can you do 10%?",  # Bargaining!
                ])
            else:
                return random.choice([
                    "I don't know... sounds expensive.",
                    "Maybe. I need to think about it.",
                    "Not sure if now is the right time.",
                    "20%? That's too much. What about 10%?",  # Bargaining!
                ])

        elif phase == "close":
            if target.get("score", 50) > 70:
                return random.choice([
                    "You know what, let's do it. What's next?",
                    "Okay, I'm in. How do we start?",
                    "This sounds good. Let's try it.",
                ])
            else:
                return random.choice([
                    "Let me think about it and I'll call you back.",
                    "Can you send me more info?",
                    "I need to talk to my partner first.",
                ])

        return "Hmm, interesting."

    def _extract_need(self, response: str) -> str:
        """Extract need from response"""
        response_lower = response.lower()

        if any(w in response_lower for w in ["booking", "appointment", "schedule"]):
            return "online_booking"
        elif any(w in response_lower for w in ["customer", "crm", "contact", "spreadsheet"]):
            return "customer_management"
        elif any(w in response_lower for w in ["market", "social", "promote", "ads"]):
            return "marketing"
        elif any(w in response_lower for w in ["app", "mobile"]):
            return "mobile_app"
        elif any(w in response_lower for w in ["automate", "time", "manual", "repetitive"]):
            return "automation"
        elif any(w in response_lower for w in ["website", "online presence", "site"]):
            return "website"

        return None

    def _match_solution(self, need: str) -> Dict:
        """Match need to solution"""
        mapping = {
            "online_booking": "booking_system",
            "customer_management": "crm",
            "marketing": "marketing_system",
            "mobile_app": "mobile_app",
            "automation": "automation",
            "website": "website"
        }

        solution_key = mapping.get(need, "automation")
        return self.solutions[solution_key]

    def _create_pitch(self, need: str, solution: Dict) -> str:
        """Create pitch for solution"""
        return f"""Perfect! I can build you a {solution['name']} in about {solution['build_time']}.

Here's the deal - normally this would cost {solution['value']}, but I have a better model:

I build it for FREE. You pay me nothing upfront.

Then, I get 20% of what it makes you. You keep 80%.

So if this helps you make an extra $10,000, you keep $8,000 and I get $2,000. If it makes you nothing, I get nothing.

Fair?"""

    def _create_close(self) -> str:
        """Create closing statement"""
        return """Great! Here's what happens next:

1. I build your solution (takes [build_time])
2. You review it and we tweak it
3. You start using it
4. You make money
5. We both win

I can start today. Want to do this?"""

    def _learn_from_call(self, call_record: Dict):
        """Learn from the call"""
        self.learnings["total_calls"] += 1

        if call_record["discovered_need"]:
            self.learnings["successful_discoveries"] += 1

        if call_record["outcome"] == "closed":
            self.learnings["closes"] += 1

            # Learn winning patterns
            opener = call_record["conversation"][0]["agent"]
            if opener not in self.learnings.get("best_openers", []):
                self.learnings.setdefault("best_openers", []).append(opener)

        self._save_learnings()

    def get_stats(self) -> Dict:
        """Get performance stats"""
        return {
            "total_calls": self.learnings["total_calls"],
            "discovery_rate": (self.learnings["successful_discoveries"] / max(1, self.learnings["total_calls"])) * 100,
            "close_rate": (self.learnings["closes"] / max(1, self.learnings["total_calls"])) * 100,
            "total_closes": self.learnings["closes"]
        }

if __name__ == "__main__":
    # Test the agent
    agent = IntelligentSalesAgent()

    # Sample target
    target = {
        "company": "Test HVAC Company",
        "phone": "+1-555-1234",
        "score": 75,
        "needs_assessment": {
            "online_booking": True,
            "customer_management": False
        }
    }

    result = agent.make_call(target)

    print(f"\n{'='*60}")
    print("CALL SUMMARY")
    print(f"{'='*60}")
    print(f"Outcome: {result['outcome']}")
    print(f"Need discovered: {result['discovered_need']}")
    print(f"Solution offered: {result.get('solution_offered', {}).get('name', 'None')}")
    print(f"Close probability: {result['close_probability']*100}%")

    stats = agent.get_stats()
    print(f"\n{'='*60}")
    print("AGENT STATS")
    print(f"{'='*60}")
    print(f"Total calls: {stats['total_calls']}")
    print(f"Discovery rate: {stats['discovery_rate']:.1f}%")
    print(f"Close rate: {stats['close_rate']:.1f}%")
