# Competition Brain - Deployment Guide

Complete guide for deploying Competition Brain to production.

---

## Table of Contents

1. [Quick Deploy (Recommended)](#quick-deploy-recommended)
2. [Platform-Specific Guides](#platform-specific-guides)
   - [Vercel + Railway](#vercel--railway)
   - [Docker (Self-Hosted)](#docker-self-hosted)
   - [Other Platforms](#other-platforms)
3. [Environment Variables](#environment-variables)
4. [Post-Deployment](#post-deployment)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

---

## Quick Deploy (Recommended)

The easiest production setup uses **Vercel** for the frontend and **Railway** for the backend.

### Prerequisites

- GitHub account
- Vercel account (free tier available)
- Railway account (free tier available)
- API keys for at least 2-3 AI providers

### Estimated Time

**15 minutes** from start to live deployment

---

## Platform-Specific Guides

### Vercel + Railway

This is the **recommended** setup for most users.

#### Part 1: Deploy Backend to Railway

1. **Sign up** at https://railway.app/

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your fork of `Capstone`
   - Set root directory: `competition-brain/backend`

3. **Add Environment Variables**

   Click "Variables" and add:
   ```
   NODE_ENV=production
   PORT=3001
   OPENAI_API_KEY=sk-your-key
   ANTHROPIC_API_KEY=sk-ant-your-key
   GOOGLE_API_KEY=your-key
   GROQ_API_KEY=your-key
   ```

   See [Environment Variables](#environment-variables) for all options.

4. **Deploy**
   - Railway will auto-deploy
   - Wait for build to complete (~2-3 minutes)
   - Copy the generated URL (e.g., `https://competition-brain-backend.railway.app`)

5. **Verify**
   ```bash
   curl https://your-backend.railway.app/health
   # Should return: {"status":"ok","version":"1.0.0"}
   ```

---

#### Part 2: Deploy Frontend to Vercel

1. **Sign up** at https://vercel.com/

2. **Import Project**
   - Click "New Project"
   - Import from GitHub
   - Select your `Capstone` repository
   - Framework: Next.js (auto-detected)
   - Root Directory: `competition-brain/frontend`

3. **Configure Environment**

   Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

   Replace with your Railway backend URL from Part 1.

4. **Deploy**
   - Click "Deploy"
   - Wait for build (~2-3 minutes)
   - Your site will be live at `https://your-project.vercel.app`

5. **Verify**
   - Visit your Vercel URL
   - Click the voice orb or type a test query
   - Check that responses are working

---

### Docker (Self-Hosted)

For full control, deploy using Docker Compose.

#### Prerequisites

- Linux server (Ubuntu 22.04+ recommended)
- Docker & Docker Compose installed
- Domain name (optional but recommended)
- At least 2GB RAM, 1 CPU core

#### Deployment Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/miKeDroP-JB/Capstone.git
   cd Capstone/competition-brain
   ```

2. **Create Environment File**
   ```bash
   cp backend/.env.example .env
   nano .env
   ```

   Add your API keys:
   ```env
   OPENAI_API_KEY=sk-your-key
   ANTHROPIC_API_KEY=sk-ant-your-key
   GOOGLE_API_KEY=your-key
   # ... add others as needed
   ```

3. **Build and Start**
   ```bash
   docker-compose up -d --build
   ```

4. **Verify**
   ```bash
   # Check containers are running
   docker-compose ps

   # Check backend health
   curl http://localhost:3001/health

   # Check frontend
   curl http://localhost:3000
   ```

5. **Access**
   - Frontend: `http://your-server-ip:3000`
   - Backend: `http://your-server-ip:3001`

#### Add HTTPS with Nginx

1. **Install Nginx**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/competition-brain
   ```

   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }

       location /api {
           proxy_pass http://localhost:3001;
           proxy_http_version 1.1;
           proxy_set_header Host $host;
       }
   }
   ```

3. **Enable and Get SSL**
   ```bash
   sudo ln -s /etc/nginx/sites-available/competition-brain /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   sudo certbot --nginx -d your-domain.com
   ```

---

### Other Platforms

#### Render

**Backend**:
1. Create new Web Service
2. Connect GitHub repo
3. Root directory: `competition-brain/backend`
4. Build command: `npm install`
5. Start command: `npm start`
6. Add environment variables

**Frontend**:
1. Create new Static Site
2. Root directory: `competition-brain/frontend`
3. Build command: `npm run build`
4. Publish directory: `.next`
5. Add `NEXT_PUBLIC_API_URL` environment variable

#### Netlify

**Frontend Only** (backend needs separate hosting):
1. Import from GitHub
2. Base directory: `competition-brain/frontend`
3. Build command: `npm run build`
4. Publish directory: `.next`
5. Add environment variable: `NEXT_PUBLIC_API_URL`

#### DigitalOcean App Platform

1. Create new App
2. Select Docker Hub or GitHub
3. Use provided Dockerfiles
4. Add environment variables
5. Deploy

---

## Environment Variables

### Backend (.env)

#### Required (Minimum 2-3 providers)

```env
# Server
NODE_ENV=production
PORT=3001

# At least add these for basic functionality:
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-key
```

#### Optional (All Providers)

```env
# Additional providers
MISTRAL_API_KEY=your-mistral-key
COHERE_API_KEY=your-cohere-key
GROQ_API_KEY=your-groq-key
DEEPSEEK_API_KEY=your-deepseek-key
XAI_API_KEY=your-xai-key
PERPLEXITY_API_KEY=your-perplexity-key
```

See [backend/AI_PROVIDERS.md](backend/AI_PROVIDERS.md) for how to get each API key.

### Frontend

```env
# Backend API URL
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

**Important**: Must start with `NEXT_PUBLIC_` to be accessible in browser.

---

## Post-Deployment

### 1. Verify All Endpoints

```bash
# Health check
curl https://your-backend.com/health

# Get models
curl https://your-backend.com/api/models

# Test query (replace with your URL)
curl -X POST https://your-backend.com/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 2+2?",
    "config": {
      "models": ["gpt-4o-mini"],
      "powerLevel": 50,
      "timeLimit": 30
    }
  }'
```

### 2. Test Frontend

1. Visit your frontend URL
2. Click voice orb or use text input
3. Try a test query: "What is machine learning?"
4. Verify synthesized response appears
5. Check individual agent responses
6. Try control panel (gear icon)

### 3. Monitor Logs

**Railway**:
- Go to project → Deployments → View logs

**Vercel**:
- Go to project → Deployments → Functions tab

**Docker**:
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend
```

### 4. Set Up Monitoring (Optional)

#### Uptime Monitoring

Use [UptimeRobot](https://uptimerobot.com/) (free):
1. Add monitor for `https://your-backend.com/health`
2. Add monitor for `https://your-frontend.com`
3. Set alert email

#### Error Tracking

Use [Sentry](https://sentry.io/) (free tier):
1. Create new project
2. Add to `backend/src/server.js`:
   ```javascript
   const Sentry = require("@sentry/node");
   Sentry.init({ dsn: "your-sentry-dsn" });
   ```
3. Deploy updates

---

## Cost Estimates

### Free Tier (Development/Testing)

**Hosting**:
- Vercel: FREE (100GB bandwidth, unlimited requests)
- Railway: FREE ($5 credit/month, ~500 hours)
- **Total**: $0/month

**AI APIs** (using free models):
- Gemini 1.5 Flash: FREE (15 RPM)
- Groq Llama: FREE (14,400 req/day)
- **Total**: $0/month

**Grand Total**: **$0/month**

---

### Production (100-500 queries/day)

**Hosting**:
- Vercel Pro: $20/month
- Railway Starter: $5/month
- **Total**: $25/month

**AI APIs** (balanced mix):
- GPT-4o Mini: ~$5/month
- Claude Haiku: ~$5/month
- Gemini: FREE
- **Total**: ~$10/month

**Grand Total**: **~$35/month**

---

### High Volume (5000+ queries/day)

**Hosting**:
- Vercel Pro: $20/month
- Railway: $20/month
- **Total**: $40/month

**AI APIs** (competition mode):
- OpenAI o1: ~$100/month
- Claude Sonnet 4.5: ~$80/month
- Gemini Exp: ~$50/month
- Others: ~$50/month
- **Total**: ~$280/month

**Grand Total**: **~$320/month**

---

## Scaling

### Horizontal Scaling

#### Backend (Railway)

1. Go to project Settings
2. Increase instances (replicas)
3. Enable autoscaling

#### Frontend (Vercel)

- Automatic scaling (no configuration needed)
- Handles millions of requests

### Caching

Enable response caching to reduce API costs:

```javascript
// Already enabled by default
const result = await client.query(query, {
  models: ['gpt-4o'],
  useCache: true  // Saves identical queries
});
```

**Savings**: 50-80% reduction in API costs during development

### Database (Future Enhancement)

For query history and analytics:

1. Add PostgreSQL on Railway
2. Store query results
3. Implement analytics dashboard

---

## Troubleshooting

### "Connection refused" errors

**Problem**: Frontend can't reach backend

**Solutions**:
1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Check backend is running: `curl https://backend-url/health`
3. Check CORS settings in `backend/src/server.js`

### "All models failed"

**Problem**: No API keys configured

**Solutions**:
1. Check environment variables are set
2. Verify API keys are valid
3. Check API provider status pages
4. Review backend logs for specific errors

### Docker containers not starting

**Problem**: Build or runtime errors

**Solutions**:
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### High API costs

**Problem**: Unexpected bills

**Solutions**:
1. Enable response caching (default: on)
2. Use free models for development
3. Set model budgets in provider dashboards
4. Monitor usage via provider dashboards

### Slow response times

**Problem**: Queries taking too long

**Solutions**:
1. Reduce `timeLimit` in queries
2. Use fewer models
3. Use faster models (Groq, Gemini Flash)
4. Check backend server resources

---

## Security Checklist

Before going live:

- [ ] All API keys in environment variables (not code)
- [ ] HTTPS enabled (SSL certificates)
- [ ] CORS configured properly
- [ ] Rate limiting enabled (optional)
- [ ] Error messages don't expose sensitive data
- [ ] Dependency vulnerabilities checked (`npm audit`)
- [ ] Environment variables secured in hosting platform
- [ ] Backup strategy in place
- [ ] Monitoring/alerting configured

---

## Maintenance

### Updates

**Backend**:
```bash
cd backend
npm update
npm audit fix
git commit -am "Update dependencies"
git push
```

**Frontend**:
```bash
cd frontend
npm update
npm audit fix
git commit -am "Update dependencies"
git push
```

**Auto-deploy**: Railway and Vercel will auto-deploy on push to main branch

### Backups

**Important data**:
- `.cache/` directory (response cache)
- Environment variables (export from platforms)
- Custom configuration

### Logs Retention

- Railway: 7 days (free tier)
- Vercel: 1 day (free tier)
- Docker: Unlimited (configure log rotation)

---

## Support

**Issues**: https://github.com/miKeDroP-JB/Capstone/issues

**Documentation**:
- [Main README](README.md)
- [AI Providers Guide](backend/AI_PROVIDERS.md)
- [SDK Documentation](sdk/README.md)

**Platform Support**:
- Vercel: https://vercel.com/support
- Railway: https://railway.app/help
- Docker: https://docs.docker.com/

---

**Ready to compete! 🏆**
