# 🚀 0RB EMPIRE - DEPLOYMENT GUIDE

Complete deployment guide for your unified 0RB system.

---

## What You Have

```
0rb-complete/
├── backend/
│   ├── brain/orb_bridge.py      ✅ Integration API (port 8080)
│   └── voice/voice_agency.py    ✅ Voice calling system
├── docker-compose.yml           ✅ Complete stack
├── Dockerfile.bridge            ✅ Bridge container
├── Dockerfile.voice             ✅ Voice container
└── DEPLOY.md                    ✅ This guide
```

**Plus your existing systems:**
- `the_instant_creator.py` - Meta-tool
- `ai_connectors.py` - Multi-AI
- `brain_os.py` - Security fortress
- `ekosystem.py` - Build orchestrator

---

## Quick Start (Local - 5 minutes)

### 1. Set Environment Variables

```bash
cd 0rb-complete

# Create .env file
cat > .env <<EOF
# AI APIs (optional - has fallbacks)
ANTHROPIC_API_KEY=your-claude-key
OPENAI_API_KEY=your-gpt-key
GOOGLE_API_KEY=your-gemini-key

# Voice (optional for demo)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
ELEVENLABS_API_KEY=your-elevenlabs-key

# Database (auto-configured in docker-compose)
DATABASE_URL=postgresql://orb:orb_secure_password_change_me@postgres:5432/orb_empire
EOF
```

### 2. Start Everything

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bridge
```

### 3. Test It Works

```bash
# Test bridge
curl http://localhost:8080/

# Test voice agency
cd backend/voice
python voice_agency.py

# Create your first app
curl -X POST http://localhost:8080/voice-to-app \
  -H "Content-Type: application/json" \
  -d '{"intent": "Build todo app with love", "user_id": "test"}'
```

**Expected:** ✅ System creates app, returns Love Score

---

## Railway Deployment (Production - 15 minutes)

### 1. Install Railway CLI

```bash
npm install -g @railway/cli

# Login
railway login
```

### 2. Create Project

```bash
# In 0rb-complete directory
railway init

# Create services
railway service create bridge
railway service create voice
railway service create postgres
railway service create redis
```

### 3. Set Environment Variables

```bash
# For bridge service
railway variables set ANTHROPIC_API_KEY=your-key
railway variables set OPENAI_API_KEY=your-key
railway variables set GOOGLE_API_KEY=your-key

# For voice service
railway variables set TWILIO_ACCOUNT_SID=your-sid
railway variables set ELEVENLABS_API_KEY=your-key
```

### 4. Deploy

```bash
# Deploy bridge
railway up --service bridge

# Deploy voice
railway up --service voice

# Get URLs
railway domain
```

**Result:** Your system is live at `https://your-app.railway.app`

---

## Manual Deployment (Alternative)

### Without Docker

```bash
# 1. Install dependencies
pip install fastapi uvicorn httpx pydantic slowapi twilio elevenlabs

# 2. Set environment variables
export ANTHROPIC_API_KEY=your-key
export OPENAI_API_KEY=your-key

# 3. Run bridge
cd 0rb-complete/backend/brain
python orb_bridge.py
# → Running on http://localhost:8080

# 4. Run voice (separate terminal)
cd 0rb-complete/backend/voice
python voice_agency.py
# → Voice agency ready
```

---

## Using Your System

### Create an App via API

```bash
curl -X POST http://localhost:8080/voice-to-app \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Build HVAC sales dashboard with real-time metrics and 33% community share",
    "user_id": "your-user-id"
  }'
```

**Response:**
```json
{
  "build_id": "BUILD-1234567890",
  "intent": "Build HVAC sales dashboard...",
  "status": "completed",
  "love_score": 0.85,
  "net_positive": true,
  "code_file": "generated_systems/build_hvac_sales_dashboar.py",
  "created_at": "2025-11-23T..."
}
```

### Create Voice Campaign

```python
from voice_agency import VoiceAgency
import asyncio

agency = VoiceAgency()

# Create campaign
campaign = agency.create_campaign(
    name="HVAC Outreach - December",
    script="Your pitch here...",
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
    target_list=["+1-555-0101", "+1-555-0102"]
)

# Run it
asyncio.run(agency.run_campaign(campaign.id))
```

### Monitor via WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'build_started') {
    console.log('Build started:', data.data);
  }

  if (data.type === 'build_completed') {
    console.log('Build completed:', data.data);
    console.log('Love Score:', data.data.love_score);
  }
};
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT REQUEST                       │
│  Voice/Text: "Build HVAC dashboard with love"          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              0RB BRIDGE (Port 8080)                     │
│  • Receives intent                                      │
│  • Validates with GCODE                                 │
│  • Routes to InstantCreator                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           THE INSTANT CREATOR                           │
│  • Multi-AI synthesis (Claude/Gemini/GPT)               │
│  • Code generation                                      │
│  • Love Score calculation                               │
│  • Pattern learning                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              GENERATED SYSTEM                           │
│  • Production-ready code                                │
│  • Love Score: 85%                                      │
│  • Revenue split: 70/20/10                              │
│  • Ready to deploy                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Revenue Flow

