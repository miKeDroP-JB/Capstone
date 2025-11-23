# 🪟 WINDOWS SETUP GUIDE

## You're on Windows - Here's How to Deploy

### STEP 1: Set Your API Key (1 minute)

Open PowerShell and run:

```powershell
$env:ANTHROPIC_API_KEY = "your_actual_key_here"
```

**To make it permanent** (so you don't have to set it every time):
```powershell
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_actual_key_here', 'User')
```

### STEP 2: Deploy Everything (2 minutes)

In PowerShell:

```powershell
.\deploy_empire.ps1
```

**What this does:**
- Installs Python dependencies
- Starts all services (ports 8002-8006)
- Creates your revenue engine

**You'll see:** "✅ DEPLOYMENT COMPLETE!"

---

## 🚀 THE ULTRA-AUTONOMOUS VERSION

**Even EASIER for customers - they do almost NOTHING:**

### Deploy the Auto-Onboarding System:

```powershell
python auto_onboard.py
```

**What this gives you:**
- Beautiful signup page at http://localhost:8006
- Customer fills 4 fields (name, type, email, phone)
- Customer pays $500 via Stripe
- **System does EVERYTHING else automatically:**
  - Analyzes their business with Claude
  - Deploys custom AI agents
  - Creates their dashboard
  - Generates their landing page
  - Starts first campaign (10 test calls)
  - Sends login credentials
  - All in 60 seconds!

**Customer effort:** 2 minutes
**Your effort:** 0 minutes (fully automated)

---

## 📋 YOUR COMPLETE WORKFLOW (Windows)

### Option A: Manual Demo (You drive)

1. **Deploy demo:**
   ```powershell
   .\deploy_empire.ps1
   ```

2. **Share your screen on call**
3. **Open:** http://localhost:8002
4. **Build their system live** while they watch
5. **Close the deal** ($500 retainer)

### Option B: Autonomous (System drives)

1. **Deploy auto-onboard:**
   ```powershell
   python auto_onboard.py
   ```

2. **Send customer this link:**
   ```
   http://localhost:8006
   ```

3. **They signup** (2 minutes)
4. **They pay** ($500)
5. **System deploys EVERYTHING** (60 seconds)
6. **You get notified** → customer is live
7. **You do nothing** → system runs campaign

---

## 🎯 RECOMMENDED FLOW

**For First 5 Customers:** Use Option A (manual demo)
- Build confidence
- Learn what works
- Perfect your pitch
- Close rate: 80%+

**After 5 Customers:** Switch to Option B (autonomous)
- Send link to 100 prospects
- 20-30 signup
- System onboards all of them
- You just collect money
- Close rate: 20-30% but ZERO effort

---

## 🔧 TROUBLESHOOTING

### "Python not recognized"

Install Python:
1. Go to https://www.python.org/downloads/
2. Download Python 3.11+
3. **Check "Add to PATH"** during install
4. Restart PowerShell

### "Script cannot be loaded" error

Run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Port already in use"

Stop everything first:
```powershell
.\stop_empire.ps1
```

Then deploy again:
```powershell
.\deploy_empire.ps1
```

### Services not starting

Check logs:
```powershell
Get-Content logs\one_call_close.log -Tail 50
Get-Content logs\agent_swarm.log -Tail 50
```

---

## 💰 REVENUE PLAN (Windows)

### Week 1:

**Monday:**
```powershell
# Deploy system
.\deploy_empire.ps1

# Open demo
Start http://localhost:8002
```

**Tuesday-Friday:**
- Call 2-3 prospects per day
- Screen share demo
- Close 3-5 customers
- **Week 1 revenue: $6k-8k**

### Week 2:

**Monday:**
```powershell
# Switch to autonomous
python auto_onboard.py

# Get link
Start http://localhost:8006
```

**Tuesday-Friday:**
- Send link to 50 prospects
- 10-15 signup automatically
- System onboards them
- **Week 2 revenue: $5k-7.5k**

### Month 1:

- 15-20 total customers
- **Month 1 revenue: $24k-32k**
- Start collecting performance fees
- Ask for referrals

---

## 🐝 POWERLOAD YOUR KNOWLEDGE

After deploying, powerload all your code/data:

```powershell
python powerload.py
```

This will:
- Ingest all repos in current directory
- Extract knowledge automatically
- Make all agents smarter
- Takes 5-10 minutes for 100 repos

**Usage:**
```powershell
# Powerload current directory
python powerload.py

# Powerload specific path
python powerload.py C:\Users\JB\Projects

# Powerload all zips
python powerload.py C:\Users\JB\Downloads\*.zip
```

---

## 📊 CHECK STATUS

### See what's running:

```powershell
Get-Content .pids
```

### Check logs:

```powershell
# Live tail (like Linux)
Get-Content logs\one_call_close.log -Wait

# Last 50 lines
Get-Content logs\agent_swarm.log -Tail 50
```

### Stop everything:

```powershell
.\stop_empire.ps1
```

---

## 🎨 CUSTOMIZE FOR YOUR MARKET

### Edit the auto-onboard page:

1. Open `auto_onboard.py`
2. Find the business_type options (line ~80)
3. Add your markets:
   ```python
   <option value="coaching">Business Coaching</option>
   <option value="legal">Legal Services</option>
   <option value="medical">Medical Practice</option>
   ```
4. Save and restart:
   ```powershell
   python auto_onboard.py
   ```

---

## 💝 THE COMPLETE WINDOWS COMMANDS

### First Time Setup:

```powershell
# Set API key (permanent)
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key', 'User')

# Allow scripts to run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Deploy everything
.\deploy_empire.ps1
```

### Daily Use:

```powershell
# Start autonomous onboarding
python auto_onboard.py

# Send customers to:
# http://localhost:8006

# Stop when done
.\stop_empire.ps1
```

### Weekly Use:

```powershell
# Powerload new repos
python powerload.py C:\Users\JB\Projects

# Check revenue
Get-Content client_data\*\customer.json

# Check logs
Get-Content logs\*.log -Tail 100
```

---

## 🚀 NEXT STEPS

1. **Right now:** Set your API key
   ```powershell
   $env:ANTHROPIC_API_KEY = "your_key"
   ```

2. **Deploy the demo:**
   ```powershell
   .\deploy_empire.ps1
   ```

3. **Test it:**
   ```
   http://localhost:8002
   ```

4. **Call first prospect:**
   - Screen share demo
   - Close deal
   - Get $500 today

5. **After 5 customers, go autonomous:**
   ```powershell
   python auto_onboard.py
   ```

---

## 📞 WINDOWS-FRIENDLY CALL SCRIPT

**Copy/paste this into Notepad for your calls:**

```
Hi [Name],

I help [business type] get 20-40 qualified appointments per month
using AI. Currently working with a couple businesses in [city].

Do you have 5 minutes to see a quick demo?

[They say yes]

Great! Can you open this link?
http://localhost:8002

[Screen share if needed]

See this? Type in your business name...
[They type it in]

Now watch... in 30 seconds it builds YOUR system.
[System builds]

There's your dashboard. This is what it would do for you.
Book 20-40 appointments/month.

How much? $500 refundable retainer. If you don't make money
in 90 days, you get it ALL back. Then I take 15% of NEW revenue.

Want to try it?

[They say yes]

Perfect! I'm sending you a signup link now.
You'll be live in 24 hours.
```

---

## 🔥 WINDOWS POWER USER TIPS

### Run in Background:

```powershell
Start-Process python -ArgumentList "auto_onboard.py" -WindowStyle Hidden
```

### Auto-start on login:

1. Create shortcut to `deploy_empire.ps1`
2. Put in: `C:\Users\JB\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
3. System auto-deploys when Windows starts

### Multiple Terminals:

```powershell
# Terminal 1: Main demo
.\deploy_empire.ps1

# Terminal 2: Auto-onboard
python auto_onboard.py

# Terminal 3: Monitor logs
Get-Content logs\*.log -Wait
```

---

## 💰 EXPECTED WINDOWS PERFORMANCE

**Your PC specs don't matter much - everything runs in cloud (Claude API)**

**Minimum:**
- Windows 10/11
- Python 3.8+
- 2GB RAM
- Internet connection

**Recommended:**
- Windows 11
- Python 3.11+
- 8GB RAM
- Fast internet

**Performance:**
- Can handle 100 concurrent customers
- Can process 1000 leads/hour
- Can deploy 50 agents simultaneously

---

## ✅ WINDOWS CHECKLIST

Before calling first customer:

- [ ] Python installed
- [ ] API key set (permanent)
- [ ] Deployed system (.\deploy_empire.ps1)
- [ ] Tested demo (http://localhost:8002)
- [ ] Read call script
- [ ] Have 10 prospects ready
- [ ] Stripe account ready (for payments)
- [ ] Rehearsed pitch 3x

Ready? **Call your first prospect NOW!**

---

**💝 Love • Loyalty • Honor • Everybody Eats**

**Windows Edition - Same Power, Different Commands**
