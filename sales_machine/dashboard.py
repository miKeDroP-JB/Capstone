"""
SALES MACHINE DASHBOARD
========================
Real-time monitoring for your AI sales army.

Features:
- Live call status
- Conversion metrics
- Commission tracking
- Lead pipeline view
- Audio playback

Love - Loyalty - Honor - Everybody Eats
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# HTML Template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Machine Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #fff;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }

        .logo {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(90deg, #00f5a0, #00d9f5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(0, 245, 160, 0.1);
            border: 1px solid rgba(0, 245, 160, 0.3);
            border-radius: 20px;
            font-size: 14px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            background: #00f5a0;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            transition: transform 0.3s, border-color 0.3s;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            border-color: rgba(0, 245, 160, 0.5);
        }

        .stat-label {
            font-size: 13px;
            color: rgba(255,255,255,0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(90deg, #fff, #00f5a0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-change {
            font-size: 13px;
            color: #00f5a0;
            margin-top: 8px;
        }

        .stat-change.negative {
            color: #ff6b6b;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }

        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }

        .panel {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .panel-title {
            font-size: 18px;
            font-weight: 600;
        }

        .call-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 400px;
            overflow-y: auto;
        }

        .call-item {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            transition: background 0.3s;
        }

        .call-item:hover {
            background: rgba(255,255,255,0.08);
        }

        .call-status {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .call-status.active {
            background: #00f5a0;
            animation: pulse 1s infinite;
        }

        .call-status.completed {
            background: #4ade80;
        }

        .call-status.failed {
            background: #ff6b6b;
        }

        .call-status.pending {
            background: #fbbf24;
        }

        .call-info {
            flex: 1;
        }

        .call-business {
            font-weight: 600;
            margin-bottom: 4px;
        }

        .call-meta {
            font-size: 13px;
            color: rgba(255,255,255,0.5);
        }

        .call-outcome {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .call-outcome.appointment {
            background: rgba(0, 245, 160, 0.2);
            color: #00f5a0;
        }

        .call-outcome.sale {
            background: rgba(255, 215, 0, 0.2);
            color: #ffd700;
        }

        .call-outcome.callback {
            background: rgba(100, 149, 237, 0.2);
            color: #6495ed;
        }

        .commission-display {
            text-align: center;
            padding: 30px;
        }

        .commission-amount {
            font-size: 48px;
            font-weight: 700;
            background: linear-gradient(90deg, #ffd700, #ff8c00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .commission-label {
            font-size: 14px;
            color: rgba(255,255,255,0.6);
        }

        .pipeline {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .pipeline-stage {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .pipeline-bar {
            flex: 1;
            height: 24px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            overflow: hidden;
        }

        .pipeline-fill {
            height: 100%;
            background: linear-gradient(90deg, #00f5a0, #00d9f5);
            border-radius: 12px;
            transition: width 0.5s ease;
        }

        .pipeline-label {
            width: 100px;
            font-size: 13px;
        }

        .pipeline-count {
            width: 40px;
            text-align: right;
            font-weight: 600;
        }

        .motto {
            text-align: center;
            padding: 30px;
            font-size: 14px;
            color: rgba(255,255,255,0.4);
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 30px;
        }

        .controls {
            display: flex;
            gap: 12px;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary {
            background: linear-gradient(90deg, #00f5a0, #00d9f5);
            color: #000;
        }

        .btn-primary:hover {
            transform: scale(1.05);
        }

        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .btn-secondary:hover {
            background: rgba(255,255,255,0.2);
        }

        .btn-danger {
            background: rgba(255, 107, 107, 0.2);
            color: #ff6b6b;
            border: 1px solid rgba(255, 107, 107, 0.3);
        }

        .btn-danger:hover {
            background: rgba(255, 107, 107, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">SALES MACHINE</div>
            <div class="status-badge">
                <div class="status-dot"></div>
                <span id="status-text">Campaign Active</span>
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Calls</div>
                <div class="stat-value" id="total-calls">0</div>
                <div class="stat-change" id="calls-rate">0 calls/hour</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Connected</div>
                <div class="stat-value" id="connected">0</div>
                <div class="stat-change" id="connect-rate">0% connect rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Appointments</div>
                <div class="stat-value" id="appointments">0</div>
                <div class="stat-change" id="appt-rate">0% conversion</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Revenue</div>
                <div class="stat-value" id="revenue">$0</div>
                <div class="stat-change" id="revenue-rate">+$0 today</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">Live Calls</div>
                    <div class="controls">
                        <button class="btn btn-primary" onclick="startCampaign()">Start</button>
                        <button class="btn btn-secondary" onclick="pauseCampaign()">Pause</button>
                        <button class="btn btn-danger" onclick="stopCampaign()">Stop</button>
                    </div>
                </div>
                <div class="call-list" id="call-list">
                    <!-- Calls will be populated here -->
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div class="panel">
                    <div class="panel-header">
                        <div class="panel-title">Commission</div>
                    </div>
                    <div class="commission-display">
                        <div class="commission-amount" id="commission">$0.00</div>
                        <div class="commission-label">10% of closed deals</div>
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-header">
                        <div class="panel-title">Pipeline</div>
                    </div>
                    <div class="pipeline" id="pipeline">
                        <!-- Pipeline stages -->
                    </div>
                </div>
            </div>
        </div>

        <div class="motto">
            Love - Loyalty - Honor - Everybody Eats
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        let ws;

        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };

            ws.onclose = function() {
                setTimeout(connectWebSocket, 3000);
            };
        }

        function updateDashboard(data) {
            // Update stats
            document.getElementById('total-calls').textContent = data.stats.calls_made || 0;
            document.getElementById('connected').textContent = data.stats.calls_connected || 0;
            document.getElementById('appointments').textContent = data.stats.appointments_set || 0;
            document.getElementById('revenue').textContent = '$' + (data.stats.total_revenue || 0).toLocaleString();
            document.getElementById('commission').textContent = '$' + (data.stats.total_commission || 0).toFixed(2);

            // Update rates
            const connectRate = data.stats.calls_made > 0
                ? ((data.stats.calls_connected / data.stats.calls_made) * 100).toFixed(1)
                : 0;
            document.getElementById('connect-rate').textContent = connectRate + '% connect rate';

            const convRate = data.stats.calls_connected > 0
                ? ((data.stats.appointments_set / data.stats.calls_connected) * 100).toFixed(1)
                : 0;
            document.getElementById('appt-rate').textContent = convRate + '% conversion';

            // Update call list
            updateCallList(data.active_calls || [], data.recent_calls || []);

            // Update pipeline
            updatePipeline(data.pipeline || {});

            // Update status
            document.getElementById('status-text').textContent =
                data.status === 'calling' ? 'Campaign Active' :
                data.status === 'paused' ? 'Paused' :
                data.status === 'idle' ? 'Ready' : data.status;
        }

        function updateCallList(activeCalls, recentCalls) {
            const list = document.getElementById('call-list');
            list.innerHTML = '';

            // Active calls first
            activeCalls.forEach(call => {
                list.innerHTML += createCallItem(call, 'active');
            });

            // Recent calls
            recentCalls.slice(0, 10).forEach(call => {
                list.innerHTML += createCallItem(call, call.outcome);
            });

            if (activeCalls.length === 0 && recentCalls.length === 0) {
                list.innerHTML = '<div style="text-align: center; color: rgba(255,255,255,0.4); padding: 40px;">No calls yet. Start the campaign!</div>';
            }
        }

        function createCallItem(call, status) {
            const statusClass = status === 'active' ? 'active' :
                               status === 'appointment' || status === 'sale' ? 'completed' :
                               status === 'failed' || status === 'no_answer' ? 'failed' : 'pending';

            const outcome = status === 'active' ? '' :
                           status === 'appointment' ? '<span class="call-outcome appointment">Appointment</span>' :
                           status === 'sale' ? '<span class="call-outcome sale">Sale!</span>' :
                           status === 'callback' ? '<span class="call-outcome callback">Callback</span>' : '';

            return `
                <div class="call-item">
                    <div class="call-status ${statusClass}"></div>
                    <div class="call-info">
                        <div class="call-business">${call.business_name || 'Unknown'}</div>
                        <div class="call-meta">${call.phone || ''} • ${call.duration || '0:00'}</div>
                    </div>
                    ${outcome}
                </div>
            `;
        }

        function updatePipeline(pipeline) {
            const container = document.getElementById('pipeline');
            const stages = [
                { key: 'new', label: 'New Leads' },
                { key: 'contacted', label: 'Contacted' },
                { key: 'qualified', label: 'Qualified' },
                { key: 'appointment_set', label: 'Appointments' },
                { key: 'closed_won', label: 'Closed Won' }
            ];

            const total = Object.values(pipeline).reduce((a, b) => a + b, 1);

            container.innerHTML = stages.map(stage => {
                const count = pipeline[stage.key] || 0;
                const pct = (count / total) * 100;
                return `
                    <div class="pipeline-stage">
                        <div class="pipeline-label">${stage.label}</div>
                        <div class="pipeline-bar">
                            <div class="pipeline-fill" style="width: ${pct}%"></div>
                        </div>
                        <div class="pipeline-count">${count}</div>
                    </div>
                `;
            }).join('');
        }

        function startCampaign() {
            fetch('/api/campaign/start', { method: 'POST' });
        }

        function pauseCampaign() {
            fetch('/api/campaign/pause', { method: 'POST' });
        }

        function stopCampaign() {
            fetch('/api/campaign/stop', { method: 'POST' });
        }

        // Initialize
        connectWebSocket();

        // Fallback polling if WebSocket fails
        setInterval(() => {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                fetch('/api/stats')
                    .then(r => r.json())
                    .then(updateDashboard)
                    .catch(() => {});
            }
        }, 5000);
    </script>
</body>
</html>
"""