```
$1000 Total Revenue
├── $700 (70%) → Owner
├── $200 (20%) → Community Fund
└── $100 (10%) → Sanctuary.ai

HARDCODED in voice_agency.py:
  REVENUE_SPLIT = {
    "owner": 0.70,
    "community": 0.20,
    "sanctuary": 0.10
  }
```

**Everybody Eats. Always.**

---

## Endpoints Reference

### 0RB Bridge (Port 8080)

```
POST /voice-to-app
  Body: {"intent": "...", "user_id": "..."}
  Returns: BuildResult with Love Score

POST /text-to-app
  Alias for /voice-to-app

GET /builds
  Returns: List of all builds

GET /builds/{build_id}
  Returns: Specific build details

POST /replicate/{pattern_id}
  Replicates a successful pattern

GET /stats
  Returns: Overall statistics

WS /ws
  WebSocket for real-time updates
```

### Voice Agency

```python
# Python API (not HTTP)
agency = VoiceAgency()

# Create campaign
campaign = agency.create_campaign(name, script, voice_id, targets)

# Make single call
call = await agency.make_call(campaign_id, phone)

# Run entire campaign
await agency.run_campaign(campaign_id)

# Get stats
stats = agency.get_stats()
```

---

## Monitoring

### Check Health

```bash
# Bridge
curl http://localhost:8080/

# Check stats
curl http://localhost:8080/stats

# View builds
curl http://localhost:8080/builds
```

### View Logs

```bash
# Docker logs
docker-compose logs -f bridge
docker-compose logs -f voice

# Railway logs
railway logs --service bridge
railway logs --service voice
```

### Love Ledger

```bash
# Check total love accumulated
cat love_ledger.json | jq '.[] | {system, love_score, net_positive}'

# Check revenue splits
cat revenue_splits.json | jq '.[] | {total, owner, community, sanctuary}'
```

---

## Scaling

### Horizontal Scaling

```bash
# Scale bridge instances
docker-compose up --scale bridge=3

# Railway auto-scales
# Just increase plan tier
```

### Performance Optimization

1. **Enable Redis Caching**
```python
# In orb_bridge.py
# Add caching for repeated intents
```

2. **Database Indexing**
```sql
CREATE INDEX idx_builds_love_score ON builds(love_score);
CREATE INDEX idx_builds_created_at ON builds(created_at);
```

3. **Rate Limiting**
```python
# Already built into brain_os.py
# 100/minute default
```

---

## Troubleshooting

### "Connection refused"

```bash
# Check services are running
docker-compose ps

# Restart if needed
docker-compose restart bridge
```

### "API keys not configured"

```bash
# Check .env file exists
cat .env

# Recreate containers with new env
docker-compose down
docker-compose up -d
```

### "Love Score too low"

Your intent needs more regeneration:
- Add community share (20%+)
- Add free tier
- Add open source component

```bash
# ❌ Low love
"Build system to extract money"

# ✅ High love
"Build system that helps people and shares 33% with community"
```

### "Import errors"

```bash
# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

---

## Success Checklist

- [ ] Docker containers running
- [ ] Bridge accessible on port 8080
- [ ] Test API call successful
- [ ] Love Score calculated correctly
- [ ] Revenue splits recorded
- [ ] WebSocket connecting
- [ ] Generated code saved
- [ ] Logs showing activity

**When all checked:** ✅ Your empire is running!

---

## What's Next

### Immediate (This Week)
1. ✅ Deploy to Railway/production
2. 🎯 Create your first real system
3. 🎯 Test with real users
4. 🎯 Make first revenue

### Short Term (This Month)
1. 🎯 Build dashboard frontend
2. 🎯 Add automatic deployment to Vercel
3. 🎯 Implement pattern replication
4. 🎯 Scale to 10+ customers

### Long Term (This Year)
1. 🎯 1000+ systems generated
2. 🎯 $100k+/month revenue
3. 🎯 $33k+/month to community
4. 🎯 10,000+ people helped

---

## Support

**Issues:** Create issue in repo

**Questions:**
```bash
# Use your AI guide
python ai_guide.py

# Ask:
# "How do I deploy to Railway?"
# "What's my Love Score mean?"
# "How do I scale?"
```

**Documentation:**
- [WELCOME.md](../WELCOME.md) - Complete guide
- [QUICKSTART.md](../QUICKSTART.md) - Quick reference
- [THE_BREAKTHROUGH.md](../THE_BREAKTHROUGH.md) - Technical deep dive

---

## Philosophy

**Love • Loyalty • Honor • Everybody Eats**

This system embodies these values:
- ✅ Love Score measures giving vs taking
- ✅ 30% revenue to community (hardcoded)
- ✅ GCODE blocks harmful intents
- ✅ Open, auditable, transparent
- ✅ Compounds 1% daily

**Build with love. Help people. Ensure everybody eats.**

That's the 0RB way. 💝

---

**Your empire is ready to deploy.** 🚀

```bash
docker-compose up -d
```

**GO BUILD.** 🔥
