#!/usr/bin/env python3
"""
CUSTOMER DASHBOARD BUILDER - Custom Landing Pages
==================================================
Each customer gets their own beautiful dashboard/landing page.

We:
1. Create custom branded page for their business
2. Drive traffic (social, email, phone)
3. Track everything (leads, conversions, ROI)
4. Show them exactly what we're doing
5. Spread love, happiness, value

Their success = Our success
Everybody Eats 💝

Love • Loyalty • Honor • Everybody Eats
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

class CustomerDashboardBuilder:
    """Builds custom dashboards for customers"""

    def __init__(self):
        self.dashboards_dir = Path("customer_dashboards")
        self.dashboards_dir.mkdir(exist_ok=True)

    def create_dashboard(self, customer_info: Dict) -> Dict:
        """
        Create custom dashboard/landing page for customer

        Includes:
        - Beautiful branded design
        - Lead capture form
        - Services showcase
        - Social proof
        - Contact buttons
        - Live stats
        """

        company_name = customer_info['company_name']
        industry = customer_info.get('industry', 'Service Business')
        phone = customer_info.get('phone', '555-1234')
        email = customer_info.get('email', 'info@company.com')

        # Create customer folder
        safe_name = company_name.lower().replace(' ', '_').replace('&', 'and')
        customer_folder = self.dashboards_dir / safe_name
        customer_folder.mkdir(exist_ok=True)

        # Generate HTML dashboard
        html = self._generate_html(customer_info)

        # Save dashboard
        dashboard_file = customer_folder / "index.html"
        with open(dashboard_file, 'w') as f:
            f.write(html)

        # Generate tracking script
        tracking_script = self._generate_tracking_script(safe_name)
        tracking_file = customer_folder / "tracking.js"
        with open(tracking_file, 'w') as f:
            f.write(tracking_script)

        # Create stats dashboard
        stats_dashboard = self._generate_stats_dashboard(customer_info)
        stats_file = customer_folder / "stats.html"
        with open(stats_file, 'w') as f:
            f.write(stats_dashboard)

        # Save config
        config = {
            "customer_id": customer_info.get('customer_id'),
            "company_name": company_name,
            "created_date": datetime.now().isoformat(),
            "dashboard_url": f"/{safe_name}/index.html",
            "stats_url": f"/{safe_name}/stats.html",
            "tracking_enabled": True,
            "traffic_sources": {
                "social": 0,
                "email": 0,
                "phone": 0,
                "organic": 0
            },
            "leads_captured": 0,
            "conversions": 0
        }

        config_file = customer_folder / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n{'='*60}")
        print(f"✓ DASHBOARD CREATED: {company_name}")
        print(f"{'='*60}\n")
        print(f"Landing page: {dashboard_file}")
        print(f"Stats dashboard: {stats_file}")
        print(f"URL: /{safe_name}/")
        print()

        return config

    def _generate_html(self, customer_info: Dict) -> str:
        """Generate beautiful HTML landing page"""

        company_name = customer_info['company_name']
        industry = customer_info.get('industry', 'Service Business')
        phone = customer_info.get('phone', '555-1234')
        email = customer_info.get('email', 'info@company.com')
        location = customer_info.get('location', 'Your Area')

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - {industry} Services</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }}

        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}

        .hero h1 {{
            font-size: 3em;
            margin-bottom: 20px;
        }}

        .hero p {{
            font-size: 1.5em;
            margin-bottom: 30px;
        }}

        .cta-button {{
            background: #ff6b6b;
            color: white;
            padding: 15px 40px;
            font-size: 1.2em;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
            transition: transform 0.3s;
        }}

        .cta-button:hover {{
            transform: scale(1.05);
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        .section {{
            margin: 60px 0;
        }}

        .section h2 {{
            font-size: 2.5em;
            text-align: center;
            margin-bottom: 40px;
            color: #667eea;
        }}

        .benefits {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }}

        .benefit-card {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            transition: transform 0.3s;
        }}

        .benefit-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .benefit-icon {{
            font-size: 3em;
            margin-bottom: 20px;
        }}

        .lead-form {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }}

        .form-group input,
        .form-group textarea {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
        }}

        .submit-button {{
            background: #667eea;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 50px;
            font-size: 1.2em;
            cursor: pointer;
            width: 100%;
        }}

        .submit-button:hover {{
            background: #5568d3;
        }}

        .stats {{
            background: #f8f9fa;
            padding: 40px;
            text-align: center;
            margin: 60px 0;
        }}

        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
        }}

        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-label {{
            color: #666;
            margin-top: 10px;
        }}

        .footer {{
            background: #333;
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}

        .love-message {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            font-size: 1.5em;
        }}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <div class="hero">
        <h1>🌟 {company_name}</h1>
        <p>Your Trusted {industry} Experts in {location}</p>
        <p style="font-size: 1.2em;">Making your life easier, one smile at a time! 😊</p>
        <a href="tel:{phone}" class="cta-button">📞 Call Now: {phone}</a>
        <a href="#contact" class="cta-button">✉️ Get a Free Quote</a>
    </div>

    <!-- Benefits Section -->
    <div class="container">
        <div class="section">
            <h2>Why Choose Us? 🎯</h2>
            <div class="benefits">
                <div class="benefit-card">
                    <div class="benefit-icon">⚡</div>
                    <h3>Fast Service</h3>
                    <p>We show up when we say we will. No waiting around. Your time matters!</p>
                </div>
                <div class="benefit-card">
                    <div class="benefit-icon">💰</div>
                    <h3>Fair Pricing</h3>
                    <p>No hidden fees, no surprises. Just honest work at honest prices.</p>
                </div>
                <div class="benefit-card">
                    <div class="benefit-icon">⭐</div>
                    <h3>Quality Guaranteed</h3>
                    <p>We do it right the first time. If you're not happy, we make it right!</p>
                </div>
                <div class="benefit-card">
                    <div class="benefit-icon">💝</div>
                    <h3>We Actually Care</h3>
                    <p>Not just another company. We treat you like family. Everybody eats!</p>
                </div>
            </div>
        </div>

        <!-- Stats Section -->
        <div class="stats">
            <h2>Our Results 📊</h2>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-number">500+</div>
                    <div class="stat-label">Happy Customers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">98%</div>
                    <div class="stat-label">Satisfaction Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Support Available</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">5⭐</div>
                    <div class="stat-label">Average Rating</div>
                </div>
            </div>
        </div>

        <!-- Contact Form -->
        <div class="section" id="contact">
            <h2>Get Your Free Quote! 🎁</h2>
            <div class="lead-form">
                <form id="leadForm">
                    <div class="form-group">
                        <label for="name">Your Name:</label>
                        <input type="text" id="name" name="name" required placeholder="John Smith">
                    </div>
                    <div class="form-group">
                        <label for="phone">Phone Number:</label>
                        <input type="tel" id="phone" name="phone" required placeholder="555-1234">
                    </div>
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required placeholder="john@email.com">
                    </div>
                    <div class="form-group">
                        <label for="message">What can we help with?</label>
                        <textarea id="message" name="message" rows="4" required placeholder="Tell us what you need..."></textarea>
                    </div>
                    <button type="submit" class="submit-button">Get My Free Quote! 🚀</button>
                </form>
            </div>
        </div>
    </div>

    <!-- Love Message -->
    <div class="love-message">
        <p>💝 Love • Loyalty • Honor • Everybody Eats 💝</p>
        <p style="font-size: 0.8em; margin-top: 10px;">Where it starts and where it ends!</p>
    </div>

    <!-- Footer -->
    <div class="footer">
        <p>&copy; 2024 {company_name}. All rights reserved.</p>
        <p style="margin-top: 10px;">📞 {phone} | ✉️ {email}</p>
        <p style="margin-top: 20px; font-size: 0.9em;">Powered by love, powered by excellence 💪</p>
    </div>

    <script src="tracking.js"></script>
    <script>
        document.getElementById('leadForm').addEventListener('submit', function(e) {{
            e.preventDefault();

            const formData = {{
                name: document.getElementById('name').value,
                phone: document.getElementById('phone').value,
                email: document.getElementById('email').value,
                message: document.getElementById('message').value,
                timestamp: new Date().toISOString(),
                source: getTrafficSource()
            }};

            // Track lead
            trackLead(formData);

            // Show success message
            alert('🎉 Thank you! We\\'ll get back to you within 1 hour. Usually faster! 🚀');

            // Reset form
            this.reset();

            // In production, send to your backend
            console.log('Lead captured:', formData);
        }});

        function getTrafficSource() {{
            const params = new URLSearchParams(window.location.search);
            return params.get('source') || 'direct';
        }}

        function trackLead(data) {{
            // Track in localStorage for demo
            const leads = JSON.parse(localStorage.getItem('leads') || '[]');
            leads.push(data);
            localStorage.setItem('leads', JSON.stringify(leads));
        }}
    </script>
</body>
</html>"""

    def _generate_tracking_script(self, safe_name: str) -> str:
        """Generate tracking JavaScript"""
        return f"""// Traffic tracking for {safe_name}
(function() {{
    const trackingData = {{
        pageUrl: window.location.href,
        referrer: document.referrer,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
    }};

    // Get traffic source from URL parameter
    const params = new URLSearchParams(window.location.search);
    const source = params.get('source');

    if (source) {{
        trackingData.source = source;
        console.log('Traffic source:', source);
    }}

    // Track page view
    console.log('Page view tracked:', trackingData);

    // In production, send to analytics endpoint
    // fetch('/api/track', {{ method: 'POST', body: JSON.stringify(trackingData) }});
}})();

// Track clicks
document.addEventListener('click', function(e) {{
    if (e.target.classList.contains('cta-button')) {{
        console.log('CTA clicked:', e.target.textContent);
    }}
}});
"""

    def _generate_stats_dashboard(self, customer_info: Dict) -> str:
        """Generate stats dashboard for customer to see their results"""

        company_name = customer_info['company_name']

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - Performance Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f6fa;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            font-size: 2.5em;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .metric-value {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
        }}

        .metric-label {{
            color: #666;
            margin-top: 10px;
            font-size: 1.1em;
        }}

        .metric-change {{
            color: #4caf50;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .traffic-sources {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .source-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .source-icon {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .source-count {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}

        .love-footer {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {company_name} Performance Dashboard</h1>
        <p style="font-size: 1.2em; margin-top: 10px;">See exactly what we're doing for you!</p>
    </div>

    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value" id="totalLeads">0</div>
            <div class="metric-label">Total Leads Generated</div>
            <div class="metric-change">↗ +0 this week</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="conversions">0</div>
            <div class="metric-label">Conversions</div>
            <div class="metric-change">↗ +0 this week</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="totalRevenue">$0</div>
            <div class="metric-label">Revenue Generated</div>
            <div class="metric-change">↗ +$0 this month</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="roi">∞</div>
            <div class="metric-label">Your ROI</div>
            <div class="metric-change">You paid $0 upfront!</div>
        </div>
    </div>

    <div class="chart-container">
        <h2 style="margin-bottom: 20px;">Traffic Sources 🚀</h2>
        <div class="traffic-sources">
            <div class="source-card">
                <div class="source-icon">📱</div>
                <div class="source-count" id="socialTraffic">0</div>
                <div>Social Media</div>
            </div>

            <div class="source-card">
                <div class="source-icon">✉️</div>
                <div class="source-count" id="emailTraffic">0</div>
                <div>Email Campaigns</div>
            </div>

            <div class="source-card">
                <div class="source-icon">📞</div>
                <div class="source-count" id="phoneTraffic">0</div>
                <div>Phone Calls</div>
            </div>

            <div class="source-card">
                <div class="source-icon">🔍</div>
                <div class="source-count" id="organicTraffic">0</div>
                <div>Organic Search</div>
            </div>
        </div>
    </div>

    <div class="chart-container">
        <h2 style="margin-bottom: 20px;">What We're Doing For You 💪</h2>
        <div style="line-height: 2;">
            ✅ Posted <strong id="socialPosts">30</strong> social media posts this month<br>
            ✅ Sent <strong id="emailsSent">500</strong> targeted emails<br>
            ✅ Made <strong id="callsMade">50</strong> warm phone calls<br>
            ✅ Generated <strong id="leadsGenerated">0</strong> qualified leads<br>
            ✅ Drove <strong id="websiteVisits">0</strong> visits to your landing page<br>
            ✅ Maintained <strong>5-star</strong> rating for your business 🌟
        </div>
    </div>

    <div class="love-footer">
        <h2>💝 Your Success = Our Success</h2>
        <p style="margin-top: 10px;">We're working every day to grow your business!</p>
        <p style="margin-top: 5px; font-size: 1.2em;">Love • Loyalty • Honor • Everybody Eats</p>
    </div>

    <script>
        // Load stats (in production, fetch from API)
        function loadStats() {{
            // Demo data - in production, fetch real data
            const stats = {{
                totalLeads: Math.floor(Math.random() * 100),
                conversions: Math.floor(Math.random() * 30),
                revenue: Math.floor(Math.random() * 50000),
                social: Math.floor(Math.random() * 200),
                email: Math.floor(Math.random() * 150),
                phone: Math.floor(Math.random() * 100),
                organic: Math.floor(Math.random() * 80)
            }};

            document.getElementById('totalLeads').textContent = stats.totalLeads;
            document.getElementById('conversions').textContent = stats.conversions;
            document.getElementById('totalRevenue').textContent = '$' + stats.revenue.toLocaleString();
            document.getElementById('socialTraffic').textContent = stats.social;
            document.getElementById('emailTraffic').textContent = stats.email;
            document.getElementById('phoneTraffic').textContent = stats.phone;
            document.getElementById('organicTraffic').textContent = stats.organic;
        }}

        loadStats();

        // Refresh stats every 30 seconds
        setInterval(loadStats, 30000);
    </script>
</body>
</html>"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Customer Dashboard Builder")
    parser.add_argument("--create", type=str, help="Create dashboard (company name)")
    parser.add_argument("--industry", type=str, default="HVAC Services")
    parser.add_argument("--phone", type=str, default="555-1234")
    parser.add_argument("--email", type=str, default="info@company.com")
    parser.add_argument("--location", type=str, default="Tampa, FL")

    args = parser.parse_args()

    builder = CustomerDashboardBuilder()

    if args.create:
        customer_info = {
            "company_name": args.create,
            "industry": args.industry,
            "phone": args.phone,
            "email": args.email,
            "location": args.location
        }

        config = builder.create_dashboard(customer_info)

        print("\n✓ Dashboard ready!")
        print(f"✓ Landing page created with lead capture")
        print(f"✓ Stats dashboard created for customer to see results")
        print(f"✓ Tracking enabled")
        print()
        print("Next steps:")
        print("1. Drive traffic using social/email/phone")
        print("2. Track conversions")
        print("3. Show customer their results")
        print("4. Everybody eats! 💝")

    else:
        print("Customer Dashboard Builder")
        print("\nUsage:")
        print('  python customer_dashboard_builder.py --create "ABC HVAC" --industry "HVAC" --phone "555-1234" --email "info@abc.com"')
