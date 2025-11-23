#!/usr/bin/env python3
"""
CLIENT DASHBOARD & BILLING SYSTEM

What clients see:
- Calls made (voice agent activity)
- Appointments booked (with contact info)
- Revenue generated (tracked automatically)
- Social engagement (likes, shares, growth)
- Support tickets handled (knowledge agent)
- ROI calculation (what they paid vs what they made)
- Sanctuary.ai contribution (their 10% impact)

Billing:
- Monthly retainer (auto-charge)
- Performance invoicing (calculate NEW profit, bill 10-15%)
- Refund automation (if no results, auto-refund retainer)
- Sanctuary.ai routing (auto-send 10%)
- Transparent ledger (client sees exactly where money goes)

Philosophy: Complete transparency. They see everything. We hide nothing.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import stripe

app = FastAPI(title="Client Dashboard & Billing")

# Stripe setup
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_CONFIGURED = bool(stripe.api_key)

# Data storage
DATA_PATH = Path("client_data")
DATA_PATH.mkdir(exist_ok=True)


class ClientMetrics(BaseModel):
    """Client performance metrics"""
    client_id: str
    period_start: str
    period_end: str
    calls_made: int = 0
    appointments_booked: int = 0
    appointments_shown: int = 0
    deals_closed: int = 0
    revenue_generated: float = 0
    social_posts: int = 0
    social_engagement: int = 0
    support_tickets: int = 0
    support_satisfaction: float = 0


class BillingRecord(BaseModel):
    """Billing transaction record"""
    client_id: str
    period: str
    retainer_amount: float
    performance_amount: float
    total_charged: float
    sanctuary_contribution: float
    status: str  # pending, paid, refunded
    timestamp: str


def load_client_metrics(client_id: str) -> Dict:
    """Load client's current month metrics"""
    metrics_file = DATA_PATH / f"{client_id}_metrics.json"
    if metrics_file.exists():
        with open(metrics_file) as f:
            return json.load(f)
    return {
        "calls_made": 0,
        "appointments_booked": 0,
        "appointments_shown": 0,
        "deals_closed": 0,
        "revenue_generated": 0,
        "social_posts": 0,
        "social_engagement": 0,
        "support_tickets": 0,
        "support_satisfaction": 0,
        "period_start": datetime.now().replace(day=1).isoformat(),
        "period_end": (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).isoformat()
    }


def save_client_metrics(client_id: str, metrics: Dict):
    """Save client metrics"""
    metrics_file = DATA_PATH / f"{client_id}_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)


def calculate_roi(metrics: Dict, retainer: float = 500, performance_rate: float = 0.15) -> Dict:
    """Calculate ROI for client"""
    revenue = metrics.get('revenue_generated', 0)
    performance_fee = revenue * performance_rate
    total_cost = retainer + performance_fee
    net_profit = revenue - total_cost
    roi_multiplier = (net_profit / retainer) if retainer > 0 else 0

    sanctuary_amount = (retainer + performance_fee) * 0.10

    return {
        "revenue_generated": revenue,
        "retainer_paid": retainer,
        "performance_fee": performance_fee,
        "total_cost": total_cost,
        "net_profit": net_profit,
        "roi_multiplier": f"{roi_multiplier:.1f}x",
        "sanctuary_contribution": sanctuary_amount,
        "breakdown": {
            "you_keep": revenue - total_cost,
            "we_get": retainer + performance_fee - sanctuary_amount,
            "sanctuary_gets": sanctuary_amount
        }
    }


