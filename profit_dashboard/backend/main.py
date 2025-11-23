#!/usr/bin/env python3
"""
Profit Dashboard Backend
Real-time monitoring and control for the Profit Engine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sqlite3
import asyncio
from datetime import datetime
import sys
import os

# Add parent directory to path to import profit_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from profit_engine import ProfitEngine, DeployedApp, MarketOpportunity

app = FastAPI(title="Profit Dashboard API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global profit engine instance
profit_engine = None
running_cycle = False

# Database setup
def init_db():
    conn = sqlite3.connect('dashboard.db')
    c = conn.cursor()

    # Apps table
    c.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            niche TEXT NOT NULL,
            monthly_revenue REAL DEFAULT 0,
            total_users INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Revenue history table
    c.execute("""
        CREATE TABLE IF NOT EXISTS revenue_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT NOT NULL,
            revenue REAL NOT NULL,
            users INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (app_id) REFERENCES apps(id)
        )
    """)

    # System metrics table
    c.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_apps INTEGER,
            total_revenue REAL,
            budget_used REAL,
            budget_remaining REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()

# Models
class AppStats(BaseModel):
    id: str
    name: str
    url: str
    niche: str
    monthly_revenue: float
    total_users: int
    status: str
    created_at: str

class SystemStats(BaseModel):
    total_apps: int
    total_revenue: float
    budget_used: float
    budget_remaining: float
    roi_percentage: float

class RevenuePoint(BaseModel):
    timestamp: str
    revenue: float
    users: int

class CycleConfig(BaseModel):
    num_apps: int = 3
    auto_scale: bool = True

# Routes
@app.get("/")
def root():
    return {"message": "Profit Dashboard API", "status": "running"}

@app.get("/api/stats/system", response_model=SystemStats)
def get_system_stats():
    """Get overall system statistics"""
    conn = sqlite3.connect('dashboard.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Get totals
    c.execute("SELECT COUNT(*) as count FROM apps WHERE status='active'")
    total_apps = c.fetchone()['count']

    c.execute("SELECT SUM(monthly_revenue) as total FROM apps WHERE status='active'")
    result = c.fetchone()
    total_revenue = result['total'] if result['total'] else 0

    # Get latest budget info
    c.execute("SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 1")
    metrics = c.fetchone()

    if metrics:
        budget_used = metrics['budget_used']
        budget_remaining = metrics['budget_remaining']
    else:
        budget_used = 0
        budget_remaining = 1000

    conn.close()

    roi = (total_revenue / budget_used * 100) if budget_used > 0 else 0

    return SystemStats(
        total_apps=total_apps,
        total_revenue=total_revenue,
        budget_used=budget_used,
        budget_remaining=budget_remaining,
        roi_percentage=roi
    )

@app.get("/api/apps", response_model=List[AppStats])
def get_apps():
    """Get all deployed apps"""
    conn = sqlite3.connect('dashboard.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM apps ORDER BY created_at DESC")
    apps = [dict(row) for row in c.fetchall()]
    conn.close()

    return apps

@app.get("/api/apps/{app_id}/revenue", response_model=List[RevenuePoint])
def get_app_revenue_history(app_id: str):
    """Get revenue history for specific app"""
    conn = sqlite3.connect('dashboard.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT timestamp, revenue, users
        FROM revenue_history
        WHERE app_id = ?
        ORDER BY timestamp DESC
        LIMIT 100
    """, (app_id,))

    history = [dict(row) for row in c.fetchall()]
    conn.close()

    return history

@app.get("/api/opportunities", response_model=List[Dict])
async def get_opportunities():
    """Get available market opportunities"""
    global profit_engine

    if not profit_engine:
        profit_engine = ProfitEngine()

    opportunities = await profit_engine.find_opportunities()

    return [{
        "id": opp.id,
        "niche": opp.niche,
        "description": opp.description,
        "profit_score": opp.profit_score,
        "estimated_monthly_revenue": opp.estimated_monthly_revenue,
        "monetization_strategy": opp.monetization_strategy,
        "difficulty": opp.difficulty,
        "time_to_market": opp.time_to_market
    } for opp in opportunities]

@app.post("/api/cycle/start")
async def start_profit_cycle(config: CycleConfig):
    """Start a new profit generation cycle"""
    global profit_engine, running_cycle

    if running_cycle:
        raise HTTPException(status_code=400, detail="Cycle already running")

    if not profit_engine:
        profit_engine = ProfitEngine()

    # Run cycle in background
    asyncio.create_task(run_cycle_background(config))

    return {"message": "Profit cycle started", "config": config}

async def run_cycle_background(config: CycleConfig):
    """Run profit cycle in background and update database"""
    global profit_engine, running_cycle

    running_cycle = True

    try:
        # Run the cycle
        result = await profit_engine.run_profit_cycle(num_apps=config.num_apps)

        # Save to database
        conn = sqlite3.connect('dashboard.db')
        c = conn.cursor()

        for app in result['deployed_apps']:
            c.execute("""
                INSERT OR REPLACE INTO apps (id, name, url, niche, monthly_revenue, total_users, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                app.id,
                app.name,
                app.url,
                app.opportunity.niche,
                app.monthly_revenue,
                app.total_users,
                app.status
            ))

            # Add revenue history
            c.execute("""
                INSERT INTO revenue_history (app_id, revenue, users)
                VALUES (?, ?, ?)
            """, (app.id, app.monthly_revenue, app.total_users))

        # Update system metrics
        c.execute("""
            INSERT INTO system_metrics (total_apps, total_revenue, budget_used, budget_remaining)
            VALUES (?, ?, ?, ?)
        """, (
            len(result['deployed_apps']),
            result['total_monthly_revenue'],
            result['total_cost'],
            profit_engine.budget_remaining
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error in profit cycle: {e}")
    finally:
        running_cycle = False

@app.get("/api/cycle/status")
def get_cycle_status():
    """Get current cycle status"""
    return {
        "running": running_cycle,
        "budget_remaining": profit_engine.budget_remaining if profit_engine else 1000
    }

@app.post("/api/apps/{app_id}/scale")
async def scale_app(app_id: str):
    """Scale up a specific app"""
    conn = sqlite3.connect('dashboard.db')
    c = conn.cursor()

    # Simulate scaling
    c.execute("""
        UPDATE apps
        SET monthly_revenue = monthly_revenue * 1.5,
            total_users = total_users * 2
        WHERE id = ?
    """, (app_id,))

    conn.commit()
    conn.close()

    return {"message": f"App {app_id} scaled successfully"}

@app.delete("/api/apps/{app_id}")
def delete_app(app_id: str):
    """Stop/delete an app"""
    conn = sqlite3.connect('dashboard.db')
    c = conn.cursor()

    c.execute("UPDATE apps SET status = 'stopped' WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()

    return {"message": f"App {app_id} stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
