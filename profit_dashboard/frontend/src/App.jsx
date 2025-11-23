import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [systemStats, setSystemStats] = useState(null);
  const [apps, setApps] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [cycleStatus, setCycleStatus] = useState({ running: false });
  const [numApps, setNumApps] = useState(3);
  const [loading, setLoading] = useState(false);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [stats, appsData, status] = await Promise.all([
        fetch(`${API_URL}/api/stats/system`).then(r => r.json()),
        fetch(`${API_URL}/api/apps`).then(r => r.json()),
        fetch(`${API_URL}/api/cycle/status`).then(r => r.json())
      ]);

      setSystemStats(stats);
      setApps(appsData);
      setCycleStatus(status);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const loadOpportunities = async () => {
    try {
      const data = await fetch(`${API_URL}/api/opportunities`).then(r => r.json());
      setOpportunities(data);
    } catch (error) {
      console.error('Error loading opportunities:', error);
    }
  };

  const startCycle = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/api/cycle/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_apps: numApps, auto_scale: true })
      });
      setTimeout(loadData, 2000);
    } catch (error) {
      console.error('Error starting cycle:', error);
    } finally {
      setLoading(false);
    }
  };

  const scaleApp = async (appId) => {
    try {
      await fetch(`${API_URL}/api/apps/${appId}/scale`, { method: 'POST' });
      loadData();
    } catch (error) {
      console.error('Error scaling app:', error);
    }
  };

  const stopApp = async (appId) => {
    if (!window.confirm('Stop this app?')) return;
    try {
      await fetch(`${API_URL}/api/apps/${appId}`, { method: 'DELETE' });
      loadData();
    } catch (error) {
      console.error('Error stopping app:', error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="App">
      <header className="header">
        <h1>💰 Profit Engine Dashboard</h1>
        <p className="tagline">Real-time monitoring and control</p>
      </header>

      {/* System Stats */}
      {systemStats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Revenue</div>
            <div className="stat-value green">{formatCurrency(systemStats.total_revenue)}/mo</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Active Apps</div>
            <div className="stat-value blue">{systemStats.total_apps}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Budget Used</div>
            <div className="stat-value orange">{formatCurrency(systemStats.budget_used)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">ROI</div>
            <div className="stat-value purple">{systemStats.roi_percentage.toFixed(0)}%</div>
          </div>
        </div>
      )}

      {/* Control Panel */}
      <div className="control-panel">
        <h2>🎮 Control Panel</h2>
        <div className="controls">
          <div className="control-group">
            <label>Number of Apps:</label>
            <input
              type="number"
              min="1"
              max="10"
              value={numApps}
              onChange={(e) => setNumApps(parseInt(e.target.value))}
              disabled={cycleStatus.running}
            />
          </div>
          <button
            className="btn btn-primary"
            onClick={startCycle}
            disabled={cycleStatus.running || loading}
          >
            {cycleStatus.running ? '🔄 Cycle Running...' : '🚀 Start Profit Cycle'}
          </button>
          <button
            className="btn btn-secondary"
            onClick={loadOpportunities}
            disabled={loading}
          >
            🔍 View Opportunities
          </button>
        </div>
        {cycleStatus.running && (
          <div className="status-message running">
            ⚡ Profit cycle in progress... Building and deploying apps
          </div>
        )}
        {cycleStatus.budget_remaining !== undefined && (
          <div className="budget-bar">
            <div className="budget-label">
              Budget Remaining: {formatCurrency(cycleStatus.budget_remaining)}
            </div>
            <div className="budget-track">
              <div
                className="budget-fill"
                style={{ width: `${(cycleStatus.budget_remaining / 1000) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Opportunities */}
      {opportunities.length > 0 && (
        <div className="opportunities-section">
          <h2>🎯 Market Opportunities</h2>
          <div className="opportunities-grid">
            {opportunities.map(opp => (
              <div key={opp.id} className="opportunity-card">
                <div className="opp-header">
                  <h3>{opp.niche}</h3>
                  <span className={`profit-score score-${Math.floor(opp.profit_score / 20)}`}>
                    {opp.profit_score}/100
                  </span>
                </div>
                <p className="opp-description">{opp.description}</p>
                <div className="opp-details">
                  <div className="opp-detail">
                    <span className="label">Revenue:</span>
                    <span className="value">{formatCurrency(opp.estimated_monthly_revenue)}/mo</span>
                  </div>
                  <div className="opp-detail">
                    <span className="label">Strategy:</span>
                    <span className="value">{opp.monetization_strategy}</span>
                  </div>
                  <div className="opp-detail">
                    <span className="label">Difficulty:</span>
                    <span className="value">{opp.difficulty}</span>
                  </div>
                  <div className="opp-detail">
                    <span className="label">Time:</span>
                    <span className="value">{opp.time_to_market} days</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Apps List */}
      <div className="apps-section">
        <h2>🚀 Deployed Apps</h2>
        {apps.length === 0 ? (
          <div className="empty-state">
            <p>No apps deployed yet. Start a profit cycle to begin!</p>
          </div>
        ) : (
          <div className="apps-grid">
            {apps.map(app => (
              <div key={app.id} className={`app-card ${app.status}`}>
                <div className="app-header">
                  <h3>{app.name}</h3>
                  <span className={`status-badge ${app.status}`}>
                    {app.status}
                  </span>
                </div>
                <div className="app-niche">{app.niche}</div>
                <div className="app-stats">
                  <div className="app-stat">
                    <div className="stat-label">Revenue</div>
                    <div className="stat-value">{formatCurrency(app.monthly_revenue)}/mo</div>
                  </div>
                  <div className="app-stat">
                    <div className="stat-label">Users</div>
                    <div className="stat-value">{app.total_users}</div>
                  </div>
                </div>
                <div className="app-url">
                  <a href={app.url} target="_blank" rel="noopener noreferrer">
                    {app.url}
                  </a>
                </div>
                <div className="app-actions">
                  <button
                    className="btn btn-scale"
                    onClick={() => scaleApp(app.id)}
                    disabled={app.status !== 'active'}
                  >
                    📈 Scale
                  </button>
                  <button
                    className="btn btn-stop"
                    onClick={() => stopApp(app.id)}
                    disabled={app.status !== 'active'}
                  >
                    ⏸️ Stop
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
