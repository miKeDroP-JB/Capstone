#!/usr/bin/env python3
"""
ECOSYSTEM SIMULATION - Show 30-Day Operation
=============================================
Simulate running the ecosystem for 30 days to demonstrate:
- Daily automation
- Revenue generation
- Metric tracking
- Monthly payments
"""

from client_management_system import ClientManagementSystem
from datetime import datetime, timedelta
import json

def simulate_30_days():
    """Simulate 30 days of ecosystem operation"""

    print(f"\n{'='*60}")
    print("30-DAY ECOSYSTEM SIMULATION")
    print(f"{'='*60}\n")

    cms = ClientManagementSystem()

    # Get our client
    clients = list(cms.clients.values())
    if not clients:
        print("❌ No clients found. Run onboarding first.")
        return

    client = clients[0]
    client_id = client["id"]

    print(f"Client: {client['company_name']}")
    print(f"Revenue Share: {client['revenue_share']}")
    print(f"Running 30-day simulation...\n")

    # Simulate 30 days
    for day in range(1, 31):
        print(f"Day {day:2d}: ", end="")

        # Post social media
        posted = cms._post_social_media(client_id)

        # Check analytics (simulate daily performance)
        analytics = cms._check_analytics(client_id)

        # Update metrics
        cms._update_metrics(client_id, analytics)

        print(f"Posted {posted} | Leads: {analytics['leads_today']:2d} | Revenue: ${analytics['revenue_today']:5,.0f}")

    # Save all changes
    cms._save_clients()
    cms._save_metrics()

    # Show final metrics
    print(f"\n{'='*60}")
    print("30-DAY RESULTS")
    print(f"{'='*60}\n")

    final_client = cms.clients[client_id]
    metrics = final_client["metrics"]

    print(f"Total posts: {metrics['total_posts']}")
    print(f"Total leads: {metrics['leads_generated']}")
    print(f"Total revenue generated: ${metrics['revenue_generated']:,.2f}")
    print(f"Total our earnings: ${metrics['our_earnings']:,.2f}")

    # Calculate their payment
    share_percent = int(client['revenue_share'].replace('%', '')) / 100
    their_payment = metrics['revenue_generated'] * (1 - share_percent)

    print(f"\n💰 PAYMENT BREAKDOWN")
    print(f"   Total revenue: ${metrics['revenue_generated']:,.2f}")
    print(f"   Their share (80%): ${their_payment:,.2f}")
    print(f"   Our share (20%): ${metrics['our_earnings']:,.2f}")

    print(f"\n✓ Client gets check for: ${their_payment:,.2f}")
    print(f"✓ We earned: ${metrics['our_earnings']:,.2f}")

    # Show ROI
    print(f"\n📊 ECOSYSTEM METRICS")
    print(f"   Client investment: $0 (free upfront)")
    print(f"   Client return: ${their_payment:,.2f}")
    print(f"   Client ROI: ∞ (infinite - they paid nothing)")
    print(f"   Our time investment: ~2 hours setup")
    print(f"   Our earnings: ${metrics['our_earnings']:,.2f}")
    print(f"   Our hourly rate: ${metrics['our_earnings']/2:,.2f}/hour")

    # Extrapolate
    print(f"\n🚀 SCALE PROJECTION")
    monthly_earnings_per_client = metrics['our_earnings']

    print(f"   With 1 client: ${monthly_earnings_per_client:,.2f}/month")
    print(f"   With 10 clients: ${monthly_earnings_per_client * 10:,.2f}/month")
    print(f"   With 50 clients: ${monthly_earnings_per_client * 50:,.2f}/month")
    print(f"   With 100 clients: ${monthly_earnings_per_client * 100:,.2f}/month")

    print(f"\n💡 THIS IS THE MODEL")
    print(f"   - Client pays $0 upfront")
    print(f"   - We do ALL the work")
    print(f"   - We track EVERYTHING")
    print(f"   - They get checks monthly")
    print(f"   - We scale infinitely")
    print(f"   - Everybody eats!")

    return cms

if __name__ == "__main__":
    cms = simulate_30_days()

    # Now process the actual payment
    print(f"\n{'='*60}")
    print("PROCESSING PAYMENT")
    print(f"{'='*60}\n")

    cms.calculate_monthly_payments()

    # Show dashboard
    cms.print_dashboard()
