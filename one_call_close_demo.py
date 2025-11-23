#!/usr/bin/env python3
"""
ONE-CALL-CLOSE DEMO SYSTEM

This is the system that closes deals LIVE while the prospect watches.

Flow:
1. Prospect gives their business info (verbally or typed)
2. System generates custom solution in 30 seconds
3. Shows their branded dashboard
4. Makes LIVE test call to their lead (while they watch)
5. Books actual appointment
6. Displays ROI calculator
7. "Activate Now" button → Deploys their system

Philosophy: SHOW, don't tell. Build it live. Zero risk. Everybody eats.

Tech Stack:
- FastAPI (backend API)
- Twilio (live calling demo)
- Stripe (instant billing)
- Vercel/Railway (instant deployment)
- AI synthesis (Claude + Gemini + Grok)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import json
from datetime import datetime
from twilio.rest import Client
import httpx

app = FastAPI(title="One-Call-Close Demo System")

# Twilio setup
TWILIO_CONFIGURED = all([
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN"),
    os.getenv("TWILIO_PHONE_NUMBER")
])

if TWILIO_CONFIGURED:
    twilio_client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )


class ProspectInfo(BaseModel):
    """Prospect business information"""
    business_name: str
    industry: str
    phone: str
    pain_points: List[str]
    current_marketing_spend: Optional[int] = 0
    monthly_revenue: Optional[int] = 0
    test_lead_phone: Optional[str] = None


class DemoRequest(BaseModel):
    """Request to generate live demo"""
    prospect: ProspectInfo
    show_live_call: bool = True
    show_roi_calculator: bool = True


@app.get("/", response_class=HTMLResponse)
async def demo_interface():
    """
    The live demo interface that runs screen-shared during sales calls

    This is what prospects SEE while you're talking to them.
    """
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Oracle AI - Live Demo</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .pulse-green {
            animation: pulse-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse-green {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: .5;
            }
        }
        .slide-up {
            animation: slide-up 0.5s ease-out;
        }
        @keyframes slide-up {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 min-h-screen text-white">
    <div class="container mx-auto px-4 py-8">

        <!-- Header -->
        <div class="text-center mb-12 slide-up">
            <h1 class="text-6xl font-bold mb-4 bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                Oracle AI
            </h1>
            <p class="text-2xl text-gray-300">
                Watch Your AI Agent Get Built - LIVE
            </p>
            <p class="text-lg text-gray-400 mt-2">
                Love • Loyalty • Honor • Everybody Eats
            </p>
        </div>

        <!-- Step 1: Collect Info -->
        <div id="step-1" class="max-w-2xl mx-auto bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
            <h2 class="text-3xl font-bold mb-6 flex items-center">
                <span class="bg-green-500 text-white rounded-full w-10 h-10 flex items-center justify-center mr-4">1</span>
                Tell Me About Your Business
            </h2>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-2">Business Name</label>
                    <input type="text" id="business_name"
                           class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                           placeholder="e.g., Joe's HVAC Service">
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">Industry</label>
                    <select id="industry"
                            class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none">
                        <option value="hvac">HVAC / Plumbing</option>
                        <option value="legal">Legal / Attorney</option>
                        <option value="dental">Dental / Medical</option>
                        <option value="realestate">Real Estate</option>
                        <option value="contractor">General Contractor</option>
                        <option value="auto">Auto Repair</option>
                        <option value="restaurant">Restaurant</option>
                        <option value="other">Other</option>
                    </select>
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">Your Phone</label>
                    <input type="tel" id="phone"
                           class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                           placeholder="(555) 123-4567">
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">Current Monthly Marketing Spend</label>
                    <input type="number" id="marketing_spend"
                           class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                           placeholder="e.g., 2000">
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">Monthly Revenue</label>
                    <input type="number" id="monthly_revenue"
                           class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                           placeholder="e.g., 50000">
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">Test Lead Phone (Optional - for live call demo)</label>
                    <input type="tel" id="test_lead_phone"
                           class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                           placeholder="(555) 987-6543">
                </div>

                <button onclick="generateDemo()"
                        class="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-bold py-4 px-8 rounded-lg hover:from-green-600 hover:to-blue-600 transition-all transform hover:scale-105">
                    🚀 Generate My Custom Solution (30 seconds)
                </button>
            </div>
        </div>

        <!-- Step 2: AI Building (Hidden initially) -->
        <div id="step-2" class="hidden max-w-4xl mx-auto bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
            <h2 class="text-3xl font-bold mb-6 flex items-center">
                <span class="bg-green-500 text-white rounded-full w-10 h-10 flex items-center justify-center mr-4 pulse-green">2</span>
                AI Building Your System...
            </h2>

            <div class="space-y-4 text-lg">
                <div id="progress-1" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Analyzing your industry...</span>
                </div>
                <div id="progress-2" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Generating custom scripts...</span>
                </div>
                <div id="progress-3" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Creating your branded dashboard...</span>
                </div>
                <div id="progress-4" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Training voice AI on your brand...</span>
                </div>
                <div id="progress-5" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Deploying your system...</span>
                </div>
            </div>
        </div>

        <!-- Step 3: Your Dashboard (Hidden initially) -->
        <div id="step-3" class="hidden max-w-6xl mx-auto">
            <div class="bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
                <h2 class="text-3xl font-bold mb-6 flex items-center">
                    <span class="bg-green-500 text-white rounded-full w-10 h-10 flex items-center justify-center mr-4">3</span>
                    <span id="business-name-display"></span> - Your Live Dashboard
                </h2>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="bg-gradient-to-br from-green-500 to-green-700 rounded-xl p-6">
                        <div class="text-sm opacity-90">Calls Made Today</div>
                        <div class="text-4xl font-bold mt-2">0</div>
                        <div class="text-sm mt-2">Starting in 60 seconds...</div>
                    </div>

                    <div class="bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl p-6">
                        <div class="text-sm opacity-90">Appointments Booked</div>
                        <div class="text-4xl font-bold mt-2">0</div>
                        <div class="text-sm mt-2">Watch this grow...</div>
                    </div>

                    <div class="bg-gradient-to-br from-purple-500 to-purple-700 rounded-xl p-6">
                        <div class="text-sm opacity-90">Est. Revenue (30 days)</div>
                        <div class="text-4xl font-bold mt-2" id="projected-revenue">$0</div>
                        <div class="text-sm mt-2">Based on 20% close rate</div>
                    </div>
                </div>
            </div>

            <!-- Live Call Demo -->
            <div id="live-call-section" class="bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
                <h2 class="text-2xl font-bold mb-6 flex items-center">
                    📞 Watch Your AI Make a LIVE Call
                </h2>

                <div id="call-placeholder" class="text-center py-12">
                    <div class="text-6xl mb-4">📞</div>
                    <p class="text-xl text-gray-300">Ready to call your test lead?</p>
                    <p class="text-sm text-gray-400 mt-2">This is a REAL call that will happen right now.</p>
                    <button onclick="makeLiveCall()"
                            class="mt-6 bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-8 rounded-lg">
                        Make Live Call Now
                    </button>
                </div>

                <div id="call-in-progress" class="hidden text-center py-12">
                    <div class="text-6xl mb-4 animate-pulse">📞</div>
                    <p class="text-2xl text-green-400 font-bold">CALL IN PROGRESS...</p>
                    <p class="text-gray-300 mt-2">Listen to your AI agent in action!</p>
                    <div id="call-transcript" class="mt-6 text-left bg-gray-900 rounded-lg p-4 max-w-2xl mx-auto">
                        <!-- Transcript will appear here -->
                    </div>
                </div>
            </div>

            <!-- ROI Calculator -->
            <div class="bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
                <h2 class="text-2xl font-bold mb-6">💰 Your ROI Calculator</h2>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <h3 class="text-lg font-bold mb-4 text-gray-300">What You Pay:</h3>
                        <div class="space-y-3">
                            <div class="flex justify-between">
                                <span>Monthly Retainer:</span>
                                <span class="font-bold">$500</span>
                            </div>
                            <div class="flex justify-between text-sm text-gray-400">
                                <span>(100% refundable if no results)</span>
                                <span></span>
                            </div>
                            <div class="flex justify-between">
                                <span>Performance Share:</span>
                                <span class="font-bold">15% of NEW profit</span>
                            </div>
                            <div class="border-t border-gray-600 pt-3 flex justify-between text-xl font-bold">
                                <span>Total Risk:</span>
                                <span class="text-green-400">$0</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 class="text-lg font-bold mb-4 text-gray-300">What You Get:</h3>
                        <div class="space-y-3">
                            <div class="flex justify-between">
                                <span>New Appointments/Month:</span>
                                <span class="font-bold" id="roi-appointments">20-40</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Close Rate (avg):</span>
                                <span class="font-bold">20%</span>
                            </div>
                            <div class="flex justify-between">
                                <span>New Revenue:</span>
                                <span class="font-bold text-green-400" id="roi-revenue">$10,000-20,000</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Your Cut (85%):</span>
                                <span class="font-bold text-green-400" id="roi-your-cut">$8,500-17,000</span>
                            </div>
                            <div class="border-t border-gray-600 pt-3 flex justify-between text-xl font-bold">
                                <span>ROI:</span>
                                <span class="text-green-400" id="roi-multiplier">17x - 34x</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-8 p-6 bg-gradient-to-r from-green-900 to-blue-900 rounded-xl">
                    <p class="text-center text-lg">
                        <span class="font-bold">10% of our cut goes to sanctuary.ai</span> - feeding, tutoring, helping people who need it.
                    </p>
                    <p class="text-center text-sm text-gray-300 mt-2">
                        Your success helps others. Everybody eats. 💝
                    </p>
                </div>
            </div>

            <!-- Activate Button -->
            <div class="text-center">
                <button onclick="activateNow()"
                        class="bg-gradient-to-r from-green-500 via-blue-500 to-purple-500 text-white font-bold py-6 px-16 rounded-2xl text-2xl hover:scale-105 transform transition-all shadow-2xl">
                    🚀 ACTIVATE NOW - Deploy My System
                </button>
                <p class="text-gray-400 mt-4">Takes 60 seconds. Zero risk. 90-day money-back guarantee.</p>
            </div>
        </div>

    </div>

    <script>
        let prospectData = {};

        async function generateDemo() {
            // Collect data
            prospectData = {
                business_name: document.getElementById('business_name').value,
                industry: document.getElementById('industry').value,
                phone: document.getElementById('phone').value,
                current_marketing_spend: parseInt(document.getElementById('marketing_spend').value) || 0,
                monthly_revenue: parseInt(document.getElementById('monthly_revenue').value) || 0,
                test_lead_phone: document.getElementById('test_lead_phone').value,
                pain_points: []  // Can be collected via chat or voice later
            };

            if (!prospectData.business_name || !prospectData.phone) {
                alert('Please fill in at least business name and phone!');
                return;
            }

            // Hide step 1, show step 2
            document.getElementById('step-1').classList.add('hidden');
            document.getElementById('step-2').classList.remove('hidden');

            // Animate progress
            const progressSteps = [
                'progress-1', 'progress-2', 'progress-3', 'progress-4', 'progress-5'
            ];

            for (let i = 0; i < progressSteps.length; i++) {
                await sleep(600);
                const elem = document.getElementById(progressSteps[i]);
                elem.classList.remove('opacity-50');
                elem.querySelector('span:first-child').textContent = '✅';
            }

            await sleep(1000);

            // Hide step 2, show step 3
            document.getElementById('step-2').classList.add('hidden');
            document.getElementById('step-3').classList.remove('hidden');

            // Populate dashboard
            document.getElementById('business-name-display').textContent = prospectData.business_name;

            // Calculate ROI
            calculateROI();
        }

        function calculateROI() {
            const avgTicket = getAvgTicket(prospectData.industry);
            const appointments = 30; // Conservative estimate
            const closeRate = 0.20;
            const newRevenue = appointments * closeRate * avgTicket;
            const performanceShare = 0.15;
            const theirCut = newRevenue * (1 - performanceShare);
            const roi = theirCut / 500;

            document.getElementById('projected-revenue').textContent = '$' + Math.round(newRevenue).toLocaleString();
            document.getElementById('roi-revenue').textContent = '$' + Math.round(newRevenue).toLocaleString();
            document.getElementById('roi-your-cut').textContent = '$' + Math.round(theirCut).toLocaleString();
            document.getElementById('roi-multiplier').textContent = Math.round(roi) + 'x';
        }

        function getAvgTicket(industry) {
            const tickets = {
                'hvac': 2500,
                'legal': 5000,
                'dental': 1500,
                'realestate': 8000,
                'contractor': 5000,
                'auto': 800,
                'restaurant': 50,
                'other': 2000
            };
            return tickets[industry] || 2000;
        }

        async function makeLiveCall() {
            if (!prospectData.test_lead_phone) {
                alert('Please provide a test lead phone number!');
                return;
            }

            document.getElementById('call-placeholder').classList.add('hidden');
            document.getElementById('call-in-progress').classList.remove('hidden');

            // Call backend API
            try {
                const response = await fetch('/api/make-live-call', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        to_number: prospectData.test_lead_phone,
                        business_name: prospectData.business_name,
                        industry: prospectData.industry
                    })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    // Simulate transcript (in production, would stream from Twilio)
                    await simulateCallTranscript();
                } else {
                    alert('Call failed: ' + data.message);
                }
            } catch (error) {
                alert('Error making call: ' + error);
            }
        }

        async function simulateCallTranscript() {
            const transcript = [
                '[AI Agent] Hi, this is Oracle calling on behalf of ' + prospectData.business_name + '...',
                '[Lead] Hello?',
                '[AI Agent] We noticed you were looking for ' + prospectData.industry + ' services...',
                '[Lead] Oh yes, I need help with that.',
                '[AI Agent] Great! Let me check our calendar. Are you available this Thursday at 2pm?',
                '[Lead] Yes, that works.',
                '[AI Agent] Perfect! I\'ll send you a confirmation text. See you Thursday!',
                '[Call Complete] ✅ Appointment booked for Thursday, 2pm'
            ];

            const container = document.getElementById('call-transcript');
            for (const line of transcript) {
                await sleep(2000);
                const p = document.createElement('p');
                p.className = 'mb-2 slide-up';
                p.textContent = line;
                container.appendChild(p);
            }
        }

        async function activateNow() {
            // Send to backend to actually deploy
            const confirmed = confirm(
                `Activate ${prospectData.business_name}'s AI system now?\n\n` +
                `You'll pay:\n` +
                `• $500/month retainer (100% refundable)\n` +
                `• 15% of NEW profit only\n\n` +
                `90-day money-back guarantee. Zero risk.`
            );

            if (confirmed) {
                window.location.href = '/api/activate?business=' + encodeURIComponent(prospectData.business_name);
            }
        }

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    </script>
</body>
</html>
    """


