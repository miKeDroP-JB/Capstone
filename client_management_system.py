#!/usr/bin/env python3
"""
CLIENT MANAGEMENT SYSTEM - The Ecosystem
=========================================
We set up, run, monitor, and pay clients.

How it works:
1. Client signs up (or we close them)
2. We auto-create all their accounts (social, email, etc.)
3. We post content, send emails, run campaigns
4. We track EVERYTHING (leads, sales, revenue)
5. We calculate their share (80% or 90%)
6. We send them checks monthly
7. We keep growing their business

This is the PLATFORM model.

One system managing 100s of clients.
Each client gets checks.
We scale infinitely.

Love • Loyalty • Honor • Everybody Eats
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import time

class ClientManagementSystem:
    """Manages all clients in the ecosystem"""

    def __init__(self):
        self.data_dir = Path("client_ecosystem")
        self.data_dir.mkdir(exist_ok=True)

        self.clients_file = self.data_dir / "clients.json"
        self.metrics_file = self.data_dir / "metrics.json"
        self.payments_file = self.data_dir / "payments.json"

        self.clients = self._load_clients()
        self.metrics = self._load_metrics()
        self.payments = self._load_payments()

    def _load_clients(self) -> Dict:
        """Load all clients"""
        if self.clients_file.exists():
            with open(self.clients_file) as f:
                return json.load(f)
        return {}

    def _save_clients(self):
        """Save clients"""
        with open(self.clients_file, 'w') as f:
            json.dump(self.clients, f, indent=2)

    def _load_metrics(self) -> Dict:
        """Load metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                return json.load(f)
        return {}

    def _save_metrics(self):
        """Save metrics"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

    def _load_payments(self) -> List:
        """Load payment history"""
        if self.payments_file.exists():
            with open(self.payments_file) as f:
                return json.load(f)
        return []

    def _save_payments(self):
        """Save payments"""
        with open(self.payments_file, 'w') as f:
            json.dump(self.payments, f, indent=2)

    def onboard_client(self, company_name: str, industry: str, deal_info: Dict) -> Dict:
        """
        Onboard new client into ecosystem

        Steps:
        1. Create client record
        2. Auto-setup accounts (social, email)
        3. Generate content packages
        4. Schedule first month
        5. Start tracking
        """
        print(f"\n{'='*60}")
        print(f"ONBOARDING NEW CLIENT")
        print(f"{'='*60}")
        print(f"Company: {company_name}")
        print(f"Industry: {industry}")
        print(f"Revenue share: {deal_info.get('split', '20%')}")
        print()

        client_id = f"client_{len(self.clients) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create client record
        client = {
            "id": client_id,
            "company_name": company_name,
            "industry": industry,
            "onboarded_date": datetime.now().isoformat(),
            "status": "active",
            "deal_info": deal_info,
            "revenue_share": deal_info.get('split', '20%'),
            "package_type": deal_info.get('solution', 'marketing_automation'),
            "accounts": {},
            "content_schedule": {},
            "metrics": {
                "total_posts": 0,
                "total_emails_sent": 0,
                "leads_generated": 0,
                "revenue_generated": 0,
                "our_earnings": 0
            }
        }

        # STEP 1: Auto-setup accounts
        print("🔧 Setting up accounts...")
        client["accounts"] = self._setup_accounts(company_name, industry)

        # STEP 2: Generate content
        print("📝 Generating content packages...")
        client["content_schedule"] = self._generate_content_schedule(company_name, industry)

        # STEP 3: Schedule automation
        print("⏰ Scheduling automation...")
        client["automation_schedule"] = self._schedule_automation(client_id)

        # STEP 4: Initialize metrics tracking
        print("📊 Initializing metrics tracking...")
        self.metrics[client_id] = {
            "daily": [],
            "weekly": [],
            "monthly": []
        }

        # Save
        self.clients[client_id] = client
        self._save_clients()
        self._save_metrics()

        print(f"\n✓ Client onboarded successfully!")
        print(f"✓ Client ID: {client_id}")
        print(f"✓ Accounts created: {len(client['accounts'])}")
        print(f"✓ Content scheduled: 30 days")
        print(f"✓ First payment scheduled: {self._get_next_payment_date()}")

        return client

    def _setup_accounts(self, company_name: str, industry: str) -> Dict:
        """
        Auto-setup all needed accounts

        In production this would:
        - Create Buffer account (social media scheduling)
        - Create Mailchimp account (email marketing)
        - Create Google My Business profile
        - Create Facebook Business page
        - Set up tracking pixels

        For now, simulate the setup
        """
        accounts = {}

        # Social media accounts
        print("   Creating social media accounts...")
        accounts["buffer"] = {
            "platform": "buffer",
            "status": "active",
            "credentials": f"buffer_{company_name.lower().replace(' ', '_')}",
            "connected_platforms": ["facebook", "instagram", "twitter", "linkedin"],
            "setup_date": datetime.now().isoformat()
        }

        # Email marketing
        print("   Creating email marketing account...")
        accounts["mailchimp"] = {
            "platform": "mailchimp",
            "status": "active",
            "credentials": f"mailchimp_{company_name.lower().replace(' ', '_')}",
            "list_name": f"{company_name} Customer List",
            "setup_date": datetime.now().isoformat()
        }

        # Google My Business
        print("   Setting up Google My Business...")
        accounts["google_business"] = {
            "platform": "google_my_business",
            "status": "active",
            "business_name": company_name,
            "setup_date": datetime.now().isoformat()
        }

        # Analytics
        print("   Setting up analytics tracking...")
        accounts["analytics"] = {
            "platform": "google_analytics",
            "status": "active",
            "tracking_id": f"GA-{random.randint(10000000, 99999999)}",
            "setup_date": datetime.now().isoformat()
        }

        time.sleep(1)  # Simulate setup time

        return accounts

    def _generate_content_schedule(self, company_name: str, industry: str) -> Dict:
        """Generate 30-day content schedule"""
        schedule = {
            "social_media": [],
            "email_campaigns": [],
            "blog_posts": []
        }

        # 30 days of social posts (1 per day)
        for day in range(1, 31):
            post_date = (datetime.now() + timedelta(days=day)).isoformat()
            schedule["social_media"].append({
                "day": day,
                "scheduled_date": post_date,
                "content": f"Day {day} social post for {company_name}",
                "platforms": ["facebook", "instagram", "twitter", "linkedin"],
                "status": "scheduled"
            })

        # Weekly email campaigns
        for week in range(1, 5):
            email_date = (datetime.now() + timedelta(weeks=week)).isoformat()
            schedule["email_campaigns"].append({
                "week": week,
                "scheduled_date": email_date,
                "campaign_name": f"Week {week} Campaign",
                "status": "scheduled"
            })

        return schedule

    def _schedule_automation(self, client_id: str) -> Dict:
        """Schedule all automation tasks"""
        return {
            "daily_tasks": [
                {"task": "post_social_media", "time": "09:00"},
                {"task": "check_analytics", "time": "17:00"},
                {"task": "update_metrics", "time": "23:00"}
            ],
            "weekly_tasks": [
                {"task": "send_email_campaign", "day": "monday", "time": "10:00"},
                {"task": "generate_report", "day": "friday", "time": "16:00"}
            ],
            "monthly_tasks": [
                {"task": "calculate_payment", "day": 1, "time": "09:00"},
                {"task": "send_payment", "day": 5, "time": "09:00"},
                {"task": "optimize_campaigns", "day": 15, "time": "14:00"}
            ]
        }

    def _get_next_payment_date(self) -> str:
        """Get next payment date (5th of next month)"""
        today = datetime.now()
        if today.day < 5:
            payment_date = today.replace(day=5)
        else:
            next_month = today.month + 1 if today.month < 12 else 1
            year = today.year if today.month < 12 else today.year + 1
            payment_date = today.replace(year=year, month=next_month, day=5)
        return payment_date.strftime("%Y-%m-%d")

    def run_daily_automation(self):
        """
        Run daily automation for ALL clients

        This runs once per day and:
        1. Posts social media for each client
        2. Checks analytics
        3. Updates metrics
        4. Tracks leads/revenue
        """
        print(f"\n{'='*60}")
        print(f"RUNNING DAILY AUTOMATION")
        print(f"{'='*60}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Active clients: {len([c for c in self.clients.values() if c['status'] == 'active'])}")
        print()

        for client_id, client in self.clients.items():
            if client["status"] != "active":
                continue

            print(f"\n📊 {client['company_name']}...")

            # Post social media
            posted = self._post_social_media(client_id)

            # Check analytics
            analytics = self._check_analytics(client_id)

            # Update metrics
            self._update_metrics(client_id, analytics)

            print(f"   ✓ Posted: {posted} social posts")
            print(f"   ✓ Leads today: {analytics['leads_today']}")
            print(f"   ✓ Revenue today: ${analytics['revenue_today']:,.2f}")

        self._save_clients()
        self._save_metrics()

        print(f"\n✓ Daily automation complete!")

    def _post_social_media(self, client_id: str) -> int:
        """Post scheduled social media content"""
        client = self.clients[client_id]
        today = datetime.now().date()

        posted = 0
        for post in client["content_schedule"]["social_media"]:
            post_date = datetime.fromisoformat(post["scheduled_date"]).date()
            if post_date == today and post["status"] == "scheduled":
                post["status"] = "posted"
                post["posted_at"] = datetime.now().isoformat()
                posted += 1
                client["metrics"]["total_posts"] += 1

        return posted

    def _check_analytics(self, client_id: str) -> Dict:
        """Check analytics and track performance"""
        # In production, this would call real APIs
        # For now, simulate realistic growth

        client = self.clients[client_id]
        days_active = (datetime.now() - datetime.fromisoformat(client["onboarded_date"])).days

        # Simulate growth over time
        base_leads = random.randint(2, 8)
        growth_factor = min(1 + (days_active * 0.1), 3.0)  # Up to 3x growth

        leads_today = int(base_leads * growth_factor)

        # Revenue per lead varies by industry
        revenue_per_lead = {
            "hvac": random.randint(200, 500),
            "dental": random.randint(150, 400),
            "restaurant": random.randint(50, 150),
            "auto": random.randint(100, 300)
        }.get(client["industry"], random.randint(100, 300))

        revenue_today = leads_today * revenue_per_lead

        return {
            "leads_today": leads_today,
            "revenue_today": revenue_today,
            "conversion_rate": random.uniform(0.15, 0.35),
            "engagement_rate": random.uniform(0.05, 0.15)
        }

    def _update_metrics(self, client_id: str, analytics: Dict):
        """Update client metrics"""
        client = self.clients[client_id]

        # Update totals
        client["metrics"]["leads_generated"] += analytics["leads_today"]
        client["metrics"]["revenue_generated"] += analytics["revenue_today"]

        # Calculate our earnings (based on revenue share)
        share_percent = int(client["revenue_share"].replace("%", "")) / 100
        our_earnings_today = analytics["revenue_today"] * share_percent
        client["metrics"]["our_earnings"] += our_earnings_today

        # Store daily metrics
        if client_id not in self.metrics:
            self.metrics[client_id] = {"daily": [], "weekly": [], "monthly": []}

        self.metrics[client_id]["daily"].append({
            "date": datetime.now().isoformat(),
            "leads": analytics["leads_today"],
            "revenue": analytics["revenue_today"],
            "our_earnings": our_earnings_today
        })

    def calculate_monthly_payments(self):
        """
        Calculate and process monthly payments to all clients

        This runs on the 1st of each month:
        1. Calculate total revenue generated
        2. Calculate their share (80% or 90%)
        3. Generate payment
        4. Send check/transfer
        """
        print(f"\n{'='*60}")
        print(f"MONTHLY PAYMENT PROCESSING")
        print(f"{'='*60}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        print()

        total_payments = 0
        total_our_earnings = 0

        for client_id, client in self.clients.items():
            if client["status"] != "active":
                continue

            # Get this month's metrics
            month_revenue = client["metrics"]["revenue_generated"]
            month_our_earnings = client["metrics"]["our_earnings"]

            # Calculate their payment (they get 80% or 90%)
            share_percent = int(client["revenue_share"].replace("%", "")) / 100
            their_payment = month_revenue * (1 - share_percent)

            print(f"\n💰 {client['company_name']}")
            print(f"   Revenue generated: ${month_revenue:,.2f}")
            print(f"   Their share ({int((1-share_percent)*100)}%): ${their_payment:,.2f}")
            print(f"   Our share ({int(share_percent*100)}%): ${month_our_earnings:,.2f}")

            # Create payment record
            payment = {
                "payment_id": f"pay_{client_id}_{datetime.now().strftime('%Y%m')}",
                "client_id": client_id,
                "company_name": client["company_name"],
                "payment_date": datetime.now().isoformat(),
                "period": datetime.now().strftime("%Y-%m"),
                "total_revenue": month_revenue,
                "their_share": their_payment,
                "our_share": month_our_earnings,
                "payment_method": "check",  # or ACH, wire, etc.
                "status": "processed"
            }

            self.payments.append(payment)

            total_payments += their_payment
            total_our_earnings += month_our_earnings

        print(f"\n{'='*60}")
        print(f"MONTHLY SUMMARY")
        print(f"{'='*60}")
        print(f"Total client payments: ${total_payments:,.2f}")
        print(f"Total our earnings: ${total_our_earnings:,.2f}")
        print(f"Total revenue managed: ${total_payments + total_our_earnings:,.2f}")
        print(f"Active clients: {len([c for c in self.clients.values() if c['status'] == 'active'])}")

        self._save_payments()

        return {
            "total_client_payments": total_payments,
            "total_our_earnings": total_our_earnings,
            "active_clients": len([c for c in self.clients.values() if c["status"] == "active"])
        }

    def get_dashboard(self) -> Dict:
        """Get ecosystem dashboard"""
        active_clients = [c for c in self.clients.values() if c["status"] == "active"]

        total_revenue = sum(c["metrics"]["revenue_generated"] for c in active_clients)
        total_our_earnings = sum(c["metrics"]["our_earnings"] for c in active_clients)
        total_leads = sum(c["metrics"]["leads_generated"] for c in active_clients)

        return {
            "overview": {
                "total_clients": len(self.clients),
                "active_clients": len(active_clients),
                "total_revenue_managed": total_revenue,
                "total_our_earnings": total_our_earnings,
                "total_leads_generated": total_leads
            },
            "clients": [
                {
                    "company": c["company_name"],
                    "industry": c["industry"],
                    "revenue": c["metrics"]["revenue_generated"],
                    "leads": c["metrics"]["leads_generated"],
                    "our_earnings": c["metrics"]["our_earnings"]
                }
                for c in active_clients
            ]
        }

    def print_dashboard(self):
        """Print ecosystem dashboard"""
        dashboard = self.get_dashboard()

        print(f"\n{'='*60}")
        print("ECOSYSTEM DASHBOARD")
        print(f"{'='*60}\n")

        print("📊 OVERVIEW")
        print(f"   Total clients: {dashboard['overview']['total_clients']}")
        print(f"   Active clients: {dashboard['overview']['active_clients']}")
        print(f"   Total revenue managed: ${dashboard['overview']['total_revenue_managed']:,.2f}")
        print(f"   Total our earnings: ${dashboard['overview']['total_our_earnings']:,.2f}")
        print(f"   Total leads generated: {dashboard['overview']['total_leads_generated']}")

        print(f"\n💼 CLIENTS")
        for client in dashboard['clients']:
            print(f"\n   {client['company']} ({client['industry']})")
            print(f"      Revenue: ${client['revenue']:,.2f}")
            print(f"      Leads: {client['leads']}")
            print(f"      Our earnings: ${client['our_earnings']:,.2f}")

        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Client Management System")
    parser.add_argument("--onboard", type=str, help="Onboard new client (company name)")
    parser.add_argument("--industry", type=str, default="hvac", help="Industry")
    parser.add_argument("--split", type=str, default="20%", help="Revenue share (20% or 10%)")
    parser.add_argument("--run-daily", action="store_true", help="Run daily automation")
    parser.add_argument("--process-payments", action="store_true", help="Process monthly payments")
    parser.add_argument("--dashboard", action="store_true", help="Show dashboard")

    args = parser.parse_args()

    cms = ClientManagementSystem()

    if args.onboard:
        deal_info = {
            "company": args.onboard,
            "industry": args.industry,
            "split": args.split,
            "solution": "marketing_automation",
            "deal_value": "$3,000-5,000"
        }
        client = cms.onboard_client(args.onboard, args.industry, deal_info)

    elif args.run_daily:
        cms.run_daily_automation()

    elif args.process_payments:
        cms.calculate_monthly_payments()

    elif args.dashboard:
        cms.print_dashboard()

    else:
        print("Client Management System")
        print("\nUsage:")
        print("  python client_management_system.py --onboard 'Company Name' --industry hvac --split 20%")
        print("  python client_management_system.py --run-daily")
        print("  python client_management_system.py --process-payments")
        print("  python client_management_system.py --dashboard")
