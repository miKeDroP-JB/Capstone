#!/bin/bash
# DEPLOY THE 0RB EMPIRE - Complete Revenue Engine Deployment
#
# This script deploys:
# 1. One-Call-Close Demo System (port 8002)
# 2. Agent Swarm (4 production agents on port 8003)
# 3. Client Dashboard & Billing (port 8004)
# 4. Instant Builder (port 8000)
# 5. HVAC Voice Agent (port 8001)
#
# Philosophy: Love • Loyalty • Honor • Everybody Eats

set -e

echo "======================================================================="
echo "🔥 DEPLOYING 0RB EMPIRE - COMPLETE REVENUE ENGINE"
echo "======================================================================="
echo ""
echo "Philosophy: Love • Loyalty • Honor • Everybody Eats"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python 3 found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -q fastapi uvicorn pydantic twilio httpx stripe

# Check environment variables
echo ""
echo "🔍 Checking environment variables..."
MISSING_VARS=()

# Core API keys (at least Claude needed)
if [ -z "$ANTHROPIC_API_KEY" ]; then
    MISSING_VARS+=("ANTHROPIC_API_KEY")
fi

# Twilio (optional but recommended)
if [ -z "$TWILIO_ACCOUNT_SID" ] || [ -z "$TWILIO_AUTH_TOKEN" ] || [ -z "$TWILIO_PHONE_NUMBER" ]; then
    echo "⚠️  Twilio not configured - voice calling will be in demo mode"
    echo "   Set: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER"
fi

# Stripe (optional but needed for billing)
if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo "⚠️  Stripe not configured - billing will be in demo mode"
    echo "   Set: STRIPE_SECRET_KEY"
fi

# Gemini (optional, for tournament)
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Gemini API not configured - will use Claude only"
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo ""
    echo "❌ Missing required environment variables:"
    printf '   %s\n' "${MISSING_VARS[@]}"
    echo ""
    echo "Export them in your shell:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   export $var=your_key_here"
    done
    exit 1
fi

echo "✅ Core API keys configured"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs client_data grimoire digital_twin amplification_patterns hvac_calls

echo "✅ Directories created"

# Kill existing services
echo ""
echo "🛑 Stopping any existing services..."
if [ -f .pids ]; then
    while read pid; do
        kill $pid 2>/dev/null || true
    done < .pids
    rm .pids
fi

# Start services
echo ""
echo "🚀 Starting services..."

# 1. One-Call-Close Demo System
echo "   Starting One-Call-Close Demo (port 8002)..."
nohup python3 one_call_close_demo.py > logs/one_call_close.log 2>&1 &
echo $! >> .pids
sleep 2

# 2. Agent Swarm
echo "   Starting Agent Swarm (port 8003)..."
nohup python3 agent_swarm.py > logs/agent_swarm.log 2>&1 &
echo $! >> .pids
sleep 2

# 3. Client Dashboard & Billing
echo "   Starting Dashboard & Billing (port 8004)..."
nohup python3 client_dashboard_and_billing.py > logs/dashboard.log 2>&1 &
echo $! >> .pids
sleep 2

# 4. Swarm Coordinator
echo "   Starting Swarm Coordinator (port 8005)..."
nohup python3 swarm_coordinator.py > logs/swarm_coordinator.log 2>&1 &
echo $! >> .pids
sleep 2

# 5. Instant Builder (if exists)
if [ -f instant_builder.py ]; then
    echo "   Starting Instant Builder (port 8000)..."
    nohup python3 instant_builder.py > logs/instant_builder.log 2>&1 &
    echo $! >> .pids
    sleep 2
fi

# 6. HVAC Voice Agent (if Twilio configured)
if [ -f hvac_agent_now.py ] && [ -n "$TWILIO_ACCOUNT_SID" ]; then
    echo "   Starting HVAC Voice Agent (port 8001)..."
    nohup python3 hvac_agent_now.py --serve > logs/hvac_agent.log 2>&1 &
    echo $! >> .pids
    sleep 2
fi

echo "✅ All services started"

# Create stop script
echo ""
echo "📝 Creating stop script..."
cat > stop_empire.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping 0RB Empire..."
if [ -f .pids ]; then
    while read pid; do
        echo "   Killing process $pid"
        kill $pid 2>/dev/null || true
    done < .pids
    rm .pids
    echo "✅ All services stopped"
else
    echo "⚠️  No PID file found"
fi
EOF
chmod +x stop_empire.sh

echo "✅ Stop script created"