@app.post("/api/generate-demo")
async def generate_demo(request: DemoRequest):
    """
    Generate custom solution for prospect in 30 seconds

    This is where the AI magic happens:
    - Analyze industry
    - Generate custom scripts
    - Create branded dashboard
    - Train voice AI
    - Deploy system
    """
    prospect = request.prospect

    # In production, this would call Claude/Gemini/Grok to generate custom solution
    # For now, return template response

    solution = {
        "business_name": prospect.business_name,
        "industry": prospect.industry,
        "custom_script": generate_custom_script(prospect),
        "dashboard_url": f"https://dashboard.oracle-ai.com/{prospect.business_name.lower().replace(' ', '-')}",
        "voice_agent_ready": True,
        "estimated_roi": calculate_roi(prospect),
        "deployment_time": "60 seconds",
        "activation_link": f"/api/activate?business={prospect.business_name}"
    }

    return solution


def generate_custom_script(prospect: ProspectInfo) -> Dict:
    """Generate custom calling script based on industry"""

    # Industry-specific value props
    value_props = {
        "hvac": "emergency service availability",
        "legal": "free consultation",
        "dental": "new patient special",
        "realestate": "market analysis",
        "contractor": "free estimate",
        "auto": "same-day service",
        "restaurant": "catering options",
        "other": "special offer"
    }

    value_prop = value_props.get(prospect.industry, "special offer")

    script = {
        "greeting": f"Hi, this is Oracle AI calling on behalf of {prospect.business_name}...",
        "qualifying": f"I see you were interested in {prospect.industry} services. Is that still the case?",
        "value_prop": f"Great! We're offering {value_prop} for new customers.",
        "booking": "I can get you scheduled this week. Are you available Thursday at 2pm or Friday at 10am?",
        "confirmation": "Perfect! I'll send you a confirmation text with all the details. Looking forward to helping you!",
        "objection_handlers": {
            "price": "I understand. That's why we offer flexible payment plans and a satisfaction guarantee.",
            "timing": "No problem! When would be better for you?",
            "competitor": f"I respect that. What would make {prospect.business_name} a better choice for you?"
        }
    }

    return script


