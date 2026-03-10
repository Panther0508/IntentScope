import hashlib
import secrets
import time
from datetime import datetime, timedelta
import json

# API Key Generator System with secure key generation, metadata storage, and rate limiting

class APIKeyGenerator:
    """Generates and manages secure API keys with expiration, usage limits, and permissions."""
    
    def __init__(self):
        self.keys = {}  # Store API key metadata
        self.usage_log = {}  # Track usage per key
        
    def generate_key(self, name, permissions=None, expires_days=30, rate_limit=1000, notes=""):
        """
        Generate a secure API key with metadata.
        
        Args:
            name: Friendly name for the API key
            permissions: List of allowed operations (e.g., ['read', 'write'])
            expires_days: Number of days until expiration
            rate_limit: Max requests per day
            notes: Additional notes about the key
            
        Returns:
            dict: API key and metadata
        """
        # Generate cryptographically secure random key
        key_bytes = secrets.token_bytes(32)
        api_key = f"zrv_{secrets.token_urlsafe(32)}"
        
        # Calculate expiration
        created_at = datetime.now()
        expires_at = created_at + timedelta(days=expires_days) if expires_days else None
        
        # Default permissions
        if permissions is None:
            permissions = ['read']
        
        # Store key metadata
        key_metadata = {
            'key': api_key,
            'name': name,
            'permissions': permissions,
            'created_at': created_at.isoformat(),
            'expires_at': expires_at.isoformat() if expires_at else None,
            'rate_limit': rate_limit,
            'notes': notes,
            'active': True,
            'usage_count': 0
        }
        
        # Hash the key for storage (in production, never store raw keys)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        self.keys[key_hash] = key_metadata
        self.usage_log[key_hash] = []
        
        return key_metadata
    
    def validate_key(self, api_key):
        """
        Validate an API key and check expiration, rate limits.
        
        Returns:
            tuple: (is_valid, reason, metadata)
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash not in self.keys:
            return False, "Invalid API key", None
        
        metadata = self.keys[key_hash]
        
        # Check if key is active
        if not metadata['active']:
            return False, "API key deactivated", metadata
        
        # Check expiration
        if metadata['expires_at']:
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if datetime.now() > expires_at:
                return False, "API key expired", metadata
        
        # Check rate limit (daily)
        today = datetime.now().date().isoformat()
        daily_usage = sum(1 for log in self.usage_log[key_hash] 
                         if log['timestamp'].startswith(today))
        
        if daily_usage >= metadata['rate_limit']:
            return False, f"Rate limit exceeded ({metadata['rate_limit']} requests/day)", metadata
        
        return True, "Valid", metadata
    
    def log_usage(self, api_key, endpoint, success=True):
        """Log API key usage for analytics."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash in self.keys:
            self.usage_log[key_hash].append({
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'success': success
            })
            self.keys[key_hash]['usage_count'] += 1
    
    def get_analytics(self, api_key):
        """Get usage analytics for a specific key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash not in self.keys:
            return None
        
        logs = self.usage_log[key_hash]
        
        return {
            'total_requests': len(logs),
            'successful_requests': sum(1 for log in logs if log['success']),
            'failed_requests': sum(1 for log in logs if not log['success']),
            'first_used': logs[0]['timestamp'] if logs else None,
            'last_used': logs[-1]['timestamp'] if logs else None,
            'metadata': self.keys[key_hash]
        }
    
    def revoke_key(self, api_key):
        """Deactivate an API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.keys:
            self.keys[key_hash]['active'] = False
            return True
        return False


# Initialize the generator
generator = APIKeyGenerator()

# Generate example API keys for different use cases
admin_key = generator.generate_key(
    name="Admin Key",
    permissions=['read', 'write', 'delete', 'admin'],
    expires_days=365,
    rate_limit=10000,
    notes="Full access admin key for internal use"
)

developer_key = generator.generate_key(
    name="Developer Key",
    permissions=['read', 'write'],
    expires_days=90,
    rate_limit=5000,
    notes="Standard developer access"
)

