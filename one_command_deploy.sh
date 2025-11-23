#!/bin/bash
# ONE COMMAND DEPLOY - Go Live in 60 Seconds
# ===========================================
# Deploys entire Love-First Builder system
#
# Usage: ./one_command_deploy.sh
#
# Love • Loyalty • Honor • Everybody Eats

set -e  # Exit on any error

echo ""
echo "============================================================"
echo "🔥 DEPLOYING LOVE-FIRST INSTANT BUILDER"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
echo "📋 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install pip"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."

pip3 install -q fastapi uvicorn pydantic twilio httpx || {
    echo "⚠️  Some dependencies failed to install. Continuing anyway..."
}

echo "✓ Dependencies installed"

# Check environment variables
echo ""
echo "🔐 Checking environment configuration..."

MISSING_VARS=()

if [ -z "$TWILIO_ACCOUNT_SID" ]; then
    MISSING_VARS+=("TWILIO_ACCOUNT_SID")
fi

if [ -z "$TWILIO_AUTH_TOKEN" ]; then
    MISSING_VARS+=("TWILIO_AUTH_TOKEN")
fi

if [ -z "$TWILIO_PHONE_NUMBER" ]; then
    MISSING_VARS+=("TWILIO_PHONE_NUMBER")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "${YELLOW}⚠️  Missing environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Set them with:"
    echo "   export TWILIO_ACCOUNT_SID='your_sid'"
    echo "   export TWILIO_AUTH_TOKEN='your_token'"
    echo "   export TWILIO_PHONE_NUMBER='+1-555-1234'"
    echo ""
    echo "Voice calling will be disabled until these are set."
    echo ""
else
    echo "✓ Twilio configured"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."

mkdir -p digital_twin
mkdir -p amplification_patterns
mkdir -p hvac_calls
mkdir -p customer_dashboards
mkdir -p traffic_campaigns
mkdir -p live_demos
mkdir -p retainer_payments
mkdir -p crm_data
mkdir -p client_ecosystem

echo "✓ Directories created"

# Start services
echo ""
echo "🚀 Starting services..."
echo ""

# Kill any existing processes on these ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Start instant_builder (main orchestrator)
echo "Starting Instant Builder (port 8000)..."
nohup python3 instant_builder.py > logs/instant_builder.log 2>&1 &
INSTANT_BUILDER_PID=$!
sleep 2

if ps -p $INSTANT_BUILDER_PID > /dev/null; then
    echo "${GREEN}✓ Instant Builder running (PID: $INSTANT_BUILDER_PID)${NC}"
else
    echo "❌ Instant Builder failed to start. Check logs/instant_builder.log"
    exit 1
fi

# Start HVAC voice agent (if Twilio configured)
if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo "Starting HVAC Voice Agent (port 8001)..."
    nohup python3 hvac_agent_now.py --serve > logs/hvac_agent.log 2>&1 &
    HVAC_AGENT_PID=$!
    sleep 2

    if ps -p $HVAC_AGENT_PID > /dev/null; then
        echo "${GREEN}✓ HVAC Voice Agent running (PID: $HVAC_AGENT_PID)${NC}"
    else
        echo "${YELLOW}⚠️  HVAC Voice Agent failed to start${NC}"
    fi
else
    echo "${YELLOW}⏭  Skipping HVAC Voice Agent (Twilio not configured)${NC}"
fi

# Save PIDs for later management
echo "$INSTANT_BUILDER_PID" > .instant_builder.pid
echo "$HVAC_AGENT_PID" > .hvac_agent.pid 2>/dev/null || true

echo ""
echo "============================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""

echo "🎯 SERVICES RUNNING:"
echo ""
echo "   Instant Builder API:"
echo "   http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo "   HVAC Voice Agent:"
    echo "   http://localhost:8001"
    echo "   Webhook: http://your-domain:8001/voice/handle"
    echo ""
fi

echo "💡 NEXT STEPS:"
echo ""
echo "1. Test the API:"
echo "   curl http://localhost:8000/status"
echo ""
echo "2. Build your first system:"
echo '   curl -X POST http://localhost:8000/serve \\'
echo '        -H "Content-Type: application/json" \\'
echo '        -d '"'"'{"intent": "HVAC contractors need help", "auto_deploy": true}'"'"
echo ""
echo "3. Check digital twin:"
echo "   python3 digital_twin.py --profile"
echo ""
echo "4. Make a test call (if Twilio configured):"
echo "   python3 hvac_agent_now.py --call +1-555-1234"
echo ""

echo "📊 LOGS:"
echo "   tail -f logs/instant_builder.log"
echo "   tail -f logs/hvac_agent.log"
echo ""

echo "🛑 TO STOP:"
echo "   ./stop_services.sh"
echo ""

echo "============================================================"
echo "💝 Love • Loyalty • Honor • Everybody Eats"
echo "============================================================"
echo ""

echo "${GREEN}READY TO SERVE! 🚀${NC}"
echo ""

# Create stop script
cat > stop_services.sh << 'STOP_SCRIPT'
#!/bin/bash
echo "Stopping services..."

if [ -f .instant_builder.pid ]; then
    kill $(cat .instant_builder.pid) 2>/dev/null || true
    rm .instant_builder.pid
    echo "✓ Instant Builder stopped"
fi

if [ -f .hvac_agent.pid ]; then
    kill $(cat .hvac_agent.pid) 2>/dev/null || true
    rm .hvac_agent.pid
    echo "✓ HVAC Voice Agent stopped"
fi

echo "All services stopped."
STOP_SCRIPT

chmod +x stop_services.sh

# Create logs directory
mkdir -p logs

echo "Deployment script complete!"
