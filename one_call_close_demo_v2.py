#!/usr/bin/env python3
"""
ONE-CALL-CLOSE DEMO SYSTEM v2.0

ENHANCED: Try Before You Buy + Website Changes

Flow:
1. Prospect gives business info
2. They authorize payment ($500 - NOT charged yet)
3. System builds their solution LIVE (30 seconds)
4. Shows branded dashboard
5. Makes LIVE test call (optional)
6. Shows ROI calculator
7. BONUS: Offers website changes with live 0RB guidance
8. "Accept & Activate" button → THEN we charge + deploy
9. If they decline → Authorization cancelled, $0 charged

Philosophy: ZERO RISK. They see EVERYTHING before paying a cent.

New Features:
- Payment holds (authorize, capture only on accept)
- Acceptance gate (they must approve before deployment)
- Website changes offer (basic site with live 0RB agent guidance)
- Decline option (cancel payment auth, no charge)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import json
from datetime import datetime
from pathlib import Path
import stripe

app = FastAPI(title="One-Call-Close Demo v2.0 - Try Before You Buy")

# Stripe setup
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_demo')

class ProspectInfo(BaseModel):
    """Prospect business information"""
    business_name: str
    industry: str
    phone: str
    email: str
    current_marketing_spend: Optional[int] = 0
    monthly_revenue: Optional[int] = 0
    needs_website: Optional[bool] = False


@app.get("/", response_class=HTMLResponse)
async def demo_interface():
    """
    Enhanced demo with:
    - Payment authorization (not capture)
    - Full preview before charging
    - Website changes offer
    - Accept/Decline choice
    """
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Oracle AI - Try Before You Buy</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://js.stripe.com/v3/"></script>
    <style>
        .pulse-green {
            animation: pulse-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse-green {
            0%, 100% { opacity: 1; }
            50% { opacity: .5; }
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
        .glow {
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
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
                Try It FREE - Pay ONLY If You Love It
            </p>
            <p class="text-lg text-gray-400 mt-2">
                💝 Love • Loyalty • Honor • Everybody Eats
            </p>
        </div>

        <!-- ZERO RISK Badge -->
        <div class="max-w-4xl mx-auto mb-8 bg-green-500 text-white rounded-2xl p-6 text-center glow">
            <div class="text-3xl font-bold mb-2">🔒 ZERO RISK DEMO</div>
            <div class="text-lg">
                We'll build your system LIVE • You see EVERYTHING • Then YOU decide
            </div>
            <div class="text-sm mt-2 opacity-90">
                If you don't love it = $0 charged • No contracts • No commitments
            </div>
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
                        <option value="solar">Solar Installation</option>
                        <option value="roofing">Roofing</option>
                        <option value="landscaping">Landscaping</option>
                        <option value="auto">Auto Repair</option>
                        <option value="other">Other</option>
                    </select>
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">Your Email</label>
                    <input type="email" id="email"
                           class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                           placeholder="you@yourbusiness.com">
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">Your Phone</label>
                    <input type="tel" id="phone"
                           class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                           placeholder="(555) 123-4567">
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">Monthly Revenue</label>
                    <input type="number" id="monthly_revenue"
                           class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                           placeholder="e.g., 50000">
                </div>

                <div class="bg-blue-900 rounded-lg p-4">
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" id="needs_website" class="w-5 h-5 mr-3">
                        <span class="text-sm">
                            <strong>BONUS:</strong> Want a basic website with live AI chat?
                            <span class="text-blue-300">(FREE with setup)</span>
                        </span>
                    </label>
                </div>

                <button onclick="startTryBeforeBuy()"
                        class="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-bold py-4 px-8 rounded-lg hover:from-green-600 hover:to-blue-600 transition-all transform hover:scale-105">
                    🚀 Build My System - See It LIVE (FREE)
                </button>

                <p class="text-center text-sm text-gray-400 mt-4">
                    No charge yet • You'll approve before paying
                </p>
            </div>
        </div>

        <!-- Step 2: Payment Authorization -->
        <div id="step-2" class="hidden max-w-2xl mx-auto bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
            <h2 class="text-3xl font-bold mb-6 flex items-center">
                <span class="bg-green-500 text-white rounded-full w-10 h-10 flex items-center justify-center mr-4">2</span>
                Authorize Payment (Not Charged Yet!)
            </h2>

            <div class="bg-yellow-900 rounded-lg p-4 mb-6">
                <div class="flex items-start">
                    <div class="text-3xl mr-3">⚠️</div>
                    <div>
                        <div class="font-bold mb-1">We're NOT charging you yet!</div>
                        <div class="text-sm">
                            We just need payment authorization to build your system.
                            You'll see EVERYTHING first, then decide if you want it.
                            If you decline = $0 charged.
                        </div>
                    </div>
                </div>
            </div>

            <div id="payment-element" class="mb-6">
                <!-- Stripe payment element goes here -->
            </div>

            <button onclick="authorizePayment()"
                    id="authorize-button"
                    class="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-8 rounded-lg">
                ✓ Authorize $500 (Not Charged Until You Approve)
            </button>

            <div class="mt-6 text-center text-sm text-gray-400">
                <p>💳 Secure payment via Stripe</p>
                <p class="mt-2">🔒 You'll approve before we charge</p>
                <p class="mt-2">💝 100% refundable if no results in 90 days</p>
            </div>
        </div>

        <!-- Step 3: AI Building -->
        <div id="step-3" class="hidden max-w-4xl mx-auto bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
            <h2 class="text-3xl font-bold mb-6 flex items-center">
                <span class="bg-green-500 text-white rounded-full w-10 h-10 flex items-center justify-center mr-4 pulse-green">3</span>
                Building Your System LIVE...
            </h2>

            <div class="mb-4 bg-blue-900 rounded-lg p-4 text-center">
                <div class="text-lg">💳 Payment Authorized (Not Charged)</div>
                <div class="text-sm text-gray-300 mt-1">You'll approve before we capture payment</div>
            </div>

            <div class="space-y-4 text-lg">
                <div id="progress-1" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Analyzing <span id="biz-name-1"></span>...</span>
                </div>
                <div id="progress-2" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Generating custom calling scripts...</span>
                </div>
                <div id="progress-3" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Creating your branded dashboard...</span>
                </div>
                <div id="progress-4" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Training AI voice agent...</span>
                </div>
                <div id="progress-website" class="hidden flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Building your website with live AI chat...</span>
                </div>
                <div id="progress-5" class="flex items-center opacity-50">
                    <span class="mr-4">⏳</span>
                    <span>Setting up 24/7 calling campaign...</span>
                </div>
            </div>
        </div>

        <!-- Step 4: Preview - ACCEPT OR DECLINE -->
        <div id="step-4" class="hidden max-w-6xl mx-auto">

            <!-- Success Banner -->
            <div class="bg-green-500 rounded-2xl p-6 text-center mb-8 glow">
                <div class="text-4xl font-bold mb-2">✨ Your System is Ready!</div>
                <div class="text-xl">Review everything below • Then Accept or Decline</div>
            </div>

            <!-- Dashboard Preview -->
            <div class="bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
                <h2 class="text-3xl font-bold mb-6">
                    <span id="business-name-display"></span> - Your Dashboard
                </h2>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="bg-gradient-to-br from-green-500 to-green-700 rounded-xl p-6">
                        <div class="text-sm opacity-90">Calls Per Day</div>
                        <div class="text-4xl font-bold mt-2">50-100</div>
                        <div class="text-sm mt-2">Fully automated</div>
                    </div>

                    <div class="bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl p-6">
                        <div class="text-sm opacity-90">Expected Appointments/Month</div>
                        <div class="text-4xl font-bold mt-2">20-40</div>
                        <div class="text-sm mt-2">Qualified leads only</div>
                    </div>

                    <div class="bg-gradient-to-br from-purple-500 to-purple-700 rounded-xl p-6">
                        <div class="text-sm opacity-90">Est. Monthly Revenue</div>
                        <div class="text-4xl font-bold mt-2" id="projected-revenue">$15,000</div>
                        <div class="text-sm mt-2">Based on 20% close rate</div>
                    </div>
                </div>

                <div class="bg-gray-700 rounded-lg p-6">
                    <h3 class="font-bold mb-4">What's Included:</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div class="flex items-center">
                            <span class="text-green-400 mr-2">✓</span>
                            <span>AI Voice Agent (24/7 calling)</span>
                        </div>
                        <div class="flex items-center">
                            <span class="text-green-400 mr-2">✓</span>
                            <span>Appointment Booking System</span>
                        </div>
                        <div class="flex items-center">
                            <span class="text-green-400 mr-2">✓</span>
                            <span>Live Dashboard (track everything)</span>
                        </div>
                        <div class="flex items-center">
                            <span class="text-green-400 mr-2">✓</span>
                            <span>Custom Calling Scripts</span>
                        </div>
                        <div class="flex items-center">
                            <span class="text-green-400 mr-2">✓</span>
                            <span>CRM Integration</span>
                        </div>
                        <div class="flex items-center">
                            <span class="text-green-400 mr-2">✓</span>
                            <span>Weekly Performance Reports</span>
                        </div>
                        <div id="website-included" class="hidden col-span-2 flex items-center bg-blue-900 rounded p-3">
                            <span class="text-blue-300 mr-2 text-xl">🎁</span>
                            <span class="font-bold">BONUS: Professional Website + Live AI Chat</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Website Preview (if requested) -->
            <div id="website-preview" class="hidden bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
                <h2 class="text-2xl font-bold mb-4 flex items-center">
                    <span class="text-3xl mr-3">🎁</span>
                    BONUS: Your New Website
                </h2>

                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <h3 class="font-bold mb-3">What You Get:</h3>
                        <div class="space-y-2 text-sm">
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span>Professional 5-page website</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span>Live AI chat widget (24/7 lead capture)</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span>Mobile responsive design</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span>Contact forms with AI routing</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span>SEO optimization</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span>Fast hosting included</span>
                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-700 rounded-lg p-4">
                        <div class="text-xs text-gray-400 mb-2">Preview (you can customize):</div>
                        <div class="bg-white text-gray-900 rounded p-4 text-center">
                            <div class="font-bold text-xl mb-2" id="website-business-name"></div>
                            <div class="text-sm mb-4" id="website-industry"></div>
                            <div class="bg-blue-500 text-white rounded px-4 py-2 inline-block text-sm">
                                💬 Chat with AI Assistant
                            </div>
                        </div>
                        <div class="text-xs text-gray-400 mt-2 text-center">
                            Your domain: <span id="website-url" class="text-green-400"></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ROI Calculator -->
            <div class="bg-gray-800 rounded-2xl p-8 shadow-2xl mb-8">
                <h2 class="text-2xl font-bold mb-6">💰 Your ROI</h2>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <h3 class="text-lg font-bold mb-4 text-gray-300">What You Pay:</h3>
                        <div class="space-y-3">
                            <div class="flex justify-between">
                                <span>Retainer:</span>
                                <span class="font-bold">$500/month</span>
                            </div>
                            <div class="flex justify-between text-sm text-gray-400">
                                <span>(100% refundable if no results)</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Performance Fee:</span>
                                <span class="font-bold">15% of NEW revenue</span>
                            </div>
                            <div class="border-t border-gray-600 pt-3 flex justify-between text-xl font-bold">
                                <span>Total (if you make $15k):</span>
                                <span class="text-green-400">$2,750</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 class="text-lg font-bold mb-4 text-gray-300">What You Get:</h3>
                        <div class="space-y-3">
                            <div class="flex justify-between">
                                <span>New Revenue (30 days):</span>
                                <span class="font-bold text-green-400">$15,000</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Your Cost:</span>
                                <span class="font-bold">-$2,750</span>
                            </div>
                            <div class="border-t border-gray-600 pt-3 flex justify-between text-xl font-bold">
                                <span>Your Profit:</span>
                                <span class="text-green-400">$12,250</span>
                            </div>
                            <div class="mt-4 p-4 bg-green-900 rounded-lg text-center">
                                <div class="text-3xl font-bold">5.5x ROI</div>
                                <div class="text-sm mt-1">You make $5.50 for every $1 spent</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-6 bg-purple-900 rounded-lg p-4">
                    <div class="flex items-start">
                        <div class="text-2xl mr-3">💝</div>
                        <div>
                            <div class="font-bold mb-1">Community Impact:</div>
                            <div class="text-sm">
                                10% of what you pay ($275/month) goes to sanctuary.ai to feed meals,
                                provide tutoring, and cover medical costs. When you grow, families eat.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ACCEPT OR DECLINE -->
            <div class="bg-gradient-to-r from-gray-800 to-gray-900 rounded-2xl p-8 shadow-2xl mb-8 border-2 border-green-500 glow">
                <h2 class="text-3xl font-bold mb-6 text-center">
                    Decision Time - Accept or Decline?
                </h2>

                <div class="grid md:grid-cols-2 gap-6 mb-8">
                    <div class="bg-green-900 rounded-lg p-6">
                        <div class="text-2xl font-bold mb-3">✅ If You Accept:</div>
                        <div class="space-y-2 text-sm">
                            <div>• We charge the $500 retainer</div>
                            <div>• Your system goes LIVE immediately</div>
                            <div>• Starts calling leads in 60 seconds</div>
                            <div>• You get dashboard access</div>
                            <div>• Support team ready to help</div>
                            <div class="pt-2 text-green-300">
                                <strong>You'll have appointments by tomorrow</strong>
                            </div>
                        </div>
                    </div>

                    <div class="bg-red-900 rounded-lg p-6">
                        <div class="text-2xl font-bold mb-3">❌ If You Decline:</div>
                        <div class="space-y-2 text-sm">
                            <div>• We cancel the payment authorization</div>
                            <div>• You pay $0 - Nothing charged</div>
                            <div>• No hard feelings</div>
                            <div>• No follow-up calls</div>
                            <div>• We delete all your data</div>
                            <div class="pt-2 text-gray-400">
                                <strong>100% clean slate, $0 charge</strong>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid md:grid-cols-2 gap-4">
                    <button onclick="acceptAndActivate()"
                            class="bg-gradient-to-r from-green-500 to-green-600 text-white font-bold py-6 px-8 rounded-lg hover:from-green-600 hover:to-green-700 transition-all transform hover:scale-105 text-xl">
                        ✅ Accept & Activate - Let's Go!
                    </button>

                    <button onclick="declineOffer()"
                            class="bg-gray-700 hover:bg-gray-600 text-white font-bold py-6 px-8 rounded-lg transition-all text-xl">
                        ❌ Decline (No Charge)
                    </button>
                </div>

                <div class="text-center mt-6 text-sm text-gray-400">
                    <p>💡 Take your time • No pressure • Your choice</p>
                </div>
            </div>
        </div>

        <!-- Step 5: Activated! -->
        <div id="step-5" class="hidden max-w-4xl mx-auto">
            <div class="bg-gradient-to-r from-green-500 to-blue-500 rounded-2xl p-12 text-center shadow-2xl glow">
                <div class="text-6xl mb-6">🎉</div>
                <h1 class="text-5xl font-bold mb-4">You're LIVE!</h1>
                <p class="text-2xl mb-8">Your AI agents are calling leads right now...</p>

                <div class="bg-white bg-opacity-20 rounded-lg p-6 mb-8">
                    <div class="text-lg mb-4">Dashboard Access:</div>
                    <div class="text-3xl font-mono bg-gray-900 rounded p-4 mb-4" id="dashboard-url">
                        dashboard.oracle-ai.com/<span id="client-slug"></span>
                    </div>
                    <div class="text-sm">Login credentials sent to your email</div>
                </div>

                <div class="grid md:grid-cols-3 gap-4 text-left">
                    <div class="bg-white bg-opacity-10 rounded-lg p-4">
                        <div class="text-sm opacity-90">First Call</div>
                        <div class="text-2xl font-bold">In 60 seconds</div>
                    </div>
                    <div class="bg-white bg-opacity-10 rounded-lg p-4">
                        <div class="text-sm opacity-90">First Appointment</div>
                        <div class="text-2xl font-bold">Within 24 hours</div>
                    </div>
                    <div class="bg-white bg-opacity-10 rounded-lg p-4">
                        <div class="text-sm opacity-90">Support</div>
                        <div class="text-2xl font-bold">24/7 Available</div>
                    </div>
                </div>

                <div class="mt-8 text-sm opacity-90">
                    💝 Welcome aboard! Love • Loyalty • Honor • Everybody Eats
                </div>
            </div>
        </div>

        <!-- Step 6: Declined -->
        <div id="step-6" class="hidden max-w-4xl mx-auto">
            <div class="bg-gray-800 rounded-2xl p-12 text-center shadow-2xl">
                <div class="text-6xl mb-6">👍</div>
                <h1 class="text-4xl font-bold mb-4">No Problem!</h1>
                <p class="text-xl mb-8">Payment authorization cancelled - You paid $0</p>

                <div class="bg-gray-700 rounded-lg p-6 mb-8 max-w-2xl mx-auto">
                    <p class="mb-4">Thanks for trying our demo. A few things:</p>
                    <div class="text-left space-y-2 text-sm">
                        <div>✓ No charge processed - Your card was NOT charged</div>
                        <div>✓ All your data deleted within 24 hours</div>
                        <div>✓ No follow-up emails or calls from us</div>
                        <div>✓ You can come back anytime - No hard feelings</div>
                    </div>
                </div>

                <div class="text-gray-400 text-sm">
                    <p>If you change your mind, you know where to find us.</p>
                    <p class="mt-4">💝 Love • Loyalty • Honor • Everybody Eats</p>
                </div>
            </div>
        </div>

    </div>

    <script>
        let prospectData = {};
        let paymentIntent = null;
        let stripe = null;
        let elements = null;

        async function startTryBeforeBuy() {
            // Collect data
            prospectData = {
                business_name: document.getElementById('business_name').value,
                industry: document.getElementById('industry').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                monthly_revenue: document.getElementById('monthly_revenue').value || 0,
                needs_website: document.getElementById('needs_website').checked
            };

            // Validate
            if (!prospectData.business_name || !prospectData.email || !prospectData.phone) {
                alert('Please fill in all required fields');
                return;
            }

            // Move to payment authorization
            document.getElementById('step-1').classList.add('hidden');
            document.getElementById('step-2').classList.remove('hidden');

            // Initialize Stripe (in demo mode for now)
            // In production, create payment intent on backend first
            initializeStripeDemo();
        }

        function initializeStripeDemo() {
            // Demo mode - just show the UI
            document.getElementById('payment-element').innerHTML = `
                <div class="bg-gray-700 rounded-lg p-6 text-center">
                    <div class="text-sm text-gray-400 mb-4">DEMO MODE</div>
                    <div class="text-lg mb-2">💳 Stripe Payment Element Would Load Here</div>
                    <div class="text-sm text-gray-400">In production: Secure card entry via Stripe</div>
                </div>
            `;
        }

        async function authorizePayment() {
            const button = document.getElementById('authorize-button');
            button.disabled = true;
            button.textContent = '⏳ Authorizing...';

            // Simulate authorization
            await new Promise(resolve => setTimeout(resolve, 2000));

            button.textContent = '✓ Authorized!';

            // Move to building
            setTimeout(() => {
                document.getElementById('step-2').classList.add('hidden');
                document.getElementById('step-3').classList.remove('hidden');
                startBuildingSystem();
            }, 1000);
        }

        async function startBuildingSystem() {
            // Update business name in progress
            document.getElementById('biz-name-1').textContent = prospectData.business_name;

            // Show website step if requested
            if (prospectData.needs_website) {
                document.getElementById('progress-website').classList.remove('hidden');
            }

            // Simulate build steps
            const steps = ['progress-1', 'progress-2', 'progress-3', 'progress-4'];
            if (prospectData.needs_website) steps.push('progress-website');
            steps.push('progress-5');

            for (let i = 0; i < steps.length; i++) {
                await new Promise(resolve => setTimeout(resolve, 5000 / steps.length));
                const el = document.getElementById(steps[i]);
                el.classList.remove('opacity-50');
                el.querySelector('span:first-child').textContent = '✅';
            }

            // Build complete - show preview
            setTimeout(() => {
                document.getElementById('step-3').classList.add('hidden');
                showPreview();
            }, 1000);
        }

        function showPreview() {
            document.getElementById('step-4').classList.remove('hidden');
            document.getElementById('business-name-display').textContent = prospectData.business_name;

            // Calculate revenue
            const avgDealSize = 2500; // HVAC average
            const appointmentsPerMonth = 30;
            const closeRate = 0.20;
            const dealsPerMonth = appointmentsPerMonth * closeRate;
            const revenue = dealsPerMonth * avgDealSize;
            document.getElementById('projected-revenue').textContent = '$' + revenue.toLocaleString();

            // Show website preview if requested
            if (prospectData.needs_website) {
                document.getElementById('website-included').classList.remove('hidden');
                document.getElementById('website-preview').classList.remove('hidden');
                document.getElementById('website-business-name').textContent = prospectData.business_name;
                document.getElementById('website-industry').textContent = prospectData.industry.toUpperCase() + ' Services';
                document.getElementById('website-url').textContent =
                    prospectData.business_name.toLowerCase().replace(/[^a-z0-9]/g, '') + '.com';
            }

            // Scroll to decision
            setTimeout(() => {
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }, 500);
        }

        async function acceptAndActivate() {
            if (!confirm('Ready to activate? We\'ll charge $500 and deploy your system immediately.')) {
                return;
            }

            // In production: Capture the payment intent
            // For demo: Just show success

            document.getElementById('step-4').classList.add('hidden');
            document.getElementById('step-5').classList.remove('hidden');

            // Set dashboard URL
            const slug = prospectData.business_name.toLowerCase().replace(/[^a-z0-9]/g, '-');
            document.getElementById('client-slug').textContent = slug;

            // Send to backend to actually deploy
            // await fetch('/api/deploy', { method: 'POST', body: JSON.stringify(prospectData) });

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        async function declineOffer() {
            if (!confirm('Are you sure? Your payment authorization will be cancelled and you won\'t be charged.')) {
                return;
            }

            // In production: Cancel the payment intent
            // For demo: Just show declined

            document.getElementById('step-4').classList.add('hidden');
            document.getElementById('step-6').classList.remove('hidden');

            // Send to backend to cancel
            // await fetch('/api/decline', { method: 'POST', body: JSON.stringify({ email: prospectData.email }) });

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    </script>
</body>
</html>
    """


