# Windows API Key Setup Script
# Copy this entire file and run in PowerShell (as Administrator)

Write-Host "🔑 Setting up API keys..." -ForegroundColor Yellow

# REPLACE THESE WITH YOUR ACTUAL FULL KEYS:
$ANTHROPIC_KEY = "sk-ant-api03-YOUR_FULL_KEY_HERE"
$OPENAI_KEY = "sk-197c86e0da664af4918079cd13c1cfeb"
$PERPLEXITY_KEY = "pplx-YOUR_FULL_KEY_HERE"
$GOOGLE_KEY = "AIza_YOUR_FULL_KEY_HERE"

# Set environment variables (permanent)
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', $ANTHROPIC_KEY, 'User')
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', $OPENAI_KEY, 'User')
[System.Environment]::SetEnvironmentVariable('PERPLEXITY_API_KEY', $PERPLEXITY_KEY, 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', $GOOGLE_KEY, 'User')

# Set for current session too
$env:ANTHROPIC_API_KEY = $ANTHROPIC_KEY
$env:OPENAI_API_KEY = $OPENAI_KEY
$env:PERPLEXITY_API_KEY = $PERPLEXITY_KEY
$env:GOOGLE_API_KEY = $GOOGLE_KEY

# Allow scripts to run
Write-Host "🔓 Enabling PowerShell scripts..." -ForegroundColor Yellow
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Verify
Write-Host "`n✅ API Keys Set Successfully!" -ForegroundColor Green
Write-Host "`nConfigured keys:" -ForegroundColor Cyan
Write-Host "  ✓ ANTHROPIC_API_KEY: $($ANTHROPIC_KEY.Substring(0,20))..." -ForegroundColor Gray
Write-Host "  ✓ OPENAI_API_KEY: $($OPENAI_KEY.Substring(0,20))..." -ForegroundColor Gray
Write-Host "  ✓ PERPLEXITY_API_KEY: $($PERPLEXITY_KEY.Substring(0,15))..." -ForegroundColor Gray
Write-Host "  ✓ GOOGLE_API_KEY: $($GOOGLE_KEY.Substring(0,15))..." -ForegroundColor Gray

Write-Host "`n🚀 Ready to deploy! Run:" -ForegroundColor Green
Write-Host "   .\deploy_empire.ps1" -ForegroundColor Yellow

Write-Host "`n💝 Love • Loyalty • Honor • Everybody Eats" -ForegroundColor Magenta
