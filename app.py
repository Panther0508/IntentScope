"""
IntentScope Live Preview Web Application
A real-time dashboard showing the AI-powered behavioral analytics system
"""

import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for all routes
CORS(app)

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

# Health check endpoint for Render
@app.route('/health')
def health_check():
    """Health check endpoint for Render deployment"""
    return jsonify({
        'status': 'healthy',
        'service': 'IntentScope Analytics',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'endpoints': ['/api/metrics', '/api/init', '/api/data', '/health']
    })

if __name__ == '__main__':
    print("=" * 60)
    print("=" * 60)
    print("Open your browser to: http://127.0.0.1:5000")
    print("=" * 60)
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