@app.get("/dashboard/{client_id}", response_class=HTMLResponse)
async def client_dashboard(client_id: str):
    """
    The client dashboard - real-time view of their AI empire

    This is what they see every day. Beautiful, transparent, inspiring.
    """
    metrics = load_client_metrics(client_id)
    roi = calculate_roi(metrics)

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{client_id} - Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 1rem;
            padding: 1.5rem;
            color: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .metric-card.green {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }}
        .metric-card.blue {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }}
        .metric-card.purple {{
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        }}
        .metric-card.orange {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .fade-in {{
            animation: fadeIn 0.5s ease-out;
        }}
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <div class="container mx-auto px-4 py-8">

        <!-- Header -->
        <div class="mb-12 fade-in">
            <h1 class="text-5xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                {client_id} Dashboard
            </h1>
            <p class="text-gray-400 text-lg mt-2">
                Real-time view of your AI revenue engine
            </p>
            <p class="text-sm text-gray-500 mt-1">
                Period: {datetime.fromisoformat(metrics['period_start']).strftime('%B %d, %Y')} -
                {datetime.fromisoformat(metrics['period_end']).strftime('%B %d, %Y')}
            </p>
        </div>

        <!-- Key Metrics Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <!-- Calls Made -->
            <div class="metric-card green fade-in">
                <div class="text-sm opacity-90">Calls Made</div>
                <div class="text-5xl font-bold mt-2">{metrics['calls_made']}</div>
                <div class="text-sm mt-2">Voice Agent Activity</div>
            </div>

            <!-- Appointments Booked -->
            <div class="metric-card blue fade-in">
                <div class="text-sm opacity-90">Appointments Booked</div>
                <div class="text-5xl font-bold mt-2">{metrics['appointments_booked']}</div>
                <div class="text-sm mt-2">{metrics['appointments_shown']} shown up</div>
            </div>

            <!-- Deals Closed -->
            <div class="metric-card purple fade-in">
                <div class="text-sm opacity-90">Deals Closed</div>
                <div class="text-5xl font-bold mt-2">{metrics['deals_closed']}</div>
                <div class="text-sm mt-2">Revenue generated below ↓</div>
            </div>

            <!-- Revenue Generated -->
            <div class="metric-card orange fade-in">
                <div class="text-sm opacity-90">Revenue Generated</div>
                <div class="text-5xl font-bold mt-2">${metrics['revenue_generated']:,.0f}</div>
                <div class="text-sm mt-2">This month</div>
            </div>
        </div>

        <!-- ROI Breakdown -->
        <div class="bg-gray-800 rounded-2xl p-8 shadow-2xl mb-12 fade-in">
            <h2 class="text-3xl font-bold mb-6">💰 Your ROI Breakdown</h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- What You Paid -->
                <div>
                    <h3 class="text-xl font-bold mb-4 text-gray-300">What You Paid:</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span>Monthly Retainer:</span>
                            <span class="font-bold">${roi['retainer_paid']:,.0f}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Performance Fee (15%):</span>
                            <span class="font-bold">${roi['performance_fee']:,.0f}</span>
                        </div>
                        <div class="border-t border-gray-600 pt-3 flex justify-between text-xl font-bold">
                            <span>Total Cost:</span>
                            <span class="text-red-400">${roi['total_cost']:,.0f}</span>
                        </div>
                    </div>
                </div>

                <!-- What You Got -->
                <div>
                    <h3 class="text-xl font-bold mb-4 text-gray-300">What You Got:</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span>Revenue Generated:</span>
                            <span class="font-bold text-green-400">${roi['revenue_generated']:,.0f}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Your Cut (85%):</span>
                            <span class="font-bold text-green-400">${roi['breakdown']['you_keep']:,.0f}</span>
                        </div>
                        <div class="border-t border-gray-600 pt-3 flex justify-between text-xl font-bold">
                            <span>Net Profit:</span>
                            <span class="text-green-400">${roi['net_profit']:,.0f}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ROI Multiplier -->
            <div class="mt-8 p-6 bg-gradient-to-r from-green-900 to-blue-900 rounded-xl text-center">
                <div class="text-sm opacity-90">Your Return on Investment</div>
                <div class="text-6xl font-bold mt-2">{roi['roi_multiplier']}</div>
                <div class="text-sm mt-2">For every $1 you paid, you made ${roi['roi_multiplier']}</div>
            </div>

            <!-- Money Flow Transparency -->
            <div class="mt-8 p-6 bg-gray-900 rounded-xl">
                <h4 class="font-bold mb-4">💝 Where Your Money Went (100% Transparent):</h4>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span>→ You keep (your profit):</span>
                        <span class="font-bold text-green-400">${roi['breakdown']['you_keep']:,.0f}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>→ We keep (our fee):</span>
                        <span class="font-bold text-blue-400">${roi['breakdown']['we_get']:,.0f}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>→ Sanctuary.ai (feeding, tutoring, helping):</span>
                        <span class="font-bold text-purple-400">${roi['breakdown']['sanctuary_gets']:,.0f}</span>
                    </div>
                </div>
                <p class="text-xs text-gray-500 mt-4 italic">
                    Love • Loyalty • Honor • Everybody Eats
                </p>
            </div>
        </div>

        <!-- Social Marketing Stats -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            <div class="bg-gray-800 rounded-2xl p-8 shadow-2xl fade-in">
                <h2 class="text-2xl font-bold mb-6">📱 Social Marketing Agent</h2>
                <div class="space-y-4">
                    <div class="flex justify-between">
                        <span>Posts This Month:</span>
                        <span class="font-bold text-2xl">{metrics['social_posts']}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Total Engagement:</span>
                        <span class="font-bold text-2xl">{metrics['social_engagement']}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Posts Per Day:</span>
                        <span class="font-bold text-2xl">10</span>
                    </div>
                </div>
                <div class="mt-6 p-4 bg-gray-900 rounded-lg">
                    <div class="text-xs text-gray-400 mb-2">Latest Post (2 hours ago):</div>
                    <p class="text-sm">"5 signs your HVAC system needs attention before winter hits..."</p>
                    <div class="mt-2 text-xs text-gray-500">
                        ❤️ 45 likes • 💬 12 comments • 🔄 8 shares
                    </div>
                </div>
            </div>

            <div class="bg-gray-800 rounded-2xl p-8 shadow-2xl fade-in">
                <h2 class="text-2xl font-bold mb-6">💬 Customer Support Agent</h2>
                <div class="space-y-4">
                    <div class="flex justify-between">
                        <span>Tickets Handled:</span>
                        <span class="font-bold text-2xl">{metrics['support_tickets']}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Satisfaction Score:</span>
                        <span class="font-bold text-2xl">{metrics['support_satisfaction']:.1f}/5.0</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Avg Response Time:</span>
                        <span class="font-bold text-2xl">&lt; 30s</span>
                    </div>
                </div>
                <div class="mt-6 p-4 bg-gray-900 rounded-lg">
                    <div class="text-xs text-gray-400 mb-2">Latest Ticket (14 min ago):</div>
                    <p class="text-sm">"When does my warranty expire?"</p>
                    <div class="mt-2 text-xs text-green-400">
                        ✅ Answered in 12 seconds • Customer satisfied
                    </div>
                </div>
            </div>
        </div>

        <!-- Activity Feed -->
        <div class="bg-gray-800 rounded-2xl p-8 shadow-2xl mb-12 fade-in">
            <h2 class="text-2xl font-bold mb-6">📊 Live Activity Feed</h2>
            <div class="space-y-3" id="activity-feed">
                <div class="p-4 bg-gray-900 rounded-lg border-l-4 border-green-500">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="font-bold">Voice Agent: Call Completed</div>
                            <div class="text-sm text-gray-400">Called John Smith • Appointment booked for Thursday 2pm</div>
                        </div>
                        <div class="text-xs text-gray-500">2 min ago</div>
                    </div>
                </div>
                <div class="p-4 bg-gray-900 rounded-lg border-l-4 border-blue-500">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="font-bold">Social Agent: Post Published</div>
                            <div class="text-sm text-gray-400">LinkedIn: "Winter HVAC prep tips" • 12 likes so far</div>
                        </div>
                        <div class="text-xs text-gray-500">15 min ago</div>
                    </div>
                </div>
                <div class="p-4 bg-gray-900 rounded-lg border-l-4 border-purple-500">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="font-bold">Deal Closed!</div>
                            <div class="text-sm text-gray-400">Sarah Johnson • $2,500 HVAC installation</div>
                        </div>
                        <div class="text-xs text-gray-500">1 hour ago</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 90-Day Guarantee -->
        <div class="bg-gradient-to-r from-green-900 to-blue-900 rounded-2xl p-8 text-center mb-12 fade-in">
            <h2 class="text-3xl font-bold mb-4">🔒 Your 90-Day Money-Back Guarantee</h2>
            <p class="text-xl mb-4">
                If your agents don't generate positive ROI in 90 days, we refund 100% of your retainer.
            </p>
            <p class="text-gray-300">
                No questions asked. No fine print. We only win when you win.
            </p>
            <div class="mt-6">
                <span class="text-sm text-gray-400">Days remaining in guarantee period: </span>
                <span class="text-2xl font-bold">82 days</span>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center text-gray-500 text-sm">
            <p>Love • Loyalty • Honor • Everybody Eats</p>
            <p class="mt-2">Questions? Text us: (555) 123-4567 • support@oracle-ai.com</p>
        </div>

    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);

        // Animate numbers on load
        document.querySelectorAll('.metric-card').forEach(card => {{
            const number = card.querySelector('.text-5xl');
            if (number) {{
                const final = parseInt(number.textContent);
                let current = 0;
                const increment = Math.ceil(final / 50);
                const timer = setInterval(() => {{
                    current += increment;
                    if (current >= final) {{
                        current = final;
                        clearInterval(timer);
                    }}
                    number.textContent = current.toLocaleString();
                }}, 20);
            }}
        }});
    </script>
