# DEPLOY THE 0RB EMPIRE - Windows PowerShell Version
#
# This script deploys:
# 1. One-Call-Close Demo System (port 8002)
# 2. Agent Swarm (4 production agents on port 8003)
# 3. Client Dashboard & Billing (port 8004)
# 4. Swarm Coordinator (port 8005) - Deploy 100s of agents simultaneously
# 5. Instant Builder (port 8000)
# 6. HVAC Voice Agent (port 8001)
#
# Philosophy: Love • Loyalty • Honor • Everybody Eats

Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "🔥 DEPLOYING 0RB EMPIRE - COMPLETE REVENUE ENGINE" -ForegroundColor Yellow
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Philosophy: Love • Loyalty • Honor • Everybody Eats" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "Checking for Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -q fastapi uvicorn pydantic twilio httpx stripe anthropic

# Check environment variables
Write-Host ""
Write-Host "🔍 Checking environment variables..." -ForegroundColor Yellow

$missingVars = @()

if (-not $env:ANTHROPIC_API_KEY) {
    $missingVars += "ANTHROPIC_API_KEY"
}

if (-not $env:TWILIO_ACCOUNT_SID -or -not $env:TWILIO_AUTH_TOKEN -or -not $env:TWILIO_PHONE_NUMBER) {
    Write-Host "⚠️  Twilio not configured - voice calling will be in demo mode" -ForegroundColor Yellow
    Write-Host "   Set: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER" -ForegroundColor Gray
}

if (-not $env:STRIPE_SECRET_KEY) {
    Write-Host "⚠️  Stripe not configured - billing will be in demo mode" -ForegroundColor Yellow
    Write-Host "   Set: STRIPE_SECRET_KEY" -ForegroundColor Gray
}