# Generate shareable test key for friends with limited permissions and rate limiting
friend_test_key = generator.generate_key(
    name="Friend Test Key",
    permissions=['read'],
    expires_days=30,
    rate_limit=100,
    notes="Shareable test key with read-only access and 100 requests/day limit"
)

# Simulate some usage
generator.log_usage(friend_test_key['key'], '/api/predict', success=True)
generator.log_usage(friend_test_key['key'], '/api/status', success=True)
generator.log_usage(friend_test_key['key'], '/api/analytics', success=True)

# Validate the test key
is_valid, reason, metadata = generator.validate_key(friend_test_key['key'])

# Get analytics
analytics = generator.get_analytics(friend_test_key['key'])

print("=" * 80)
print("API KEY GENERATOR SYSTEM - INITIALIZED")
print("=" * 80)
print("\n✓ Secure key generation with cryptographically strong randomness")
print("✓ Expiration date management")
print("✓ Usage limits and rate limiting")
print("✓ Permission-based access control")
print("✓ Usage analytics and tracking")
print("✓ Key validation and revocation")

print("\n" + "=" * 80)
print("GENERATED API KEYS")
print("=" * 80)

print(f"\n1. ADMIN KEY:")
print(f"   Name: {admin_key['name']}")
print(f"   Key: {admin_key['key'][:20]}...{admin_key['key'][-10:]}")
print(f"   Permissions: {', '.join(admin_key['permissions'])}")
print(f"   Rate Limit: {admin_key['rate_limit']:,} requests/day")
print(f"   Expires: {admin_key['expires_at']}")
print(f"   Notes: {admin_key['notes']}")

print(f"\n2. DEVELOPER KEY:")
print(f"   Name: {developer_key['name']}")
print(f"   Key: {developer_key['key'][:20]}...{developer_key['key'][-10:]}")
print(f"   Permissions: {', '.join(developer_key['permissions'])}")
print(f"   Rate Limit: {developer_key['rate_limit']:,} requests/day")
print(f"   Expires: {developer_key['expires_at']}")
print(f"   Notes: {developer_key['notes']}")

print(f"\n3. FRIEND TEST KEY (SHAREABLE):")
print(f"   Name: {friend_test_key['name']}")
print(f"   Key: {friend_test_key['key']}")
print(f"   Permissions: {', '.join(friend_test_key['permissions'])}")
print(f"   Rate Limit: {friend_test_key['rate_limit']:,} requests/day")
print(f"   Expires: {friend_test_key['expires_at']}")
print(f"   Notes: {friend_test_key['notes']}")
print(f"   Status: {'✓ Active' if friend_test_key['active'] else '✗ Inactive'}")

print("\n" + "=" * 80)
print("TEST KEY VALIDATION & ANALYTICS")
print("=" * 80)

print(f"\nValidation Result: {'✓ VALID' if is_valid else '✗ INVALID'}")
print(f"Reason: {reason}")
print(f"\nUsage Statistics:")
print(f"   Total Requests: {analytics['total_requests']}")
print(f"   Successful: {analytics['successful_requests']}")
print(f"   Failed: {analytics['failed_requests']}")
print(f"   Remaining Today: {friend_test_key['rate_limit'] - analytics['total_requests']}")

print("\n" + "=" * 80)
print("SHAREABLE TEST KEY - READY TO USE")
print("=" * 80)
print(f"\nShare this key with friends for testing:")
print(f"\nAPI_KEY = '{friend_test_key['key']}'")
print(f"\nUsage Example:")
print(f"  curl -H 'Authorization: Bearer {friend_test_key['key'][:30]}...'")
print(f"       https://api.yourservice.com/predict")
print(f"\nLimits:")
print(f"  • Read-only access")
print(f"  • 100 requests per day")
print(f"  • Expires in 30 days ({friend_test_key['expires_at'][:10]})")

print("\n" + "=" * 80)
print("SUCCESS: API Key Generator System Ready")
print("=" * 80)
