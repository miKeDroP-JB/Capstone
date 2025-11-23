#!/usr/bin/env python3
"""
HVAC VOICE AGENT - Make Real Calls TODAY
=========================================
Real voice agent that calls prospects, books appointments.

Uses:
- Twilio for phone calls
- OpenAI Realtime for voice AI
- CRM for tracking
- Dashboard for results

Deploy in 10 minutes. Make money today.

Love • Loyalty • Honor • Everybody Eats
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

class HVACVoiceAgent:
    """Voice agent that calls HVAC prospects"""

    def __init__(self):
        # Twilio credentials (from environment)
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

        # Initialize Twilio client
        if self.twilio_sid and self.twilio_token:
            self.client = Client(self.twilio_sid, self.twilio_token)
            self.configured = True
        else:
            self.client = None
            self.configured = False

        # Call tracking
        self.calls_dir = Path("hvac_calls")
        self.calls_dir.mkdir(exist_ok=True)

        # Load call script
        self.script = self._load_script()

    def _load_script(self) -> Dict:
        """Load call script"""
        return {
            "greeting": "Hi {name}, this is the Oracle AI calling on behalf of {contractor}. I noticed you requested an HVAC quote recently. Quick question: Is your system working right now, or is this more urgent?",

            "responses": {
                "urgent": "I understand. {contractor} has emergency service available. Let me connect you with them right away.",
                "not_urgent": "Great. {contractor} has an opening {day}. Would morning or afternoon work better for you?",
                "working": "Perfect. {contractor} offers free system checkups to prevent issues. Would you like to schedule one?"
            },

            "booking": "Perfect. You'll get a text confirmation in the next few minutes. The technician will arrive {time_slot} on {date}. Anything else before I let you go?",

            "closing": "Thanks {name}, have a great day. {contractor} looks forward to helping you."
        }

    def make_call(self, prospect: Dict, contractor: Dict) -> Dict:
        """
        Make outbound call to prospect

        Args:
            prospect: {
                "name": "John Smith",
                "phone": "+1-555-1234",
                "requested_quote": true,
                "urgency": "normal"
            }
            contractor: {
                "name": "ABC HVAC",
                "phone": "+1-555-5678",
                "calendly_link": "https://calendly.com/abc-hvac"
            }

        Returns:
            Call result with status and outcome
        """

        if not self.configured:
            return {
                "status": "error",
                "message": "Twilio not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER"
            }

        print(f"\n📞 Calling {prospect['name']} at {prospect['phone']}...")

        # Create TwiML for call
        callback_url = f"{os.getenv('BASE_URL', 'http://localhost:8000')}/voice/handle"

        try:
            call = self.client.calls.create(
                to=prospect['phone'],
                from_=self.twilio_number,
                url=callback_url,
                status_callback=f"{callback_url}/status",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                record=True  # Record for quality/training
            )

            # Track call
            call_record = {
                "call_sid": call.sid,
                "timestamp": datetime.now().isoformat(),
                "prospect": prospect,
                "contractor": contractor,
                "status": "initiated",
                "outcome": None
            }

            # Save
            call_file = self.calls_dir / f"{call.sid}.json"
            with open(call_file, 'w') as f:
                json.dump(call_record, f, indent=2)

            print(f"✓ Call initiated: {call.sid}")
            print(f"✓ Status: {call.status}")

            return {
                "status": "success",
                "call_sid": call.sid,
                "call_status": call.status
            }

        except Exception as e:
            print(f"❌ Call failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def generate_twiml_greeting(self, prospect: Dict, contractor: Dict) -> str:
        """Generate TwiML for greeting"""

        response = VoiceResponse()

        # Greeting
        greeting_text = self.script["greeting"].format(
            name=prospect["name"],
            contractor=contractor["name"]
        )

        gather = Gather(
            input='speech',
            action='/voice/respond',
            method='POST',
            timeout=5,
            speechTimeout='auto'
        )
        gather.say(greeting_text, voice='Polly.Joanna')

        response.append(gather)

        # If no input
        response.say("I didn't catch that. Let me transfer you to someone who can help.", voice='Polly.Joanna')

        return str(response)

    def generate_twiml_response(self, user_input: str, prospect: Dict, contractor: Dict) -> str:
        """Generate TwiML based on user's response"""

        response = VoiceResponse()

        # Simple intent detection
        user_input_lower = user_input.lower()

        if any(word in user_input_lower for word in ["urgent", "broken", "not working", "emergency"]):
            # Urgent case
            response.say(
                self.script["responses"]["urgent"].format(contractor=contractor["name"]),
                voice='Polly.Joanna'
            )

            # Transfer to contractor
            response.dial(contractor["phone"])

        elif any(word in user_input_lower for word in ["yes", "sure", "okay", "interested"]):
            # Ready to book
            booking_text = self.script["booking"].format(
                time_slot="between 9am-12pm",
                date="tomorrow"
            )

            response.say(booking_text, voice='Polly.Joanna')

            # Send SMS with confirmation
            response.sms(
                f"Your HVAC appointment with {contractor['name']} is confirmed for tomorrow 9am-12pm. Reply with any questions.",
                to=prospect["phone"],
                from_=self.twilio_number
            )

        else:
            # Need more info
            gather = Gather(
                input='speech',
                action='/voice/respond',
                method='POST',
                timeout=5
            )
            gather.say("Would you like to schedule a free checkup? Say yes or no.", voice='Polly.Joanna')
            response.append(gather)

        # Closing
        response.say(
            self.script["closing"].format(name=prospect["name"], contractor=contractor["name"]),
            voice='Polly.Joanna'
        )

        return str(response)

    def batch_call(self, prospects: List[Dict], contractor: Dict) -> Dict:
        """Make batch calls to multiple prospects"""

        print(f"\n{'='*60}")
        print(f"📞 BATCH CALLING")
        print(f"{'='*60}\n")
        print(f"Prospects: {len(prospects)}")
        print(f"Contractor: {contractor['name']}")
        print()

        results = {
            "total_calls": len(prospects),
            "successful": 0,
            "failed": 0,
            "calls": []
        }

        for prospect in prospects:
            result = self.make_call(prospect, contractor)

            if result["status"] == "success":
                results["successful"] += 1
            else:
                results["failed"] += 1

            results["calls"].append(result)

        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}\n")
        print(f"Total calls: {results['total_calls']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print()

        return results

    def check_configuration(self) -> Dict:
        """Check if Twilio is configured"""

        config = {
            "configured": self.configured,
            "twilio_sid": "Set" if self.twilio_sid else "Missing",
            "twilio_token": "Set" if self.twilio_token else "Missing",
            "twilio_number": self.twilio_number or "Missing",
            "ready_to_call": self.configured
        }

        return config


# =============================================================================
# FASTAPI ENDPOINTS (for Twilio callbacks)
# =============================================================================

from fastapi import FastAPI, Form, Request
from fastapi.responses import Response

app = FastAPI()
agent = HVACVoiceAgent()

@app.post("/voice/handle")
async def handle_call(request: Request):
    """Handle incoming call (Twilio callback)"""

    form_data = await request.form()

    # Get prospect info from database based on To number
    # For now, demo data
    prospect = {
        "name": "John",
        "phone": form_data.get("To")
    }

    contractor = {
        "name": "ABC HVAC",
        "phone": "+1-555-5678"
    }

    twiml = agent.generate_twiml_greeting(prospect, contractor)

    return Response(content=twiml, media_type="application/xml")


@app.post("/voice/respond")
async def handle_response(
    SpeechResult: Optional[str] = Form(None),
    To: Optional[str] = Form(None)
):
    """Handle user's speech response"""

    user_input = SpeechResult or ""

    # Get prospect/contractor info
    prospect = {"name": "John", "phone": To}
    contractor = {"name": "ABC HVAC", "phone": "+1-555-5678"}

    twiml = agent.generate_twiml_response(user_input, prospect, contractor)

    return Response(content=twiml, media_type="application/xml")


@app.post("/voice/handle/status")
async def handle_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...)
):
    """Handle call status updates"""

    print(f"Call {CallSid}: {CallStatus}")

    # Update call record
    call_file = Path(f"hvac_calls/{CallSid}.json")
    if call_file.exists():
        with open(call_file) as f:
            call_record = json.load(f)

        call_record["status"] = CallStatus
        call_record["updated_at"] = datetime.now().isoformat()

        with open(call_file, 'w') as f:
            json.dump(call_record, f, indent=2)

    return {"status": "received"}


