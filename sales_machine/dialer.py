#!/usr/bin/env python3
"""
DIALER - Telephony Management
Handles outbound calling via Twilio.

Love - Loyalty - Honor - Everybody Eats
"""

import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

class CallStatus(Enum):
    QUEUED = "queued"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    FAILED = "failed"
    VOICEMAIL = "voicemail"


class CallDirection(Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"


@dataclass
class DialerConfig:
    """Dialer configuration"""
    twilio_account_sid: str = field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", ""))
    twilio_auth_token: str = field(default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN", ""))
    twilio_phone_number: str = field(default_factory=lambda: os.getenv("TWILIO_PHONE_NUMBER", ""))

    # Call settings
    max_concurrent_calls: int = 5
    call_timeout_seconds: int = 30
    retry_attempts: int = 2
    retry_delay_minutes: int = 60

    # Hours of operation (24h format)
    start_hour: int = 9
    end_hour: int = 20

    # Voicemail detection
    detect_voicemail: bool = True
    voicemail_message: str = ""


@dataclass
class Call:
    """A phone call"""
    id: str
    lead_id: str
    phone_number: str
    direction: CallDirection = CallDirection.OUTBOUND
    status: CallStatus = CallStatus.QUEUED

    # Timing
    queued_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0

    # Recording
    recording_url: Optional[str] = None
    recording_duration: int = 0

    # Results
    outcome: str = ""
    notes: str = ""

    # Retries
    attempt: int = 1
    max_attempts: int = 3


@dataclass
class CallQueue:
    """Queue of calls to make"""
    calls: List[Call] = field(default_factory=list)
    active_calls: int = 0
    completed_today: int = 0
    successful_today: int = 0


# ═══════════════════════════════════════════════════════════════
# DIALER ENGINE
# ═══════════════════════════════════════════════════════════════

class Dialer:
    """
    Telephony management for AI calling.
    Uses Twilio for actual calls.
    """

    def __init__(self, config: DialerConfig = None):
        self.config = config or DialerConfig()
        self.queue = CallQueue()
        self.calls: Dict[str, Call] = {}
        self._call_counter = 0
        self._client = None

    def _init_twilio(self):
        """Initialize Twilio client"""
        if not self._client and self.config.twilio_account_sid:
            try:
                from twilio.rest import Client
                self._client = Client(
                    self.config.twilio_account_sid,
                    self.config.twilio_auth_token
                )
            except ImportError:
                print("  [!] Install twilio: pip install twilio")

    def _generate_call_id(self) -> str:
        """Generate unique call ID"""
        self._call_counter += 1
        return f"call_{self._call_counter:08d}"

    def _is_within_hours(self) -> bool:
        """Check if current time is within calling hours"""
        now = datetime.now()
        return self.config.start_hour <= now.hour < self.config.end_hour

    # ═══════════════════════════════════════════════════════════
    # QUEUE MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def add_to_queue(self, lead_id: str, phone_number: str) -> Call:
        """Add a lead to the call queue"""
        call = Call(
            id=self._generate_call_id(),
            lead_id=lead_id,
            phone_number=phone_number,
        )

        self.calls[call.id] = call
        self.queue.calls.append(call)

        return call

    def add_batch_to_queue(self, leads: List[Dict[str, str]]) -> List[Call]:
        """Add multiple leads to queue"""
        calls = []
        for lead in leads:
            call = self.add_to_queue(lead["id"], lead["phone"])
            calls.append(call)
        return calls

    def get_next_call(self) -> Optional[Call]:
        """Get next call from queue"""
        if not self._is_within_hours():
            return None

        if self.queue.active_calls >= self.config.max_concurrent_calls:
            return None

        for call in self.queue.calls:
            if call.status == CallStatus.QUEUED:
                return call

        return None

    # ═══════════════════════════════════════════════════════════
    # CALLING
    # ═══════════════════════════════════════════════════════════

    async def make_call(self, call: Call, twiml_url: str) -> Call:
        """
        Initiate an outbound call.
        twiml_url should point to your TwiML endpoint.
        """
        self._init_twilio()

        call.status = CallStatus.RINGING
        call.started_at = datetime.now()
        self.queue.active_calls += 1

        if self._client:
            try:
                twilio_call = self._client.calls.create(
                    to=call.phone_number,
                    from_=self.config.twilio_phone_number,
                    url=twiml_url,
                    timeout=self.config.call_timeout_seconds,
                    machine_detection="Enable" if self.config.detect_voicemail else "Disable",
                )
                call.id = twilio_call.sid
            except Exception as e:
                call.status = CallStatus.FAILED
                call.notes = str(e)
        else:
            # Simulation mode
            print(f"  [DIAL] Calling {call.phone_number}...")
            await asyncio.sleep(2)  # Simulate ring time
            call.status = CallStatus.IN_PROGRESS

        return call

    async def end_call(self, call: Call, outcome: str):
        """End a call and record outcome"""
        call.ended_at = datetime.now()
        call.status = CallStatus.COMPLETED
        call.outcome = outcome

        if call.started_at:
            call.duration_seconds = int((call.ended_at - call.started_at).total_seconds())

        self.queue.active_calls -= 1
        self.queue.completed_today += 1

        if outcome in ["booked", "interested", "callback"]:
            self.queue.successful_today += 1

        # Remove from queue
        if call in self.queue.calls:
            self.queue.calls.remove(call)

    async def handle_no_answer(self, call: Call):
        """Handle no answer - schedule retry if attempts remain"""
        call.status = CallStatus.NO_ANSWER
        call.ended_at = datetime.now()
        self.queue.active_calls -= 1

        if call.attempt < call.max_attempts:
            # Schedule retry
            call.attempt += 1
            call.status = CallStatus.QUEUED
            call.queued_at = datetime.now()
        else:
            call.outcome = "no_answer_max_attempts"
            self.queue.calls.remove(call)

    async def handle_voicemail(self, call: Call):
        """Handle voicemail detection"""
        call.status = CallStatus.VOICEMAIL
        call.outcome = "voicemail"
        # Could leave a message here
        await self.end_call(call, "voicemail")

    # ═══════════════════════════════════════════════════════════
    # DIALING LOOP
    # ═══════════════════════════════════════════════════════════

    async def run_dialer(self, twiml_url: str, callback=None):
        """
        Main dialing loop.
        Continuously makes calls from queue.
        """
        print(f"\n{'='*60}")
        print(f"  DIALER STARTED")
        print(f"  Queue: {len(self.queue.calls)} calls")
        print(f"  Hours: {self.config.start_hour}:00 - {self.config.end_hour}:00")
        print(f"{'='*60}\n")

        while self.queue.calls:
            call = self.get_next_call()

            if not call:
                if not self._is_within_hours():
                    print("  [!] Outside calling hours. Pausing...")
                await asyncio.sleep(5)
                continue

            print(f"  [DIAL] {call.phone_number} (attempt {call.attempt})")

            await self.make_call(call, twiml_url)

            if callback:
                # Hand off to conversation handler
                outcome = await callback(call)
                await self.end_call(call, outcome)
            else:
                # Simulation
                await asyncio.sleep(30)
                await self.end_call(call, "completed")

            print(f"  [DONE] {call.phone_number}: {call.outcome}")

        print(f"\n{'='*60}")
        print(f"  DIALER FINISHED")
        print(f"  Completed: {self.queue.completed_today}")
        print(f"  Successful: {self.queue.successful_today}")
        print(f"{'='*60}\n")

    # ═══════════════════════════════════════════════════════════
    # STATS
    # ═══════════════════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """Get dialer statistics"""
        completed_calls = [c for c in self.calls.values() if c.status == CallStatus.COMPLETED]

        return {
            "queue_size": len(self.queue.calls),
            "active_calls": self.queue.active_calls,
            "completed_today": self.queue.completed_today,
            "successful_today": self.queue.successful_today,
            "success_rate": self.queue.successful_today / max(1, self.queue.completed_today),
            "avg_duration": sum(c.duration_seconds for c in completed_calls) / max(1, len(completed_calls)),
            "total_calls": len(self.calls),
        }


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

async def main():
    """Demo the dialer"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                        DIALER                                 ║
║                                                               ║
║   Telephony management for AI calling                         ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    config = DialerConfig(
        max_concurrent_calls=3,
        start_hour=9,
        end_hour=21,
    )

    dialer = Dialer(config)

    # Add test leads
    test_leads = [
        {"id": "lead_001", "phone": "+1-555-0101"},
        {"id": "lead_002", "phone": "+1-555-0102"},
        {"id": "lead_003", "phone": "+1-555-0103"},
    ]

    dialer.add_batch_to_queue(test_leads)

    print(f"Queue: {len(dialer.queue.calls)} calls")
    print(f"Config: {config.max_concurrent_calls} concurrent, {config.start_hour}-{config.end_hour}")

    print("\nTo run with Twilio, set:")
    print("  export TWILIO_ACCOUNT_SID=your_sid")
    print("  export TWILIO_AUTH_TOKEN=your_token")
    print("  export TWILIO_PHONE_NUMBER=+1234567890")


if __name__ == "__main__":
    asyncio.run(main())