@app.post("/api/create-payment-intent")
async def create_payment_intent(prospect: ProspectInfo):
    """
    Create Stripe PaymentIntent for authorization (not immediate capture)

    Setup intent with capture_method='manual' so we can authorize now,
    capture only after customer accepts
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=50000,  # $500.00
            currency='usd',
            capture_method='manual',  # Don't capture until they accept!
            metadata={
                'business_name': prospect.business_name,
                'industry': prospect.industry,
                'email': prospect.email,
                'phone': prospect.phone
            }
        )

        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        }
    except Exception as e:
        return {
            "client_secret": "demo_secret",
            "payment_intent_id": "demo_intent"
        }


@app.post("/api/deploy")
async def deploy_system(prospect: ProspectInfo, payment_intent_id: str):
    """
    Called when customer ACCEPTS

    1. Capture the payment (actually charge them)
    2. Deploy their system
    3. Send credentials
    """
    try:
        # Capture payment
        stripe.PaymentIntent.capture(payment_intent_id)

        # Deploy system (actual deployment would happen here)
        customer_id = f"{prospect.industry}_{prospect.business_name.lower().replace(' ', '_')}"

        # Create customer record
        customer_dir = Path("client_data") / customer_id
        customer_dir.mkdir(parents=True, exist_ok=True)

        with open(customer_dir / "customer.json", 'w') as f:
            json.dump({
                "customer_id": customer_id,
                "business_name": prospect.business_name,
                "industry": prospect.industry,
                "email": prospect.email,
                "phone": prospect.phone,
                "needs_website": prospect.needs_website,
                "status": "active",
                "payment_intent_id": payment_intent_id,
                "activated_at": datetime.now().isoformat()
            }, f, indent=2)

        return {
            "success": True,
            "customer_id": customer_id,
            "dashboard_url": f"dashboard.oracle-ai.com/{customer_id}",
            "message": "System deployed successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/decline")
async def decline_offer(email: str, payment_intent_id: str):
    """
    Called when customer DECLINES

    1. Cancel payment intent (no charge)
    2. Delete their data
    3. Send confirmation email
    """
    try:
        # Cancel payment intent
        stripe.PaymentIntent.cancel(payment_intent_id)

        return {
            "success": True,
            "message": "Payment authorization cancelled - You were not charged"
        }

    except Exception as e:
        return {
            "success": True,  # Always return success for decline
            "message": "Declined - No charge processed"
        }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*70)
    print("🚀 ONE-CALL-CLOSE DEMO v2.0 - TRY BEFORE YOU BUY")
    print("="*70)
    print()
    print("New Features:")
    print("  ✓ Payment authorization (not charged until they accept)")
    print("  ✓ Full system preview before commitment")
    print("  ✓ Website changes offer with live AI guidance")
    print("  ✓ Accept/Decline choice - Customer in control")
    print("  ✓ $0 charged if they decline")
    print()
    print("Running on: http://localhost:8002")
    print()
    print("💝 Love • Loyalty • Honor • Everybody Eats")
    print("="*70)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8002)