@app.get("/status")
async def status():
    """Check agent status"""

    config = agent.check_configuration()

    return {
        "status": "operational" if config["ready_to_call"] else "configuration_needed",
        "configuration": config,
        "calls_made": len(list(Path("hvac_calls").glob("*.json"))) if Path("hvac_calls").exists() else 0
    }


if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="HVAC Voice Agent")
    parser.add_argument("--serve", action="store_true", help="Start server")
    parser.add_argument("--call", type=str, help="Make single call (phone number)")
    parser.add_argument("--batch", type=str, help="Batch call (prospects JSON file)")
    parser.add_argument("--status", action="store_true", help="Check status")

    args = parser.parse_args()

    if args.serve:
        print("\n🚀 Starting HVAC Voice Agent Server...")
        print(f"Webhook URL: http://your-domain:8000/voice/handle")
        print(f"Configure this URL in Twilio dashboard\n")

        uvicorn.run(app, host="0.0.0.0", port=8000)

    elif args.status:
        agent = HVACVoiceAgent()
        config = agent.check_configuration()

        print(f"\n{'='*60}")
        print("HVAC VOICE AGENT STATUS")
        print(f"{'='*60}\n")

        for key, value in config.items():
            print(f"{key}: {value}")

        print()

        if not config["ready_to_call"]:
            print("⚠️  Configuration needed:")
            print("   export TWILIO_ACCOUNT_SID='your_sid'")
            print("   export TWILIO_AUTH_TOKEN='your_token'")
            print("   export TWILIO_PHONE_NUMBER='+1-555-1234'")
            print()

    elif args.call:
        agent = HVACVoiceAgent()

        prospect = {
            "name": "Test Prospect",
            "phone": args.call,
            "requested_quote": True
        }

        contractor = {
            "name": "ABC HVAC",
            "phone": "+1-555-5678",
            "calendly_link": "https://calendly.com/abc-hvac"
        }

        result = agent.make_call(prospect, contractor)
        print(json.dumps(result, indent=2))

    elif args.batch:
        agent = HVACVoiceAgent()

        with open(args.batch) as f:
            prospects = json.load(f)

        contractor = {
            "name": "ABC HVAC",
            "phone": "+1-555-5678",
            "calendly_link": "https://calendly.com/abc-hvac"
        }

        results = agent.batch_call(prospects, contractor)
        print(json.dumps(results, indent=2))

    else:
        print("HVAC Voice Agent")
        print("\nUsage:")
        print("  python hvac_agent_now.py --serve                    # Start server")
        print("  python hvac_agent_now.py --status                   # Check config")
        print("  python hvac_agent_now.py --call +1-555-1234         # Make single call")
        print("  python hvac_agent_now.py --batch prospects.json     # Batch calls")
        print()
        print("Configure Twilio:")
        print("  export TWILIO_ACCOUNT_SID='your_sid'")
        print("  export TWILIO_AUTH_TOKEN='your_token'")
        print("  export TWILIO_PHONE_NUMBER='+1-555-1234'")
