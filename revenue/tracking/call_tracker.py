#!/usr/bin/env python3
"""
CALL TRACKER - Track your sales calls and results
Usage: python call_tracker.py
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class CallTracker:
    """Track sales calls, demos, and results"""

    def __init__(self, data_file: str = "calls_data.json"):
        self.data_file = data_file
        self.calls = self._load_data()

    def _load_data(self) -> List[Dict]:
        """Load existing call data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return []

    def _save_data(self):
        """Save call data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.calls, f, indent=2)

    def add_call(self, company: str, contact: str, phone: str,
                 outcome: str, notes: str = "", follow_up: str = ""):
        """Log a new call"""
        call = {
            "id": len(self.calls) + 1,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "company": company,
            "contact": contact,
            "phone": phone,
            "outcome": outcome,  # interested, not_interested, demo_booked, callback, voicemail
            "notes": notes,
            "follow_up": follow_up,
            "status": "active"
        }
        self.calls.append(call)
        self._save_data()
        print(f"✓ Call logged: {company} - {outcome}")
        return call

    def add_demo(self, call_id: int, demo_date: str, outcome: str,
                 amount: float = 0, notes: str = ""):
        """Log a demo result"""
        for call in self.calls:
            if call['id'] == call_id:
                call['demo'] = {
                    "date": demo_date,
                    "outcome": outcome,  # closed, thinking, lost
                    "amount": amount,
                    "notes": notes
                }
                if outcome == "closed":
                    call['status'] = "closed"
                    call['revenue'] = amount
                self._save_data()
                print(f"✓ Demo logged: {call['company']} - {outcome}")
                return call
        print(f"✗ Call ID {call_id} not found")
        return None

    def get_stats(self) -> Dict:
        """Get overall statistics"""
        total_calls = len(self.calls)
        demos_booked = len([c for c in self.calls if c['outcome'] == 'demo_booked'])
        closed = len([c for c in self.calls if c.get('status') == 'closed'])

        total_revenue = sum(c.get('revenue', 0) for c in self.calls)

        stats = {
            "total_calls": total_calls,
            "interested": len([c for c in self.calls if c['outcome'] == 'interested']),
            "demos_booked": demos_booked,
            "closed": closed,
            "lost": len([c for c in self.calls if c.get('demo', {}).get('outcome') == 'lost']),
            "pending": len([c for c in self.calls if c['outcome'] == 'callback' or
                          c.get('demo', {}).get('outcome') == 'thinking']),
            "total_revenue": total_revenue,
            "avg_deal_size": total_revenue / closed if closed > 0 else 0,
            "call_to_demo_rate": (demos_booked / total_calls * 100) if total_calls > 0 else 0,
            "demo_to_close_rate": (closed / demos_booked * 100) if demos_booked > 0 else 0,
            "overall_close_rate": (closed / total_calls * 100) if total_calls > 0 else 0
        }
        return stats

    def list_calls(self, filter_by: str = "all"):
        """List calls with optional filter"""
        filtered = self.calls

        if filter_by == "pending":
            filtered = [c for c in self.calls if c['outcome'] in ['callback', 'interested']
                       or c.get('demo', {}).get('outcome') == 'thinking']
        elif filter_by == "closed":
            filtered = [c for c in self.calls if c.get('status') == 'closed']
        elif filter_by == "lost":
            filtered = [c for c in self.calls if c.get('demo', {}).get('outcome') == 'lost']

        return filtered

    def print_stats(self):
        """Print formatted statistics"""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("CALL TRACKER STATISTICS")
        print("=" * 60)
        print(f"\n📞 CALLS MADE: {stats['total_calls']}")
        print(f"   ├─ Interested: {stats['interested']}")
        print(f"   ├─ Demos Booked: {stats['demos_booked']}")
        print(f"   ├─ Pending: {stats['pending']}")
        print(f"   └─ Lost: {stats['lost']}")

        print(f"\n🎯 DEMOS")
        print(f"   ├─ Closed: {stats['closed']}")
        print(f"   └─ Thinking: {stats['pending']}")

        print(f"\n💰 REVENUE")
        print(f"   ├─ Total: ${stats['total_revenue']:,.2f}")
        print(f"   └─ Avg Deal: ${stats['avg_deal_size']:,.2f}")

        print(f"\n📊 CONVERSION RATES")
        print(f"   ├─ Call → Demo: {stats['call_to_demo_rate']:.1f}%")
        print(f"   ├─ Demo → Close: {stats['demo_to_close_rate']:.1f}%")
        print(f"   └─ Overall Close: {stats['overall_close_rate']:.1f}%")

        print("\n" + "=" * 60 + "\n")

    def print_calls(self, calls: List[Dict]):
        """Print formatted call list"""
        if not calls:
            print("No calls found.")
            return

        print("\n" + "-" * 80)
        for call in calls:
            status_emoji = {
                'interested': '✨',
                'demo_booked': '📅',
                'callback': '📞',
                'voicemail': '📧',
                'not_interested': '✗',
                'closed': '✓'
            }.get(call.get('status', call['outcome']), '•')

            print(f"\n{status_emoji} [{call['id']}] {call['company']} - {call['contact']}")
            print(f"   Date: {call['date']} {call['time']}")
            print(f"   Phone: {call['phone']}")
            print(f"   Outcome: {call['outcome'].replace('_', ' ').title()}")

            if call.get('notes'):
                print(f"   Notes: {call['notes']}")

            if call.get('demo'):
                demo = call['demo']
                print(f"   Demo: {demo['date']} - {demo['outcome'].title()}")
                if demo.get('amount'):
                    print(f"   Amount: ${demo['amount']:,.2f}")

            if call.get('follow_up'):
                print(f"   Follow-up: {call['follow_up']}")

        print("\n" + "-" * 80 + "\n")

def interactive_mode():
    """Interactive CLI for call tracking"""
    tracker = CallTracker()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    CALL TRACKER                               ║
║            Track calls, demos, and revenue                    ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    while True:
        print("\nWhat would you like to do?")
        print("  1. Log a call")
        print("  2. Log a demo result")
        print("  3. View statistics")
        print("  4. List all calls")
        print("  5. List pending calls")
        print("  6. List closed deals")
        print("  7. Export to CSV")
        print("  8. Exit")

        choice = input("\nChoice (1-8): ").strip()

        if choice == "1":
            print("\n--- LOG CALL ---")
            company = input("Company name: ").strip()
            contact = input("Contact name: ").strip()
            phone = input("Phone number: ").strip()

            print("\nOutcome:")
            print("  1. Interested")
            print("  2. Demo booked")
            print("  3. Callback requested")
            print("  4. Voicemail")
            print("  5. Not interested")
            outcome_choice = input("Choice (1-5): ").strip()

            outcome_map = {
                "1": "interested",
                "2": "demo_booked",
                "3": "callback",
                "4": "voicemail",
                "5": "not_interested"
            }
            outcome = outcome_map.get(outcome_choice, "interested")

            notes = input("Notes (optional): ").strip()
            follow_up = input("Follow-up date (optional): ").strip()

            tracker.add_call(company, contact, phone, outcome, notes, follow_up)

        elif choice == "2":
            print("\n--- LOG DEMO ---")
            call_id = int(input("Call ID: ").strip())
            demo_date = input("Demo date (YYYY-MM-DD): ").strip()

            print("\nOutcome:")
            print("  1. Closed (won)")
            print("  2. Thinking")
            print("  3. Lost")
            outcome_choice = input("Choice (1-3): ").strip()

            outcome_map = {"1": "closed", "2": "thinking", "3": "lost"}
            outcome = outcome_map.get(outcome_choice, "thinking")

            amount = 0
            if outcome == "closed":
                amount = float(input("Deal amount ($): ").strip())

            notes = input("Notes (optional): ").strip()

            tracker.add_demo(call_id, demo_date, outcome, amount, notes)

        elif choice == "3":
            tracker.print_stats()

        elif choice == "4":
            calls = tracker.list_calls("all")
            tracker.print_calls(calls)

        elif choice == "5":
            calls = tracker.list_calls("pending")
            tracker.print_calls(calls)

        elif choice == "6":
            calls = tracker.list_calls("closed")
            tracker.print_calls(calls)

        elif choice == "7":
            filename = f"calls_export_{datetime.now().strftime('%Y%m%d')}.csv"
            with open(filename, 'w') as f:
                f.write("ID,Date,Time,Company,Contact,Phone,Outcome,Status,Revenue,Notes\n")
                for call in tracker.calls:
                    f.write(f"{call['id']},{call['date']},{call['time']},"
                           f"{call['company']},{call['contact']},{call['phone']},"
                           f"{call['outcome']},{call.get('status', 'active')},"
                           f"{call.get('revenue', 0)},{call.get('notes', '')}\n")
            print(f"\n✓ Exported to {filename}")

        elif choice == "8":
            print("\n✓ Goodbye!\n")
            break

if __name__ == "__main__":
    interactive_mode()