# Display status
echo ""
echo "======================================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================================================================="
echo ""
echo "🌐 SERVICES RUNNING:"
echo ""
echo "   📍 One-Call-Close Demo:"
echo "      http://localhost:8002"
echo "      → Screen-share this during sales calls"
echo "      → Live demo that closes deals instantly"
echo ""
echo "   📍 Agent Swarm:"
echo "      http://localhost:8003"
echo "      http://localhost:8003/api/pricing"
echo "      → 4 production agents ($299-$599/month recurring)"
echo ""
echo "   📍 Client Dashboard:"
echo "      http://localhost:8004/dashboard/[client_id]"
echo "      → Real-time ROI, transparent billing"
echo ""
echo "   📍 Swarm Coordinator:"
echo "      http://localhost:8005"
echo "      http://localhost:8005/api/swarm/templates/hvac-appointments?target=100"
echo "      → Deploy 100s of agents simultaneously"
echo ""
if [ -f instant_builder.py ]; then
echo "   📍 Instant Builder:"
echo "      http://localhost:8000"
echo "      → Master orchestrator (SERVE/PROTECT/AMPLIFY)"
echo ""
fi
if [ -f hvac_agent_now.py ] && [ -n "$TWILIO_ACCOUNT_SID" ]; then
echo "   📍 HVAC Voice Agent:"
echo "      http://localhost:8001"
echo "      → Live voice calling system"
echo ""
fi
echo "======================================================================="
echo ""
echo "📊 REVENUE MODEL:"
echo ""
echo "   One-Call-Close:"
echo "   • $500 refundable retainer"
echo "   • 15% of NEW revenue generated"
echo "   • 90-day money-back guarantee"
echo ""
echo "   Agent Subscriptions:"
echo "   • Knowledge Base: $299/month"
echo "   • Voice Sales: Retainer + 10-15%"
echo "   • Social Marketing: $299/month"
echo "   • Chatbot: $199/month"
echo ""
echo "   Bundles:"
echo "   • Starter: $399/month (save $99)"
echo "   • Growth: Retainer + 10% + $399/month"
echo "   • Empire: Retainer + 10% + $599/month (save $299)"
echo ""
echo "   Community:"
echo "   • 10% of ALL revenue → sanctuary.ai"
echo ""
echo "======================================================================="
echo ""
echo "🎯 NEXT STEPS TO MAKE MONEY:"
echo ""
echo "   1. CALL PROSPECTS (today):"
echo "      → Find 10 HVAC contractors, call them"
echo "      → \"I can get you 20-40 appointments/month for \$500 refundable\""
echo "      → Screen-share http://localhost:8002"
echo "      → Build their system LIVE while talking"
echo "      → Close 2-4 of them = \$1,000-2,000 THIS WEEK"
echo ""
echo "   2. DELIVER RESULTS (this week):"
echo "      → Deploy their voice agent"
echo "      → Make 100 calls for them"
echo "      → Book 20-30 appointments"
echo "      → They close 4-6 deals"
echo "      → They make \$10k-15k"
echo "      → You bill 15% = \$1,500-2,250 performance fee"
echo ""
echo "   3. SCALE (this month):"
echo "      → Get 10 clients = \$5,000 retainer + \$15k-22k performance"
echo "      → Total: \$20,000-27,000 in month 1"
echo "      → Reinvest in more agents, more clients"
echo "      → Month 2: 25 clients = \$50k-75k"
echo "      → Month 3: 50 clients = \$100k-150k"
echo ""
echo "   4. ENTER CONTESTS (while scaling):"
echo "      → Next Top AI Agent (March 2025) - \$500k prize pool"
echo "      → a16z Speedrun (May 2025) - Up to \$1M funding"
echo "      → With 50+ paying customers, you're unstoppable"
echo ""
echo "======================================================================="
echo ""
echo "📝 LOGS:"
echo "   tail -f logs/one_call_close.log"
echo "   tail -f logs/agent_swarm.log"
echo "   tail -f logs/dashboard.log"
echo ""
echo "🛑 STOP ALL SERVICES:"
echo "   ./stop_empire.sh"
echo ""
echo "💝 PHILOSOPHY:"
echo "   Love • Loyalty • Honor • Everybody Eats"
echo ""
echo "   You're not building a business to get rich."
echo "   You're building a system to help people."
echo "   The money comes BECAUSE you helped."
echo ""
echo "   Help 1 person → They tell 3 people"
echo "   Help 100 people → They tell 300 people"
echo "   Help 10,000 people → They tell 30,000 people"
echo ""
echo "   Exponential growth through genuine value."
echo ""
echo "🔥 NOW GO CLOSE YOUR FIRST CUSTOMER!"
echo "======================================================================="
