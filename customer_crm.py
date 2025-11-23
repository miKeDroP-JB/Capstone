#!/usr/bin/env python3
"""
CUSTOMER CRM - Track Everything, Deliver Everything
====================================================
Complete customer relationship management:
- Track every customer interaction
- Monitor delivery status
- Ensure promises are kept
- Handle disputes immediately
- Customer service comes FIRST

If we say we'll do it, we do it. No exceptions.

Love • Loyalty • Honor • Everybody Eats
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class CustomerCRM:
    """Complete CRM system"""

    def __init__(self):
        self.data_dir = Path("crm_data")
        self.data_dir.mkdir(exist_ok=True)

        self.customers_file = self.data_dir / "customers.json"
        self.interactions_file = self.data_dir / "interactions.json"
        self.deliverables_file = self.data_dir / "deliverables.json"
        self.disputes_file = self.data_dir / "disputes.json"

        self.customers = self._load_customers()
        self.interactions = self._load_interactions()
        self.deliverables = self._load_deliverables()
        self.disputes = self._load_disputes()

    def _load_customers(self) -> Dict:
        """Load customers"""
        if self.customers_file.exists():
            with open(self.customers_file) as f:
                return json.load(f)
        return {}

    def _save_customers(self):
        """Save customers"""
        with open(self.customers_file, 'w') as f:
            json.dump(self.customers, f, indent=2)

    def _load_interactions(self) -> List:
        """Load interactions"""
        if self.interactions_file.exists():
            with open(self.interactions_file) as f:
                return json.load(f)
        return []

    def _save_interactions(self):
        """Save interactions"""
        with open(self.interactions_file, 'w') as f:
            json.dump(self.interactions, f, indent=2)

    def _load_deliverables(self) -> List:
        """Load deliverables"""
        if self.deliverables_file.exists():
            with open(self.deliverables_file) as f:
                return json.load(f)
        return []

    def _save_deliverables(self):
        """Save deliverables"""
        with open(self.deliverables_file, 'w') as f:
            json.dump(self.deliverables, f, indent=2)

    def _load_disputes(self) -> List:
        """Load disputes"""
        if self.disputes_file.exists():
            with open(self.disputes_file) as f:
                return json.load(f)
        return []

    def _save_disputes(self):
        """Save disputes"""
        with open(self.disputes_file, 'w') as f:
            json.dump(self.disputes, f, indent=2)

    def add_customer(self, company_name: str, contact_name: str, email: str, phone: str,
                    deal_info: Dict) -> str:
        """Add new customer"""

        customer_id = f"cust_{len(self.customers) + 1:04d}"

        customer = {
            "customer_id": customer_id,
            "company_name": company_name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "status": "active",
            "onboarded_date": datetime.now().isoformat(),
            "deal_info": deal_info,
            "retainer_paid": False,
            "retainer_amount": deal_info.get("retainer", 500),
            "revenue_share": deal_info.get("split", "20%"),
            "promised_deliverables": deal_info.get("deliverables", []),
            "health_score": 100,  # Customer health (100 = perfect)
            "satisfaction": "unknown",  # unknown, satisfied, unsatisfied
            "last_contact": datetime.now().isoformat(),
            "notes": []
        }

        self.customers[customer_id] = customer
        self._save_customers()

        # Log interaction
        self.log_interaction(customer_id, "customer_added",
                           f"New customer onboarded: {company_name}")

        # Create deliverables
        for deliverable in customer["promised_deliverables"]:
            self.create_deliverable(customer_id, deliverable)

        print(f"✓ Customer added: {customer_id}")
        print(f"✓ Company: {company_name}")
        print(f"✓ Health score: {customer['health_score']}")

        return customer_id

    def log_interaction(self, customer_id: str, interaction_type: str,
                       details: str, sentiment: str = "neutral"):
        """Log customer interaction"""

        interaction = {
            "interaction_id": f"int_{len(self.interactions) + 1:06d}",
            "customer_id": customer_id,
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,  # call, email, support, delivery, dispute
            "details": details,
            "sentiment": sentiment,  # positive, neutral, negative
            "handled_by": "system"
        }

        self.interactions.append(interaction)
        self._save_interactions()

        # Update customer last_contact
        if customer_id in self.customers:
            self.customers[customer_id]["last_contact"] = datetime.now().isoformat()
            self._save_customers()

    def create_deliverable(self, customer_id: str, deliverable_name: str,
                          due_date: Optional[str] = None):
        """Create deliverable to track"""

        # Calculate due date
        if not due_date:
            # Default: 7 days from now
            due_date = (datetime.now() + timedelta(days=7)).isoformat()

        deliverable = {
            "deliverable_id": f"del_{len(self.deliverables) + 1:06d}",
            "customer_id": customer_id,
            "name": deliverable_name,
            "status": "pending",  # pending, in_progress, delivered, accepted, disputed
            "created_date": datetime.now().isoformat(),
            "due_date": due_date,
            "delivered_date": None,
            "accepted_date": None,
            "notes": []
        }

        self.deliverables.append(deliverable)
        self._save_deliverables()

        print(f"✓ Deliverable created: {deliverable_name}")
        print(f"✓ Due: {due_date[:10]}")

        return deliverable["deliverable_id"]

    def update_deliverable_status(self, deliverable_id: str, status: str, notes: str = ""):
        """Update deliverable status"""

        for deliverable in self.deliverables:
            if deliverable["deliverable_id"] == deliverable_id:
                deliverable["status"] = status

                if status == "delivered":
                    deliverable["delivered_date"] = datetime.now().isoformat()
                elif status == "accepted":
                    deliverable["accepted_date"] = datetime.now().isoformat()

                if notes:
                    deliverable["notes"].append({
                        "timestamp": datetime.now().isoformat(),
                        "note": notes
                    })

                self._save_deliverables()

                # Log interaction
                customer_id = deliverable["customer_id"]
                self.log_interaction(customer_id, "delivery_update",
                                   f"{deliverable['name']} - {status}")

                print(f"✓ Updated {deliverable_id} to {status}")
                return

        print(f"❌ Deliverable not found: {deliverable_id}")

    def create_dispute(self, customer_id: str, issue: str, severity: str = "medium"):
        """Create dispute - HANDLE IMMEDIATELY"""

        dispute = {
            "dispute_id": f"dis_{len(self.disputes) + 1:04d}",
            "customer_id": customer_id,
            "issue": issue,
            "severity": severity,  # low, medium, high, critical
            "status": "open",  # open, investigating, resolved
            "created_date": datetime.now().isoformat(),
            "resolved_date": None,
            "resolution": None,
            "customer_satisfaction": None,
            "timeline": []
        }

        # Add to timeline
        dispute["timeline"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "Dispute created",
            "details": issue
        })

        self.disputes.append(dispute)
        self._save_disputes()

        # Update customer health score (dispute = bad)
        if customer_id in self.customers:
            customer = self.customers[customer_id]

            # Decrease health score based on severity
            if severity == "critical":
                customer["health_score"] = max(0, customer["health_score"] - 40)
            elif severity == "high":
                customer["health_score"] = max(0, customer["health_score"] - 25)
            elif severity == "medium":
                customer["health_score"] = max(0, customer["health_score"] - 15)
            else:
                customer["health_score"] = max(0, customer["health_score"] - 5)

            customer["satisfaction"] = "unsatisfied"
            self._save_customers()

        # Log interaction
        self.log_interaction(customer_id, "dispute", issue, sentiment="negative")

        print(f"\n{'='*60}")
        print(f"⚠️  DISPUTE CREATED - HANDLE IMMEDIATELY")
        print(f"{'='*60}")
        print(f"Dispute ID: {dispute['dispute_id']}")
        print(f"Customer ID: {customer_id}")
        print(f"Company: {self.customers[customer_id]['company_name']}")
        print(f"Issue: {issue}")
        print(f"Severity: {severity}")
        print()
        print("ACTION REQUIRED:")
        print("1. Contact customer immediately")
        print("2. Understand the issue")
        print("3. Make it right")
        print("4. Document resolution")
        print()

        return dispute["dispute_id"]

    def resolve_dispute(self, dispute_id: str, resolution: str,
                       customer_satisfaction: str = "satisfied"):
        """Resolve dispute"""

        for dispute in self.disputes:
            if dispute["dispute_id"] == dispute_id:
                dispute["status"] = "resolved"
                dispute["resolved_date"] = datetime.now().isoformat()
                dispute["resolution"] = resolution
                dispute["customer_satisfaction"] = customer_satisfaction

                dispute["timeline"].append({
                    "timestamp": datetime.now().isoformat(),
                    "event": "Dispute resolved",
                    "details": resolution
                })

                self._save_disputes()

                # Update customer health score (resolution = good)
                customer_id = dispute["customer_id"]
                if customer_id in self.customers:
                    customer = self.customers[customer_id]

                    if customer_satisfaction == "satisfied":
                        customer["health_score"] = min(100, customer["health_score"] + 30)
                        customer["satisfaction"] = "satisfied"
                    elif customer_satisfaction == "neutral":
                        customer["health_score"] = min(100, customer["health_score"] + 10)
                        customer["satisfaction"] = "neutral"

                    self._save_customers()

                # Log interaction
                self.log_interaction(customer_id, "dispute_resolved",
                                   resolution, sentiment="positive")

                print(f"✓ Dispute resolved: {dispute_id}")
                print(f"✓ Customer satisfaction: {customer_satisfaction}")
                return

        print(f"❌ Dispute not found: {dispute_id}")

    def check_overdue_deliverables(self) -> List[Dict]:
        """Check for overdue deliverables"""

        now = datetime.now()
        overdue = []

        for deliverable in self.deliverables:
            if deliverable["status"] in ["pending", "in_progress"]:
                due_date = datetime.fromisoformat(deliverable["due_date"])

                if now > due_date:
                    overdue.append(deliverable)

        return overdue

    def customer_health_check(self):
        """Check customer health scores"""

        print(f"\n{'='*60}")
        print("🏥 CUSTOMER HEALTH CHECK")
        print(f"{'='*60}\n")

        at_risk = []
        healthy = []

        for customer_id, customer in self.customers.items():
            if customer["health_score"] < 70:
                at_risk.append(customer)
            else:
                healthy.append(customer)

        print(f"Healthy customers: {len(healthy)} (score >= 70)")
        print(f"At-risk customers: {len(at_risk)} (score < 70)")
        print()

        if at_risk:
            print("⚠️  AT-RISK CUSTOMERS - NEED ATTENTION:")
            for customer in at_risk:
                print(f"\n  {customer['company_name']}")
                print(f"    Health score: {customer['health_score']}")
                print(f"    Satisfaction: {customer['satisfaction']}")
                print(f"    Last contact: {customer['last_contact'][:10]}")
                print(f"    ACTION: Contact immediately, check in, make sure they're happy")

        print()

    def daily_workflow_check(self):
        """Run daily workflow check - ensure everything is on track"""

        print(f"\n{'='*60}")
        print("📋 DAILY WORKFLOW CHECK")
        print(f"{'='*60}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

        # Check overdue deliverables
        overdue = self.check_overdue_deliverables()

        if overdue:
            print(f"🚨 OVERDUE DELIVERABLES ({len(overdue)}):")
            for deliverable in overdue:
                customer = self.customers[deliverable["customer_id"]]
                print(f"\n  {deliverable['name']}")
                print(f"    Customer: {customer['company_name']}")
                print(f"    Due: {deliverable['due_date'][:10]}")
                print(f"    Status: {deliverable['status']}")
                print(f"    ACTION: Deliver IMMEDIATELY or communicate delay")
        else:
            print("✓ No overdue deliverables")

        print()

        # Check open disputes
        open_disputes = [d for d in self.disputes if d["status"] == "open"]

        if open_disputes:
            print(f"⚠️  OPEN DISPUTES ({len(open_disputes)}) - HANDLE NOW:")
            for dispute in open_disputes:
                customer = self.customers[dispute["customer_id"]]
                print(f"\n  Dispute {dispute['dispute_id']}")
                print(f"    Customer: {customer['company_name']}")
                print(f"    Issue: {dispute['issue']}")
                print(f"    Severity: {dispute['severity']}")
                print(f"    ACTION: Resolve immediately")
        else:
            print("✓ No open disputes")

        print()

        # Check pending deliverables due soon
        due_soon = []
        now = datetime.now()

        for deliverable in self.deliverables:
            if deliverable["status"] in ["pending", "in_progress"]:
                due_date = datetime.fromisoformat(deliverable["due_date"])
                days_until_due = (due_date - now).days

                if 0 < days_until_due <= 3:
                    due_soon.append((deliverable, days_until_due))

        if due_soon:
            print(f"⏰ DELIVERABLES DUE SOON ({len(due_soon)}):")
            for deliverable, days in due_soon:
                customer = self.customers[deliverable["customer_id"]]
                print(f"\n  {deliverable['name']}")
                print(f"    Customer: {customer['company_name']}")
                print(f"    Due in: {days} days")
                print(f"    Status: {deliverable['status']}")
        else:
            print("✓ No deliverables due in next 3 days")

        print()

        # Health check
        self.customer_health_check()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Customer CRM")
    parser.add_argument("--add", type=str, help="Add customer (company name)")
    parser.add_argument("--email", type=str, help="Customer email")
    parser.add_argument("--phone", type=str, help="Customer phone")
    parser.add_argument("--contact", type=str, help="Contact name")
    parser.add_argument("--workflow", action="store_true", help="Run daily workflow check")
    parser.add_argument("--health", action="store_true", help="Customer health check")

    args = parser.parse_args()

    crm = CustomerCRM()

    if args.add and args.email and args.phone and args.contact:
        deal_info = {
            "retainer": 500,
            "split": "20%",
            "deliverables": ["Marketing Automation System", "30 Days Content", "Setup & Training"]
        }

        crm.add_customer(args.add, args.contact, args.email, args.phone, deal_info)

    elif args.workflow:
        crm.daily_workflow_check()

    elif args.health:
        crm.customer_health_check()

    else:
        print("Customer CRM")
        print("\nUsage:")
        print("  python customer_crm.py --add 'Company' --contact 'John' --email 'j@co.com' --phone '555-1234'")
        print("  python customer_crm.py --workflow  # Daily workflow check")
        print("  python customer_crm.py --health    # Customer health check")