if ($missingVars.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ Missing required environment variables:" -ForegroundColor Red
    foreach ($var in $missingVars) {
        Write-Host "   $var" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Set them in PowerShell:" -ForegroundColor Yellow
    foreach ($var in $missingVars) {
        Write-Host "   `$env:$var = 'your_key_here'" -ForegroundColor Gray
    }
    exit 1
}

Write-Host "✅ Core API keys configured" -ForegroundColor Green

# Create necessary directories
Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$dirs = @("logs", "client_data", "grimoire", "digital_twin", "amplification_patterns", "hvac_calls")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
Write-Host "✅ Directories created" -ForegroundColor Green

# Kill existing services
Write-Host ""
Write-Host "🛑 Stopping any existing services..." -ForegroundColor Yellow
if (Test-Path ".pids") {
    Get-Content ".pids" | ForEach-Object {
        try {
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        } catch {}
    }
    Remove-Item ".pids"
}

# Start services
Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Yellow

# 1. One-Call-Close Demo System
Write-Host "   Starting One-Call-Close Demo (port 8002)..." -ForegroundColor Cyan
$process = Start-Process python -ArgumentList "one_call_close_demo.py" -WindowStyle Hidden -PassThru -RedirectStandardOutput "logs\one_call_close.log" -RedirectStandardError "logs\one_call_close_error.log"
$process.Id | Out-File -Append ".pids"
Start-Sleep -Seconds 2

# 2. Agent Swarm
Write-Host "   Starting Agent Swarm (port 8003)..." -ForegroundColor Cyan
$process = Start-Process python -ArgumentList "agent_swarm.py" -WindowStyle Hidden -PassThru -RedirectStandardOutput "logs\agent_swarm.log" -RedirectStandardError "logs\agent_swarm_error.log"
$process.Id | Out-File -Append ".pids"
Start-Sleep -Seconds 2

# 3. Client Dashboard & Billing
Write-Host "   Starting Dashboard & Billing (port 8004)..." -ForegroundColor Cyan
$process = Start-Process python -ArgumentList "client_dashboard_and_billing.py" -WindowStyle Hidden -PassThru -RedirectStandardOutput "logs\dashboard.log" -RedirectStandardError "logs\dashboard_error.log"
$process.Id | Out-File -Append ".pids"
Start-Sleep -Seconds 2

# 4. Swarm Coordinator
Write-Host "   Starting Swarm Coordinator (port 8005)..." -ForegroundColor Cyan
$process = Start-Process python -ArgumentList "swarm_coordinator.py" -WindowStyle Hidden -PassThru -RedirectStandardOutput "logs\swarm_coordinator.log" -RedirectStandardError "logs\swarm_coordinator_error.log"
$process.Id | Out-File -Append ".pids"
Start-Sleep -Seconds 2

# 5. Instant Builder (if exists)
if (Test-Path "instant_builder.py") {
    Write-Host "   Starting Instant Builder (port 8000)..." -ForegroundColor Cyan
    $process = Start-Process python -ArgumentList "instant_builder.py" -WindowStyle Hidden -PassThru -RedirectStandardOutput "logs\instant_builder.log" -RedirectStandardError "logs\instant_builder_error.log"
    $process.Id | Out-File -Append ".pids"
    Start-Sleep -Seconds 2
}

# 6. HVAC Voice Agent (if Twilio configured)
if ((Test-Path "hvac_agent_now.py") -and $env:TWILIO_ACCOUNT_SID) {
    Write-Host "   Starting HVAC Voice Agent (port 8001)..." -ForegroundColor Cyan
    $process = Start-Process python -ArgumentList "hvac_agent_now.py --serve" -WindowStyle Hidden -PassThru -RedirectStandardOutput "logs\hvac_agent.log" -RedirectStandardError "logs\hvac_agent_error.log"
    $process.Id | Out-File -Append ".pids"
    Start-Sleep -Seconds 2
}

Write-Host "✅ All services started" -ForegroundColor Green

# Create stop script
Write-Host ""
Write-Host "📝 Creating stop script..." -ForegroundColor Yellow
@"
# Stop all 0RB Empire services
Write-Host "🛑 Stopping 0RB Empire..." -ForegroundColor Yellow
if (Test-Path ".pids") {
    Get-Content ".pids" | ForEach-Object {
        Write-Host "   Killing process `$_" -ForegroundColor Gray
        try {
            Stop-Process -Id `$_ -Force -ErrorAction SilentlyContinue
        } catch {}
    }
    Remove-Item ".pids"
    Write-Host "✅ All services stopped" -ForegroundColor Green
} else {
    Write-Host "⚠️  No PID file found" -ForegroundColor Yellow
}
"@ | Out-File -FilePath "stop_empire.ps1"

Write-Host "✅ Stop script created" -ForegroundColor Green

# Display status
Write-Host ""
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 SERVICES RUNNING:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   📍 One-Call-Close Demo:" -ForegroundColor Cyan
Write-Host "      http://localhost:8002" -ForegroundColor White
Write-Host "      → Screen-share this during sales calls" -ForegroundColor Gray
Write-Host ""
Write-Host "   📍 Agent Swarm:" -ForegroundColor Cyan
Write-Host "      http://localhost:8003" -ForegroundColor White
Write-Host "      → 4 production agents" -ForegroundColor Gray
Write-Host ""
Write-Host "   📍 Client Dashboard:" -ForegroundColor Cyan
Write-Host "      http://localhost:8004/dashboard/[client_id]" -ForegroundColor White
Write-Host "      → Real-time ROI tracking" -ForegroundColor Gray
Write-Host ""
Write-Host "   📍 Swarm Coordinator:" -ForegroundColor Cyan
Write-Host "      http://localhost:8005" -ForegroundColor White
Write-Host "      → Deploy 100s of agents" -ForegroundColor Gray
Write-Host ""
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   1. Open demo: http://localhost:8002" -ForegroundColor White
Write-Host "   2. Call prospects (see LAUNCH_CHECKLIST.md)" -ForegroundColor White
Write-Host "   3. Close deals, make money, feed community" -ForegroundColor White
Write-Host ""
Write-Host "🛑 STOP ALL SERVICES:" -ForegroundColor Yellow
Write-Host "   .\stop_empire.ps1" -ForegroundColor White
Write-Host ""
Write-Host "💝 Love • Loyalty • Honor • Everybody Eats" -ForegroundColor Green
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""
