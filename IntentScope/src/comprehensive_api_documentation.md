# IntentScope API Documentation

**Version:** 1.0  
**Last Updated:** February 2026  
**Base URL:** `https://api.intentscope.io/v1`

---

## 🚀 Quick Start

IntentScope predicts user intentions and success likelihood in real-time based on behavioral event streams. Perfect for building adaptive UX, personalized onboarding, and proactive intervention systems.

### Test API Key (Shareable)
```
API_KEY="zrv_test_demo_key_1a2b3c4d5e6f7g8h9i0j"
```

**Key Limits:**
- 100 requests per day
- Read-only access
- 30-day expiration
- Rate limit resets daily at midnight UTC

---

## 📡 Endpoints

### 1. POST /predict
**Real-time user intention prediction**

Accepts behavioral event streams and returns intention classification with success probability.

**Authentication:**
```
Authorization: Bearer YOUR_API_KEY
```

**Request:**
```http
POST /v1/predict
Content-Type: application/json
Authorization: Bearer zrv_test_demo_key_1a2b3c4d5e6f7g8h9i0j

{
  "user_id": 12345,
  "events": [
    {
      "event_name": "login",
      "timestamp": "2024-02-18T10:00:00Z",
      "metadata": {
        "tier": "basic",
        "success": true,
        "session_duration": 15
      }
    },
    {
      "event_name": "run_analysis",
      "timestamp": "2024-02-18T10:05:00Z",
      "metadata": {
        "tier": "advanced",
        "success": true,
        "session_duration": 25
      }
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "user_id": 12345,
  "intention": "Builder",
  "success_probability": 87.5,
  "confidence": 0.92,
  "top_predictive_behaviors": [
    "advanced_feature_frequency",
    "session_duration_avg",
    "action_diversity",
    "premium_tier_usage",
    "success_rate_overall"
  ],
  "inference_time_ms": 47.3,
  "features_extracted": 54,
  "events_processed": 2,
  "timestamp": "2024-02-18T10:05:01Z",
  "status": "success"
}
```

