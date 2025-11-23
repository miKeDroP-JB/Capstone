#!/usr/bin/env python3
"""
STRIPE RETAINER - Collect $500 Retainers
=========================================
Manages retainer payments:
- Collects $500 upfront
- Tracks payment status
- Handles refunds (if no results in 90 days)

Love • Loyalty • Honor • Everybody Eats
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class StripeRetainerManager:
    """Manages retainer payments"""

    def __init__(self):
        self.data_dir = Path("retainer_payments")
        self.data_dir.mkdir(exist_ok=True)

        self.payments_file = self.data_dir / "retainer_payments.json"
        self.payments = self._load_payments()

    def _load_payments(self) -> List[Dict]:
        """Load payment records"""
        if self.payments_file.exists():
            with open(self.payments_file) as f:
                return json.load(f)
        return []

    def _save_payments(self):
        """Save payments"""
        with open(self.payments_file, 'w') as f:
            json.dump(self.payments, f, indent=2)

    def create_payment_link(self, company_name: str, client_email: str) -> str:
        """
        Create Stripe payment link for retainer

        In production, this would use Stripe API:
        stripe.PaymentLink.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Custom Solution Retainer'},
                    'unit_amount': 50000  # $500
                },
                'quantity': 1
            }]
        )

        For now, generate instructions for manual creation
        """

        payment_id = f"ret_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Record payment expectation
        payment_record = {
            "payment_id": payment_id,
            "company_name": company_name,
            "client_email": client_email,
            "amount": 500,
            "status": "pending",
            "created_date": datetime.now().isoformat(),
            "paid_date": None,
            "refund_eligible_until": (datetime.now() + timedelta(days=90)).isoformat(),
            "refunded": False,
            "refund_date": None
        }

        self.payments.append(payment_record)
        self._save_payments()

        # Generate Stripe instructions
        print(f"\n{'='*60}")
        print("💳 CREATE STRIPE PAYMENT LINK")
        print(f"{'='*60}\n")

        print("1. Go to: https://dashboard.stripe.com/payment-links/create")
        print()
        print("2. Fill in:")
        print(f"   Product name: Custom Solution Retainer - {company_name}")
        print(f"   Price: $500.00")
        print(f"   Customer email: {client_email}")
        print()
        print("3. Copy the payment link")
        print()
        print("4. Send to client:")
        print(f'   "Here\'s your payment link: [PASTE LINK]"')
        print(f'   "Once paid, I\'ll start building immediately!"')
        print()
        print(f"5. Mark as paid when received:")
        print(f"   python stripe_retainer.py --mark-paid {payment_id}")
        print()

        # Alternative: Generate link format
        link = f"https://buy.stripe.com/test_XXXXXX?client_reference_id={payment_id}"

        print(f"✓ Payment ID: {payment_id}")
        print(f"✓ Simulated link: {link}")
        print()

        return link

    def mark_paid(self, payment_id: str):
        """Mark retainer as paid"""
        for payment in self.payments:
            if payment["payment_id"] == payment_id:
                payment["status"] = "paid"
                payment["paid_date"] = datetime.now().isoformat()
                self._save_payments()

                print(f"✓ Marked {payment_id} as PAID")
                print(f"✓ Company: {payment['company_name']}")
                print(f"✓ Amount: ${payment['amount']}")
                print(f"✓ Refund eligible until: {payment['refund_eligible_until'][:10]}")
                return

        print(f"❌ Payment ID not found: {payment_id}")

    def check_refund_eligibility(self, company_name: str) -> Dict:
        """Check if client is eligible for refund"""

        for payment in self.payments:
            if payment["company_name"] == company_name and payment["status"] == "paid":

                eligible_until = datetime.fromisoformat(payment["refund_eligible_until"])
                now = datetime.now()

                is_eligible = now < eligible_until

                return {
                    "eligible": is_eligible,
                    "payment_id": payment["payment_id"],
                    "amount": payment["amount"],
                    "days_remaining": (eligible_until - now).days if is_eligible else 0,
                    "paid_date": payment["paid_date"],
                    "refund_eligible_until": payment["refund_eligible_until"]
                }

        return {"eligible": False}

    def process_refund(self, payment_id: str, reason: str = "No results in 90 days"):
        """Process refund"""

        for payment in self.payments:
            if payment["payment_id"] == payment_id:

                if payment["refunded"]:
                    print(f"❌ Already refunded on {payment['refund_date']}")
                    return

                # Mark as refunded
                payment["refunded"] = True
                payment["refund_date"] = datetime.now().isoformat()
                payment["refund_reason"] = reason
                payment["status"] = "refunded"

                self._save_payments()

                print(f"\n{'='*60}")
                print("💸 PROCESS REFUND")
                print(f"{'='*60}\n")

                print(f"Company: {payment['company_name']}")
                print(f"Amount: ${payment['amount']}")
                print(f"Reason: {reason}")
                print()
                print("STEPS:")
                print("1. Go to Stripe Dashboard")
                print("2. Find the payment")
                print("3. Click 'Refund'")
                print("4. Refund full amount ($500)")
                print()
                print(f"✓ Recorded as refunded in system")
                return

        print(f"❌ Payment ID not found: {payment_id}")

    def get_retainer_revenue(self) -> Dict:
        """Calculate retainer revenue"""

        total_collected = 0
        total_refunded = 0
        total_pending = 0
        total_net = 0

        for payment in self.payments:
            if payment["status"] == "paid" and not payment["refunded"]:
                total_collected += payment["amount"]
                total_net += payment["amount"]
            elif payment["refunded"]:
                total_refunded += payment["amount"]
            elif payment["status"] == "pending":
                total_pending += payment["amount"]

        return {
            "total_collected": total_collected,
            "total_refunded": total_refunded,
            "total_pending": total_pending,
            "net_revenue": total_net,
            "total_payments": len(self.payments),
            "paid_count": len([p for p in self.payments if p["status"] == "paid"]),
            "refunded_count": len([p for p in self.payments if p["refunded"]])
        }

    def print_dashboard(self):
        """Print retainer dashboard"""

        stats = self.get_retainer_revenue()

        print(f"\n{'='*60}")
        print("💳 RETAINER REVENUE DASHBOARD")
        print(f"{'='*60}\n")

        print(f"Total retainers: {stats['total_payments']}")
        print(f"Paid: {stats['paid_count']}")
        print(f"Refunded: {stats['refunded_count']}")
        print()
        print(f"Collected: ${stats['total_collected']:,}")
        print(f"Refunded: ${stats['total_refunded']:,}")
        print(f"Net revenue: ${stats['net_revenue']:,}")
        print()

        # Show pending
        pending = [p for p in self.payments if p["status"] == "pending"]
        if pending:
            print(f"PENDING ({len(pending)}):")
            for p in pending:
                print(f"  - {p['company_name']}: ${p['amount']}")
            print()

        # Show refund eligible
        eligible = []
        for p in self.payments:
            if p["status"] == "paid" and not p["refunded"]:
                eligible_until = datetime.fromisoformat(p["refund_eligible_until"])
                if datetime.now() < eligible_until:
                    days_left = (eligible_until - datetime.now()).days
                    eligible.append((p, days_left))

        if eligible:
            print(f"REFUND ELIGIBLE ({len(eligible)}):")
            for p, days in eligible:
                print(f"  - {p['company_name']}: {days} days remaining")
            print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stripe Retainer Manager")
    parser.add_argument("--create", type=str, help="Create payment link (company name)")
    parser.add_argument("--email", type=str, help="Client email")
    parser.add_argument("--mark-paid", type=str, help="Mark payment as paid (payment ID)")
    parser.add_argument("--refund", type=str, help="Process refund (payment ID)")
    parser.add_argument("--check", type=str, help="Check refund eligibility (company name)")
    parser.add_argument("--dashboard", action="store_true", help="Show dashboard")

    args = parser.parse_args()

    manager = StripeRetainerManager()

    if args.create and args.email:
        manager.create_payment_link(args.create, args.email)
    elif args.mark_paid:
        manager.mark_paid(args.mark_paid)
    elif args.refund:
        manager.process_refund(args.refund)
    elif args.check:
        result = manager.check_refund_eligibility(args.check)
        if result["eligible"]:
            print(f"✓ Eligible for refund")
            print(f"  Days remaining: {result['days_remaining']}")
        else:
            print(f"❌ Not eligible for refund")
    elif args.dashboard:
        manager.print_dashboard()
    else:
        print("Stripe Retainer Manager")
        print("\nUsage:")
        print("  python stripe_retainer.py --create 'Company Name' --email client@email.com")
        print("  python stripe_retainer.py --mark-paid ret_XXXXXX")
        print("  python stripe_retainer.py --check 'Company Name'")
        print("  python stripe_retainer.py --refund ret_XXXXXX")
        print("  python stripe_retainer.py --dashboard")