class Dashboard:
    """
    Real-time web dashboard for Sales Machine.
    Uses FastAPI + WebSockets for live updates.
    """

    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.clients: List[Any] = []

    def create_app(self):
        """Create the FastAPI application"""
        try:
            from fastapi import FastAPI, WebSocket, WebSocketDisconnect
            from fastapi.responses import HTMLResponse
        except ImportError:
            raise RuntimeError("Install FastAPI: pip install fastapi uvicorn")

        app = FastAPI(title="Sales Machine Dashboard")

        @app.get("/", response_class=HTMLResponse)
        async def get_dashboard():
            return DASHBOARD_HTML

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.clients.append(websocket)

            try:
                while True:
                    # Send updates every second
                    data = self._get_dashboard_data()
                    await websocket.send_json(data)
                    await asyncio.sleep(1)
            except WebSocketDisconnect:
                self.clients.remove(websocket)

        @app.get("/api/stats")
        async def get_stats():
            return self._get_dashboard_data()

        @app.post("/api/campaign/start")
        async def start_campaign():
            if self.orchestrator:
                asyncio.create_task(self.orchestrator.start_calling())
            return {"status": "started"}

        @app.post("/api/campaign/pause")
        async def pause_campaign():
            if self.orchestrator:
                await self.orchestrator.pause()
            return {"status": "paused"}

        @app.post("/api/campaign/stop")
        async def stop_campaign():
            if self.orchestrator:
                await self.orchestrator.stop()
            return {"status": "stopped"}

        return app

    def _get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        if not self.orchestrator:
            return self._get_demo_data()

        stats = self.orchestrator.get_stats()
        crm = self.orchestrator.crm

        # Get active calls
        active_calls = [
            {
                "business_name": self.orchestrator.crm.leads.get(call.lead_id, {}).get("business_name", "Unknown"),
                "phone": call.to_number,
                "duration": self._format_duration(call.duration or 0)
            }
            for call in self.orchestrator.active_calls.values()
        ]

        # Get recent calls
        recent_calls = [
            {
                "business_name": crm.leads.get(log.lead_id, {}).business_name if hasattr(crm.leads.get(log.lead_id, {}), 'business_name') else "Unknown",
                "phone": "",
                "duration": self._format_duration(log.duration),
                "outcome": log.outcome
            }
            for log in list(crm.call_logs)[-20:]
        ]

        # Get pipeline
        pipeline = crm.get_analytics().get("pipeline", {})

        return {
            "status": self.orchestrator.status.value,
            "stats": stats,
            "active_calls": active_calls,
            "recent_calls": recent_calls,
            "pipeline": pipeline
        }

    def _get_demo_data(self) -> Dict[str, Any]:
        """Demo data for testing without orchestrator"""
        import random

        return {
            "status": "calling",
            "stats": {
                "calls_made": random.randint(50, 100),
                "calls_connected": random.randint(30, 60),
                "appointments_set": random.randint(5, 15),
                "total_revenue": random.randint(10000, 50000),
                "total_commission": random.randint(1000, 5000)
            },
            "active_calls": [
                {"business_name": "Cool Air HVAC", "phone": "+1 555-0001", "duration": "1:23"},
                {"business_name": "Texas Heat Solutions", "phone": "+1 555-0002", "duration": "0:45"},
            ],
            "recent_calls": [
                {"business_name": "Comfort Zone AC", "outcome": "appointment", "duration": "3:45"},
                {"business_name": "Arctic Systems", "outcome": "callback", "duration": "2:10"},
                {"business_name": "Gulf Cooling", "outcome": "sale", "duration": "5:30"},
            ],
            "pipeline": {
                "new": 45,
                "contacted": 32,
                "qualified": 18,
                "appointment_set": 8,
                "closed_won": 3
            }
        }

    def _format_duration(self, seconds: int) -> str:
        """Format seconds as M:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"

    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast update to all connected clients"""
        for client in self.clients:
            try:
                await client.send_json(data)
            except:
                pass

    def run(self, host: str = "0.0.0.0", port: int = 8888):
        """Run the dashboard server"""
        import uvicorn
        app = self.create_app()
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║              SALES MACHINE DASHBOARD                      ║
║                                                           ║
║   Open in browser: http://localhost:{port}                 ║
║                                                           ║
║   Love - Loyalty - Honor - Everybody Eats                 ║
╚═══════════════════════════════════════════════════════════╝
        """)
        uvicorn.run(app, host=host, port=port)


def main():
    """Run dashboard standalone for testing"""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
