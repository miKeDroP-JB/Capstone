# 💰 Profit Engine Dashboard

Real-time monitoring and control dashboard for the automated profit generation system.

## Features

### 📊 Real-time Monitoring
- Live system statistics (total revenue, active apps, budget usage, ROI)
- Auto-refresh every 5 seconds
- Visual budget tracking bar

### 🎮 Control Panel
- Start automated profit cycles
- Configure number of apps to build (1-10)
- View market opportunities with profit scores
- Real-time cycle status updates

### 🚀 App Management
- View all deployed apps
- Monitor individual app revenue and users
- Scale successful apps with one click
- Stop/pause underperforming apps
- Quick access to deployed URLs

### 🎯 Market Intelligence
- 8 pre-researched profitable opportunities
- Profit scores (0-100)
- Revenue estimates
- Monetization strategies
- Difficulty ratings

## Tech Stack

- **Frontend**: React 18 with modern hooks
- **Backend**: FastAPI with async support
- **Database**: SQLite for persistence
- **Styling**: Custom CSS with glassmorphism effects
- **Integration**: Direct connection to profit_engine.py

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs on: http://localhost:3000

## API Endpoints

- `GET /api/stats/system` - Overall system statistics
- `GET /api/apps` - List all deployed apps
- `GET /api/apps/{app_id}/revenue` - Revenue history for specific app
- `GET /api/opportunities` - Available market opportunities
- `GET /api/cycle/status` - Current profit cycle status
- `POST /api/cycle/start` - Start new profit generation cycle
- `POST /api/apps/{app_id}/scale` - Scale up an app
- `DELETE /api/apps/{app_id}` - Stop an app

## How It Works

1. **Start Profit Cycle**: Click "Start Profit Cycle" to begin automated app generation
2. **Monitor Progress**: Watch real-time updates as apps are built and deployed
3. **Track Revenue**: See monthly revenue estimates for each app
4. **Scale Winners**: Click "Scale" on profitable apps to increase revenue
5. **Manage Budget**: Visual budget tracker shows remaining free tier credits

## Database Schema

### Apps Table
- `id`: Unique app identifier
- `name`: App display name
- `url`: Deployed URL
- `niche`: Market niche
- `monthly_revenue`: Estimated monthly revenue
- `total_users`: Current user count
- `status`: active | stopped
- `created_at`: Timestamp

### Revenue History Table
- Tracks revenue over time for trend analysis
- Links to apps via `app_id` foreign key

### System Metrics Table
- Total apps count
- Total revenue
- Budget used/remaining
- Timestamps for historical tracking

## Integration with Profit Engine

The dashboard directly imports and uses `profit_engine.py`:

```python
from profit_engine import ProfitEngine, DeployedApp, MarketOpportunity

# Create instance
profit_engine = ProfitEngine()

# Run cycle
result = await profit_engine.run_profit_cycle(num_apps=3)
```

All data is persisted to SQLite and displayed in real-time on the dashboard.

## UI Components

### System Stats Cards
- Green: Total Revenue
- Blue: Active Apps
- Orange: Budget Used
- Purple: ROI Percentage

### Control Panel
- Input field for number of apps
- Primary action button for starting cycles
- Secondary button for viewing opportunities
- Budget progress bar

### App Cards
- App name and status badge
- Revenue and user metrics
- Deployed URL link
- Scale and stop action buttons
- Color-coded by status

### Opportunity Cards
- Profit score badge (color-coded 0-100)
- Niche description
- Revenue estimates
- Monetization strategy
- Difficulty and time to market

## Profit Cycle Flow

```
User clicks "Start Cycle"
    ↓
Backend receives POST /api/cycle/start
    ↓
Async task starts profit_engine.run_profit_cycle()
    ↓
For each app:
    - Research market opportunity
    - Generate complete code
    - Deploy to free tier platform
    - Set up monetization
    - Track performance
    ↓
Save all results to database
    ↓
Frontend auto-refreshes and shows new apps
    ↓
User can scale winners or stop losers
```

## Monetization Tracking

Each app includes:
- **Freemium**: Free tier + paid upgrades
- **Pay-per-use**: API calls, credits
- **Affiliate**: Commission from referrals
- **Ads**: Display advertising revenue

Revenue is estimated based on:
- Market size
- Competition level
- User engagement
- Conversion rates

## Deployment

### Local Development
```bash
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend
cd frontend && npm start
```

### Production
- Backend: Deploy to Railway/Render free tier
- Frontend: Deploy to Vercel/Netlify free tier
- Database: SQLite (or upgrade to PostgreSQL)

## Future Enhancements

- [ ] Revenue charts with historical trends
- [ ] A/B testing controls for apps
- [ ] Automated scaling based on performance
- [ ] Email/Slack notifications for milestones
- [ ] Multi-user support with authentication
- [ ] Custom opportunity suggestions
- [ ] Integration with real payment processors
- [ ] Advanced analytics and forecasting

## Troubleshooting

**Apps not loading?**
- Check backend is running on port 8000
- Check frontend proxy is configured correctly
- Verify profit_engine.py is in parent directory

**Cycle not starting?**
- Check console for errors
- Ensure profit_engine.py imports successfully
- Verify code_generator.py is available

**Database errors?**
- Delete dashboard.db and restart backend
- Check write permissions in backend directory

## License

Part of the 0RB LIMITLESS OS profit generation system.

---

**Built with 🧠 by the Code Generation Engine**
*Turning $1000 free credits into maximum profit*
