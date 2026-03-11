"""
IntentScope Live Preview Web Application
A real-time dashboard showing the AI-powered behavioral analytics system
"""

from flask import Flask, render_template, jsonify, request
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import time

app = Flask(__name__)

# Sample data generators
def generate_live_users():
    """Generate live user data for the dashboard"""
    users = []
    user_types = ['Builder', 'Explorer', 'Learner', 'Abandoner']
    
    for i in range(50):
        user = {
            'id': i + 1,
            'name': f'User_{i+1:03d}',
            'type': random.choice(user_types),
            'interactions': random.randint(1, 100),
            'success_rate': round(random.uniform(0.3, 1.0), 2),
            'churn_risk': round(random.uniform(0.1, 0.9), 2),
            'last_active': (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat(),
            'is_anomaly': random.random() < 0.05,
            'segment': random.choice(['Premium', 'Regular', 'New', 'At-Risk'])
        }
        users.append(user)
    
    return users

def generate_metrics():
    """Generate real-time metrics"""
    return {
        'total_users': random.randint(4500, 5500),
        'active_users': random.randint(800, 1200),
        'avg_success_rate': round(random.uniform(0.75, 0.90), 3),
        'churn_rate': round(random.uniform(0.05, 0.15), 3),
        'anomalies_detected': random.randint(10, 50),
        'predictions_made': random.randint(1000, 5000),
        'recommendations_served': random.randint(500, 2000),
        'timestamp': datetime.now().isoformat()
    }

def generate_intention_distribution():
    """Generate intention class distribution"""
    total = 1000
    return {
        'Builder': random.randint(200, 350),
        'Explorer': random.randint(150, 300),
        'Learner': random.randint(200, 400),
        'Abandoner': random.randint(50, 150)
    }

def generate_feature_importance():
    """Generate feature importance data"""
    features = [
        'successful_actions', 'overall_success_rate', 'advanced_premium_usage',
        'total_interactions', 'unique_actions', 'session_duration_mean',
        'action_diversity_ratio', 'days_active', 'login_count', 'complete_sessions'
    ]
    
    importance = {f: round(random.uniform(0.01, 0.5), 4) for f in features}
    total = sum(importance.values())
    return {k: round(v/total, 4) for k, v in importance.items()}

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IntentScope - Live AI Analytics Preview</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .live-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(0,0,0,0.3);
            padding: 8px 16px;
            border-radius: 20px;
        }
        
        .pulse {
            width: 12px;
            height: 12px;
            background: #00ff88;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.3); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .container {
            padding: 30px 40px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #aaa;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .metric-change {
            font-size: 0.85rem;
            margin-top: 5px;
        }
        
        .positive { color: #00ff88; }
        .negative { color: #ff4757; }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .chart-card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .chart-card h3 {
            margin-bottom: 20px;
            color: #e0e0e0;
            font-size: 1.1rem;
        }
        
        .users-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .users-table th, .users-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .users-table th {
            background: rgba(255,255,255,0.1);
            font-weight: 600;
        }
        
        .users-table tr:hover {
            background: rgba(255,255,255,0.05);
        }
        
        .type-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .type-Builder { background: #00d9ff; color: #000; }
        .type-Explorer { background: #a55eea; color: #fff; }
        .type-Learner { background: #ffa502; color: #000; }
        .type-Abandoner { background: #ff4757; color: #fff; }
        
        .risk-high { color: #ff4757; }
        .risk-medium { color: #ffa502; }
        .risk-low { color: #00ff88; }
        
        .anomaly-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #ff4757;
            display: inline-block;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            50% { opacity: 0.3; }
        }
        
        .refresh-btn {
            background: linear-gradient(90deg, #667eea, #764ba2);
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: transform 0.2s;
        }
        
        .refresh-btn:hover {
            transform: scale(1.05);
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 IntentScope - Live AI Analytics</h1>
        <div class="live-indicator">
            <div class="pulse"></div>
            <span>LIVE</span>
        </div>
    </div>
    
    <div class="container">
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Users</div>
                <div class="metric-value" id="totalUsers">-</div>
                <div class="metric-change positive">↑ 12% this week</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Active Users</div>
                <div class="metric-value" id="activeUsers">-</div>
                <div class="metric-change positive">↑ 8% this week</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Success Rate</div>
                <div class="metric-value" id="successRate">-</div>
                <div class="metric-change positive">↑ 5% this week</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Churn Rate</div>
                <div class="metric-value" id="churnRate">-</div>
                <div class="metric-change negative">↓ 2% this week</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Anomalies Detected</div>
                <div class="metric-value" id="anomalies">-</div>
                <div class="metric-change">Real-time monitoring</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Predictions Made</div>
                <div class="metric-value" id="predictions">-</div>
                <div class="metric-change">Today</div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="chart-card">
                <h3>📊 Intention Distribution</h3>
                <canvas id="intentionChart" height="200"></canvas>
            </div>
            <div class="chart-card">
                <h3>📈 Feature Importance</h3>
                <canvas id="featureChart" height="200"></canvas>
            </div>
            <div class="chart-card">
                <h3>👥 Live User Activity</h3>
                <canvas id="activityChart" height="200"></canvas>
            </div>
            <div class="chart-card">
                <h3>🎯 User Segments</h3>
                <canvas id="segmentChart" height="200"></canvas>
            </div>
        </div>
        
        <div class="chart-card">
            <h3>👤 Recent User Activity (Live Feed)</h3>
            <table class="users-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Interactions</th>
                        <th>Success Rate</th>
                        <th>Churn Risk</th>
                        <th>Last Active</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="usersTable">
                </tbody>
            </table>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
        </div>
    </div>
    
    <div class="footer">
        IntentScope AI Analytics Platform | Powered by TensorFlow & scikit-learn
    </div>
    
    <script>
        let intentionChart, featureChart, activityChart, segmentChart;
        
        function initCharts(intentionData, featureData, activityData, segmentData) {
            // Intention Distribution Chart
            const intentionCtx = document.getElementById('intentionChart').getContext('2d');
            intentionChart = new Chart(intentionCtx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(intentionData),
                    datasets: [{
                        data: Object.values(intentionData),
                        backgroundColor: ['#00d9ff', '#a55eea', '#ffa502', '#ff4757'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#fff' } }
                    }
                }
            });
            
            // Feature Importance Chart
            const featureCtx = document.getElementById('featureChart').getContext('2d');
            const sortedFeatures = Object.entries(featureData).sort((a, b) => b[1] - a[1]).slice(0, 8);
            featureChart = new Chart(featureCtx, {
                type: 'bar',
                data: {
                    labels: sortedFeatures.map(f => f[0].replace('_', ' ')),
                    datasets: [{
                        label: 'Importance',
                        data: sortedFeatures.map(f => f[1]),
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { color: '#aaa' }, grid: { display: false } },
                        y: { ticks: { color: '#aaa' }, grid: { color: 'rgba(255,255,255,0.1)' } }
                    }
                }
            });
            
            // Activity Chart
            const activityCtx = document.getElementById('activityChart').getContext('2d');
            activityChart = new Chart(activityCtx, {
                type: 'line',
                data: {
                    labels: activityData.labels,
                    datasets: [{
                        label: 'Active Users',
                        data: activityData.values,
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { color: '#aaa' }, grid: { display: false } },
                        y: { ticks: { color: '#aaa' }, grid: { color: 'rgba(255,255,255,0.1)' } }
                    }
                }
            });
            
            // Segment Chart
            const segmentCtx = document.getElementById('segmentChart').getContext('2d');
            segmentChart = new Chart(segmentCtx, {
                type: 'pie',
                data: {
                    labels: Object.keys(segmentData),
                    datasets: [{
                        data: Object.values(segmentData),
                        backgroundColor: ['#667eea', '#00d9ff', '#00ff88', '#ffa502'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#fff' } }
                    }
                }
            });
        }
        
        function updateCharts(intentionData, featureData, activityData, segmentData) {
            intentionChart.data.datasets[0].data = Object.values(intentionData);
            intentionChart.update();
            
            const sortedFeatures = Object.entries(featureData).sort((a, b) => b[1] - a[1]).slice(0, 8);
            featureChart.data.labels = sortedFeatures.map(f => f[0].replace('_', ' '));
            featureChart.data.datasets[0].data = sortedFeatures.map(f => f[1]);
            featureChart.update();
            
            activityChart.data.datasets[0].data = activityData.values;
            activityChart.update();
            
            segmentChart.data.datasets[0].data = Object.values(segmentData);
            segmentChart.update();
        }
        
        function getRiskClass(risk) {
            if (risk >= 0.7) return 'risk-high';
            if (risk >= 0.4) return 'risk-medium';
            return 'risk-low';
        }
        
        function formatTime(isoString) {
            const date = new Date(isoString);
            const now = new Date();
            const diff = Math.floor((now - date) / 60000);
            if (diff < 60) return `${diff}m ago`;
            if (diff < 1440) return `${Math.floor(diff/60)}h ago`;
            return `${Math.floor(diff/1440)}d ago`;
        }
        
        async function refreshData() {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            
            // Update metrics
            document.getElementById('totalUsers').textContent = data.metrics.total_users.toLocaleString();
            document.getElementById('activeUsers').textContent = data.metrics.active_users.toLocaleString();
            document.getElementById('successRate').textContent = (data.metrics.avg_success_rate * 100).toFixed(1) + '%';
            document.getElementById('churnRate').textContent = (data.metrics.churn_rate * 100).toFixed(1) + '%';
            document.getElementById('anomalies').textContent = data.metrics.anomalies_detected;
            document.getElementById('predictions').textContent = data.metrics.predictions_made.toLocaleString();
            
            // Update user table
            const tableBody = document.getElementById('usersTable');
            tableBody.innerHTML = data.users.slice(0, 10).map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td><span class="type-badge type-${user.type}">${user.type}</span></td>
                    <td>${user.interactions}</td>
                    <td>${(user.success_rate * 100).toFixed(0)}%</td>
                    <td class="${getRiskClass(user.churn_risk)}">${(user.churn_risk * 100).toFixed(0)}%</td>
                    <td>${formatTime(user.last_active)}</td>
                    <td>${user.is_anomaly ? '<span class="anomaly-dot"></span> Anomaly' : 'Normal'}</td>
                </tr>
            `).join('');
            
            // Update charts
            updateCharts(data.intention_dist, data.feature_importance, data.activity_data, data.segment_data);
        }
        
        // Initialize
        fetch('/api/init')
            .then(res => res.json())
            .then(data => {
                initCharts(data.intention_dist, data.feature_importance, data.activity_data, data.segment_data);
                refreshData();
            });
        
        // Auto-refresh every 5 seconds
        setInterval(refreshData, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    """Combined API for dashboard data"""
    return jsonify({
        'metrics': generate_metrics(),
        'users': generate_live_users(),
        'intention_dist': generate_intention_distribution(),
        'feature_importance': generate_feature_importance(),
        'segment_data': {
            'Premium': random.randint(280, 380),
            'Regular': random.randint(1100, 1400),
            'New': random.randint(500, 700),
            'At-Risk': random.randint(100, 200)
        },
        'activity_data': {
            'labels': ['6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'],
            'values': [random.randint(100, 200), random.randint(200, 350), random.randint(300, 450), 
                      random.randint(450, 600), random.randint(400, 550), random.randint(350, 500),
                      random.randint(300, 450), random.randint(200, 350), random.randint(100, 250)]
        }
    })

@app.route('/api/init')
def api_init():
    """Initial data for chart initialization"""
    return jsonify({
        'intention_dist': generate_intention_distribution(),
        'feature_importance': generate_feature_importance(),
        'activity_data': {
            'labels': ['6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'],
            'values': [120, 250, 380, 520, 480, 420, 380, 290, 180]
        },
        'segment_data': {
            'Premium': 320,
            'Regular': 1250,
            'New': 580,
            'At-Risk': 150
        }
    })

@app.route('/api/metrics')
def api_metrics():
    """Live metrics data"""
    return jsonify({
        'metrics': generate_metrics(),
        'users': generate_live_users(),
        'intention_dist': generate_intention_distribution(),
        'feature_importance': generate_feature_importance(),
        'activity_data': {
            'labels': ['6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'],
            'values': [random.randint(100, 200), random.randint(200, 350), random.randint(300, 450), 
                      random.randint(450, 600), random.randint(400, 550), random.randint(350, 500),
                      random.randint(300, 450), random.randint(200, 350), random.randint(100, 250)]
        },
        'segment_data': {
            'Premium': random.randint(280, 380),
            'Regular': random.randint(1100, 1400),
            'New': random.randint(500, 700),
            'At-Risk': random.randint(100, 200)
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 IntentScope Live Preview Server")
    print("=" * 60)
    print("🌐 Open your browser to: http://127.0.0.1:5000")
    print("=" * 60)
    import os
port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