**Response Fields:**
- `intention`: User intention category (see [Intention Categories](#intention-categories))
- `success_probability`: Likelihood of long-term success (0-100)
- `confidence`: Model confidence score (0-1)
- `top_predictive_behaviors`: Top 5 behavioral features driving the prediction
- `inference_time_ms`: Total processing time in milliseconds
- `features_extracted`: Number of behavioral features computed
- `events_processed`: Number of events in the request

**Event Types:**
- `login` - User authentication
- `view_dashboard` - Dashboard viewing
- `run_analysis` - Execute analysis/computation
- `create_visualization` - Create chart/visualization
- `export_data` - Export results
- `share_result` - Share with others
- `upgrade_tier` - Upgrade account

**Metadata Fields:**
- `tier`: User tier ("basic", "advanced", "premium")
- `success`: Whether action succeeded (boolean)
- `session_duration`: Duration in minutes (number)

---

### 2. GET /status
**API health check**

**Request:**
```http
GET /v1/status
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "status": "operational",
  "version": "1.0",
  "uptime_hours": 1248,
  "requests_today": 1537,
  "avg_latency_ms": 52.3,
  "model_version": "gb_v1.2"
}
```

---

### 3. GET /analytics
**Usage analytics for your API key**

**Request:**
```http
GET /v1/analytics
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "api_key_name": "Friend Test Key",
  "requests_today": 23,
  "remaining_today": 77,
  "total_requests": 456,
  "success_rate": 98.5,
  "avg_latency_ms": 48.7,
  "rate_limit": 100,
  "expires_at": "2024-03-20T00:00:00Z"
}
```

---

## 🎯 Intention Categories

| Intention | Description | Characteristics |
|-----------|-------------|-----------------|
| **Builder** | Power users creating advanced workflows | High feature diversity, long sessions, premium features |
| **Explorer** | Active users discovering capabilities | Medium engagement, varied actions, moderate success |
| **Learner** | New users in onboarding phase | Sequential actions, basic features, growing engagement |
| **Abandoner** | Users at risk of churning | Low engagement, short sessions, failed actions |

---

## 🔐 Authentication

All API requests require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

**Getting Your Key:**
Contact support@intentscope.io or use the test key provided above.

**Security Best Practices:**
- Never commit API keys to version control
- Rotate keys every 30-90 days
- Use environment variables to store keys
- Monitor usage in the analytics endpoint

---

## 💻 Code Examples

### Python
```python
import requests
import json
from datetime import datetime

API_KEY = "zrv_test_demo_key_1a2b3c4d5e6f7g8h9i0j"
BASE_URL = "https://api.intentscope.io/v1"

def predict_intention(user_id, events):
    """
    Predict user intention from behavioral events.
    
    Args:
        user_id: Unique user identifier
        events: List of event dicts with event_name, timestamp, metadata
    
    Returns:
        dict: Prediction response
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "user_id": user_id,
        "events": events
    }
    
    response = requests.post(
        f"{BASE_URL}/predict",
        headers=headers,
        json=payload,
        timeout=10
    )
    
    response.raise_for_status()
    return response.json()

# Example usage
events = [
    {
        "event_name": "login",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metadata": {
            "tier": "basic",
            "success": True,
            "session_duration": 15
        }
    },
    {
        "event_name": "run_analysis",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metadata": {
            "tier": "advanced",
            "success": True,
            "session_duration": 25
        }
    }
]

try:
    result = predict_intention(user_id=12345, events=events)
    print(f"Intention: {result['intention']}")
    print(f"Success Probability: {result['success_probability']}%")
    print(f"Latency: {result['inference_time_ms']}ms")
except requests.exceptions.HTTPError as e:
    print(f"API Error: {e.response.status_code} - {e.response.text}")
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

const API_KEY = 'zrv_test_demo_key_1a2b3c4d5e6f7g8h9i0j';
const BASE_URL = 'https://api.intentscope.io/v1';

/**
 * Predict user intention from behavioral events
 * @param {number} userId - Unique user identifier
 * @param {Array} events - Array of event objects
 * @returns {Promise<Object>} Prediction response
 */
async function predictIntention(userId, events) {
  try {
    const response = await axios.post(
      `${BASE_URL}/predict`,
      {
        user_id: userId,
        events: events
      },
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 10000
      }
    );
    
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error(`API Error: ${error.response.status}`, error.response.data);
    } else {
      console.error('Network Error:', error.message);
    }
    throw error;
  }
}

// Example usage
const events = [
  {
    event_name: 'login',
    timestamp: new Date().toISOString(),
    metadata: {
      tier: 'basic',
      success: true,
      session_duration: 15
    }
  },
  {
    event_name: 'run_analysis',
    timestamp: new Date().toISOString(),
    metadata: {
      tier: 'advanced',
      success: true,
      session_duration: 25
    }
  }
];

predictIntention(12345, events)
  .then(result => {
    console.log(`Intention: ${result.intention}`);
    console.log(`Success Probability: ${result.success_probability}%`);
    console.log(`Latency: ${result.inference_time_ms}ms`);
  })
  .catch(error => {
    console.error('Failed to get prediction');
  });
```

### cURL
```bash
curl -X POST https://api.intentscope.io/v1/predict \
  -H "Authorization: Bearer zrv_test_demo_key_1a2b3c4d5e6f7g8h9i0j" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 12345,
    "events": [
      {
        "event_name": "login",
        "timestamp": "2024-02-18T10:00:00Z",
        "metadata": {
          "tier": "basic",
          "success": true,
          "session_duration": 15
        }
      },
      {
        "event_name": "run_analysis",
        "timestamp": "2024-02-18T10:05:00Z",
        "metadata": {
          "tier": "advanced",
          "success": true,
          "session_duration": 25
        }
      }
    ]
  }'
```

---

## ⚡ Performance

- **Target Latency:** <200ms end-to-end
- **Typical Latency:** 50-100ms
- **Max Events per Request:** 100
- **Max Request Size:** 1MB
- **Concurrent Requests:** Supported (thread-safe)

**Optimization Tips:**
- Batch events when possible (up to 100 per request)
- Cache predictions for 5-10 minutes if user behavior unchanged
- Use async/await or promises for non-blocking requests
- Monitor latency via the analytics endpoint

---

## ❌ Error Codes

| Code | Error | Description | Solution |
|------|-------|-------------|----------|
| 400 | Bad Request | Missing or invalid fields | Check request format |
| 401 | Unauthorized | Invalid API key | Verify API key |
| 403 | Forbidden | Key expired or revoked | Request new key |
| 429 | Rate Limit Exceeded | Daily limit reached | Wait until next day or upgrade |
| 500 | Internal Server Error | Server processing error | Retry with exponential backoff |
| 503 | Service Unavailable | Temporary outage | Check /status endpoint |

**Error Response Format:**
```json
{
  "status": "error",
  "error_code": 429,
  "error_message": "Rate limit exceeded (100 requests/day)",
  "remaining_requests": 0,
  "resets_at": "2024-02-19T00:00:00Z"
}
```

---

## 📊 Rate Limits

| Key Type | Requests/Day | Requests/Min | Features |
|----------|--------------|--------------|----------|
| Test | 100 | 10 | Read-only |
| Developer | 5,000 | 100 | Read + Write |
| Production | 50,000 | 1,000 | Full access |
| Enterprise | Unlimited | Unlimited | Custom SLA |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 77
X-RateLimit-Reset: 1708300800
```

---

## 🧪 Testing from Your IDE

### Python Test Script
```python
# test_intentscope.py
import requests
import json
from datetime import datetime

API_KEY = "zrv_test_demo_key_1a2b3c4d5e6f7g8h9i0j"
BASE_URL = "https://api.intentscope.io/v1"

def test_api():
    """Test the IntentScope API with sample data"""
    
    # Test 1: Check API status
    print("Test 1: Checking API status...")
    response = requests.get(
        f"{BASE_URL}/status",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    print(f"✓ Status: {response.json()['status']}")
    
    # Test 2: Predict Builder intention
    print("\nTest 2: Predicting Builder intention...")
    builder_events = [
        {"event_name": "login", "timestamp": datetime.utcnow().isoformat() + "Z",
         "metadata": {"tier": "premium", "success": True, "session_duration": 45}},
        {"event_name": "run_analysis", "timestamp": datetime.utcnow().isoformat() + "Z",
         "metadata": {"tier": "premium", "success": True, "session_duration": 60}},
        {"event_name": "create_visualization", "timestamp": datetime.utcnow().isoformat() + "Z",
         "metadata": {"tier": "premium", "success": True, "session_duration": 30}},
        {"event_name": "export_data", "timestamp": datetime.utcnow().isoformat() + "Z",
         "metadata": {"tier": "premium", "success": True, "session_duration": 15}}
    ]
    
    response = requests.post(
        f"{BASE_URL}/predict",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"user_id": 1001, "events": builder_events}
    )
    result = response.json()
    print(f"✓ Intention: {result['intention']}")
    print(f"✓ Success Probability: {result['success_probability']}%")
    print(f"✓ Latency: {result['inference_time_ms']}ms")
    
    # Test 3: Check analytics
    print("\nTest 3: Checking analytics...")
    response = requests.get(
        f"{BASE_URL}/analytics",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    analytics = response.json()
    print(f"✓ Requests today: {analytics['requests_today']}/{analytics['rate_limit']}")
    print(f"✓ Remaining: {analytics['remaining_today']}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_api()
```

### JavaScript Test Script
```javascript
// test_intentscope.js
const axios = require('axios');

const API_KEY = 'zrv_test_demo_key_1a2b3c4d5e6f7g8h9i0j';
const BASE_URL = 'https://api.intentscope.io/v1';

async function testAPI() {
  try {
    // Test 1: Check API status
    console.log('Test 1: Checking API status...');
    const statusResponse = await axios.get(`${BASE_URL}/status`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    console.log(`✓ Status: ${statusResponse.data.status}`);
    
    // Test 2: Predict Builder intention
    console.log('\nTest 2: Predicting Builder intention...');
    const builderEvents = [
      {
        event_name: 'login',
        timestamp: new Date().toISOString(),
        metadata: { tier: 'premium', success: true, session_duration: 45 }
      },
      {
        event_name: 'run_analysis',
        timestamp: new Date().toISOString(),
        metadata: { tier: 'premium', success: true, session_duration: 60 }
      }
    ];
    
    const predictResponse = await axios.post(`${BASE_URL}/predict`, {
      user_id: 1001,
      events: builderEvents
    }, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
    
    const result = predictResponse.data;
    console.log(`✓ Intention: ${result.intention}`);
    console.log(`✓ Success Probability: ${result.success_probability}%`);
    console.log(`✓ Latency: ${result.inference_time_ms}ms`);
    
    // Test 3: Check analytics
    console.log('\nTest 3: Checking analytics...');
    const analyticsResponse = await axios.get(`${BASE_URL}/analytics`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    const analytics = analyticsResponse.data;
    console.log(`✓ Requests today: ${analytics.requests_today}/${analytics.rate_limit}`);
    console.log(`✓ Remaining: ${analytics.remaining_today}`);
    
    console.log('\n✅ All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
}

testAPI();
```

---

## 🎓 Use Cases

### 1. Adaptive Onboarding
Adjust onboarding flow based on real-time intention detection:
```python
result = predict_intention(user_id, recent_events)

if result['intention'] == 'Learner':
    show_tutorial()
elif result['intention'] == 'Builder':
    unlock_advanced_features()
elif result['intention'] == 'Abandoner':
    trigger_intervention()
```

### 2. Proactive Support
Detect users at risk and intervene:
```python
if result['intention'] == 'Abandoner' and result['success_probability'] < 30:
    offer_live_chat_support()
    send_personalized_tips()
```

### 3. Feature Recommendations
Suggest next-best actions:
```python
top_behaviors = result['top_predictive_behaviors']
recommend_features_based_on(top_behaviors)
```

### 4. A/B Testing
Segment users by intention for experiments:
```python
if result['intention'] in ['Builder', 'Explorer']:
    show_beta_feature()
```

---

## 🔄 Changelog

**v1.0 (Feb 2026)**
- Initial release
- Real-time prediction API
- 4 intention categories (Builder, Explorer, Learner, Abandoner)
- 54 behavioral features
- <200ms latency guarantee

---

## 📞 Support

- **Documentation:** https://docs.intentscope.io
- **Email:** support@intentscope.io
- **Status Page:** https://status.intentscope.io
- **Community:** https://community.intentscope.io

---

## 📄 License

This API documentation is licensed under CC BY 4.0.  
IntentScope API is proprietary software.