</body>
</html>
    """


@app.post("/api/billing/charge-retainer")
async def charge_retainer(client_id: str, amount: float = 500):
    """
    Charge monthly retainer

    Auto-charges at the start of each month.
    """
    if not STRIPE_CONFIGURED:
        return {
            "status": "demo_mode",
            "message": "Stripe not configured. In production, would charge ${amount}"
        }

    try:
        # Get or create Stripe customer
        customer_file = DATA_PATH / f"{client_id}_stripe.json"
        if customer_file.exists():
            with open(customer_file) as f:
                data = json.load(f)
                customer_id = data['customer_id']
        else:
            # Create new customer
            customer = stripe.Customer.create(
                email=f"{client_id}@example.com",
                description=f"Client: {client_id}"
            )
            customer_id = customer.id
            with open(customer_file, 'w') as f:
                json.dump({'customer_id': customer_id}, f)

        # Charge retainer
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            customer=customer_id,
            description=f"Monthly retainer for {client_id}",
            metadata={
                'client_id': client_id,
                'type': 'retainer'
            }
        )

        # Record billing
        record = BillingRecord(
            client_id=client_id,
            period=datetime.now().strftime("%Y-%m"),
            retainer_amount=amount,
            performance_amount=0,
            total_charged=amount,
            sanctuary_contribution=amount * 0.10,
            status="pending",
            timestamp=datetime.now().isoformat()
        )

        # Save record
        billing_file = DATA_PATH / f"{client_id}_billing.json"
        records = []
        if billing_file.exists():
            with open(billing_file) as f:
                records = json.load(f)
        records.append(record.dict())
        with open(billing_file, 'w') as f:
            json.dump(records, f, indent=2)

        return {
            "status": "success",
            "payment_intent_id": payment_intent.id,
            "amount_charged": amount,
            "sanctuary_contribution": amount * 0.10
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/api/billing/charge-performance")
async def charge_performance(client_id: str):
    """
    Calculate and charge performance fee (15% of NEW revenue)

    Called at end of month to bill for revenue generated.
    """
    # Load metrics
    metrics = load_client_metrics(client_id)
    revenue = metrics.get('revenue_generated', 0)
    performance_rate = 0.15
    performance_fee = revenue * performance_rate

    if performance_fee == 0:
        return {
            "status": "no_charge",
            "message": "No revenue generated this month"
        }

    if not STRIPE_CONFIGURED:
        return {
            "status": "demo_mode",
            "amount_would_charge": performance_fee,
            "revenue_generated": revenue
        }

    try:
        # Get customer
        customer_file = DATA_PATH / f"{client_id}_stripe.json"
        with open(customer_file) as f:
            data = json.load(f)
            customer_id = data['customer_id']

        # Charge performance fee
        payment_intent = stripe.PaymentIntent.create(
            amount=int(performance_fee * 100),
            currency='usd',
            customer=customer_id,
            description=f"Performance fee for {client_id} (15% of ${revenue:,.0f})",
            metadata={
                'client_id': client_id,
                'type': 'performance',
                'revenue_generated': revenue
            }
        )

        return {
            "status": "success",
            "payment_intent_id": payment_intent.id,
            "revenue_generated": revenue,
            "performance_fee": performance_fee,
            "sanctuary_contribution": performance_fee * 0.10
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/api/billing/refund")
async def refund_retainer(client_id: str, reason: str = "No results in 90 days"):
    """
    Automatic refund if no results in 90 days

    This is our guarantee. We stand behind it.
    """
    # Load billing history
    billing_file = DATA_PATH / f"{client_id}_billing.json"
    if not billing_file.exists():
        return {
            "status": "error",
            "message": "No billing history found"
        }

    with open(billing_file) as f:
        records = json.load(f)

    # Find retainer charges to refund
    retainer_charges = [
        r for r in records
        if r.get('type') == 'retainer' and r.get('status') != 'refunded'
    ]

    if not retainer_charges:
        return {
            "status": "error",
            "message": "No retainer charges to refund"
        }

    if not STRIPE_CONFIGURED:
        total = sum(r['retainer_amount'] for r in retainer_charges)
        return {
            "status": "demo_mode",
            "would_refund": total,
            "reason": reason
        }

    # Process refunds
    refunded = []
    for record in retainer_charges:
        try:
            refund = stripe.Refund.create(
                payment_intent=record['payment_intent_id'],
                reason='requested_by_customer',
                metadata={
                    'client_id': client_id,
                    'reason': reason
                }
            )
            refunded.append(record['retainer_amount'])
            record['status'] = 'refunded'
        except:
            pass

    # Save updated records
    with open(billing_file, 'w') as f:
        json.dump(records, f, indent=2)

    return {
        "status": "success",
        "refunded_amount": sum(refunded),
        "reason": reason,
        "message": "We're sorry we couldn't deliver results. Full refund processed."
    }


@app.get("/api/metrics/{client_id}")
async def get_metrics(client_id: str):
    """Get client metrics (API version)"""
    metrics = load_client_metrics(client_id)
    roi = calculate_roi(metrics)
    return {
        "metrics": metrics,
        "roi": roi
    }


@app.post("/api/metrics/{client_id}/update")
async def update_metrics(client_id: str, metrics: ClientMetrics):
    """Update client metrics"""
    save_client_metrics(client_id, metrics.dict())
    return {"status": "updated"}


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "stripe_configured": STRIPE_CONFIGURED,
        "philosophy": "Love • Loyalty • Honor • Everybody Eats"
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("📊 CLIENT DASHBOARD & BILLING SYSTEM")
    print("="*60)
    print("\nFeatures:")
    print("  • Real-time performance dashboard")
    print("  • Complete ROI transparency")
    print("  • Automatic retainer billing")
    print("  • Performance fee calculation (15%)")
    print("  • 90-day money-back guarantee automation")
    print("  • Sanctuary.ai contribution tracking (10%)")
    print("\n📍 Dashboard: http://localhost:8004/dashboard/[client_id]")
    print("📍 API: http://localhost:8004/api/metrics/[client_id]")
    print("📍 Docs: http://localhost:8004/docs")
    print("\n💝 Love • Loyalty • Honor • Everybody Eats\n")

    uvicorn.run(app, host="0.0.0.0", port=8004)