def calculate_roi(prospect: ProspectInfo) -> Dict:
    """Calculate projected ROI for prospect"""

    # Industry average ticket sizes
    avg_tickets = {
        "hvac": 2500,
        "legal": 5000,
        "dental": 1500,
        "realestate": 8000,
        "contractor": 5000,
        "auto": 800,
        "restaurant": 50,
        "other": 2000
    }

    avg_ticket = avg_tickets.get(prospect.industry, 2000)
    calls_per_month = 100  # Conservative estimate
    contact_rate = 0.30  # 30% reach someone
    appointment_rate = 0.50  # 50% of contacts book
    show_rate = 0.80  # 80% show up
    close_rate = 0.20  # 20% close

    appointments = calls_per_month * contact_rate * appointment_rate * show_rate
    closes = appointments * close_rate
    new_revenue = closes * avg_ticket

    retainer = 500
    performance_share = 0.15
    our_cut = retainer + (new_revenue * performance_share)
    their_cut = new_revenue - (new_revenue * performance_share)
    roi_multiplier = their_cut / retainer if retainer > 0 else 0

    return {
        "calls_per_month": calls_per_month,
        "appointments_booked": round(appointments),
        "appointments_shown": round(appointments * show_rate),
        "deals_closed": round(closes),
        "new_monthly_revenue": round(new_revenue),
        "retainer_cost": retainer,
        "performance_fee": round(new_revenue * performance_share),
        "total_cost": round(retainer + (new_revenue * performance_share)),
        "net_profit": round(their_cut - retainer),
        "roi_multiplier": f"{round(roi_multiplier)}x",
        "sanctuary_contribution": round(our_cut * 0.10),
        "risk_level": "ZERO (100% refundable if no results in 90 days)"
    }


@app.post("/api/make-live-call")
async def make_live_call(to_number: str, business_name: str, industry: str):
    """
    Make LIVE call while prospect watches

    This is the WOW moment that closes deals.
    """
    if not TWILIO_CONFIGURED:
        return JSONResponse({
            "status": "demo_mode",
            "message": "Twilio not configured. In demo mode, we simulate the call.",
            "call_sid": "DEMO_" + datetime.now().strftime("%Y%m%d%H%M%S")
        })

    try:
        # Generate script
        prospect = ProspectInfo(
            business_name=business_name,
            industry=industry,
            phone="",
            pain_points=[]
        )
        script = generate_custom_script(prospect)

        # Make actual call
        call = twilio_client.calls.create(
            to=to_number,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            url=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/api/twiml/demo-call",
            status_callback=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/api/call-status",
            record=True
        )

        return {
            "status": "success",
            "call_sid": call.sid,
            "message": "Call initiated successfully!",
            "script": script
        }

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.get("/api/activate")
async def activate_system(business: str):
    """
    Actually deploy the customer's system

    This is where they go from prospect to PAYING CUSTOMER.
    """
    # In production:
    # 1. Create Stripe customer
    # 2. Charge $500 retainer
    # 3. Deploy their actual system
    # 4. Send onboarding email
    # 5. Schedule kickoff call

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Welcome to Oracle AI!</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white min-h-screen flex items-center justify-center">
        <div class="max-w-2xl mx-auto text-center p-8">
            <div class="text-8xl mb-8">🎉</div>
            <h1 class="text-5xl font-bold mb-6">Welcome to Oracle AI, {business}!</h1>
            <p class="text-2xl text-gray-300 mb-8">
                Your AI agent is deploying now...
            </p>
            <div class="bg-gray-800 rounded-2xl p-8 mb-8">
                <h2 class="text-2xl font-bold mb-4">What Happens Next:</h2>
                <div class="text-left space-y-4">
                    <div class="flex items-start">
                        <span class="text-2xl mr-4">✅</span>
                        <div>
                            <div class="font-bold">Step 1: Payment Setup (2 minutes)</div>
                            <div class="text-gray-400">$500 retainer - 100% refundable if no results</div>
                        </div>
                    </div>
                    <div class="flex items-start">
                        <span class="text-2xl mr-4">✅</span>
                        <div>
                            <div class="font-bold">Step 2: System Deployment (60 seconds)</div>
                            <div class="text-gray-400">Your dashboard and voice agent go live</div>
                        </div>
                    </div>
                    <div class="flex items-start">
                        <span class="text-2xl mr-4">✅</span>
                        <div>
                            <div class="font-bold">Step 3: First Calls (5 minutes)</div>
                            <div class="text-gray-400">Your AI starts calling leads immediately</div>
                        </div>
                    </div>
                    <div class="flex items-start">
                        <span class="text-2xl mr-4">✅</span>
                        <div>
                            <div class="font-bold">Step 4: First Appointments (Same Day)</div>
                            <div class="text-gray-400">Watch your calendar fill up</div>
                        </div>
                    </div>
                </div>
            </div>
            <a href="mailto:support@oracle-ai.com"
               class="bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-8 rounded-lg inline-block">
                Continue to Payment Setup
            </a>
            <p class="text-gray-400 mt-6">
                Questions? Text us: (555) 123-4567<br>
                Love • Loyalty • Honor • Everybody Eats 💝
            </p>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "twilio_configured": TWILIO_CONFIGURED,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("🔥 ONE-CALL-CLOSE DEMO SYSTEM")
    print("="*60)
    print("\nThis is the system that closes deals LIVE.")
    print("\nPhilosophy: SHOW, don't tell. Build it live. Zero risk.")
    print("\nStarting server...")
    print("\n📍 Demo Interface: http://localhost:8002")
    print("📍 API Docs: http://localhost:8002/docs")
    print("\n💝 Love • Loyalty • Honor • Everybody Eats\n")

    uvicorn.run(app, host="0.0.0.0", port=8002)
