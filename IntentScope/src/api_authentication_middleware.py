import hashlib
import time
import secrets
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

class APIAuthenticationMiddleware:
    """
    API Authentication middleware for validating API keys, checking permissions,
    enforcing rate limits, and logging usage for IntentScope prediction and analytics systems.
    """
    
    def __init__(self):
        # In-memory storage for demo (production should use Redis/database)
        self.api_keys = {}
        self.rate_limit_counters = {}
        self.usage_logs = []
        self.blocked_keys = set()
        
        # Rate limit configurations by tier
        self.rate_limits = {
            'free': {'requests_per_minute': 10, 'requests_per_day': 1000},
            'basic': {'requests_per_minute': 60, 'requests_per_day': 10000},
            'premium': {'requests_per_minute': 300, 'requests_per_day': 100000},
            'enterprise': {'requests_per_minute': 1000, 'requests_per_day': 1000000}
        }
        
        # Permission configurations by tier
        self.permissions = {
            'free': ['predict', 'basic_analytics'],
            'basic': ['predict', 'basic_analytics', 'batch_predict'],
            'premium': ['predict', 'basic_analytics', 'batch_predict', 'advanced_analytics', 'recommendations'],
            'enterprise': ['predict', 'basic_analytics', 'batch_predict', 'advanced_analytics', 'recommendations', 'admin']
        }
        
    def generate_api_key(self, user_id: str, tier: str = 'free', 
                         expiry_days: int = 365) -> str:
        """Generate a new API key for a user"""
        if tier not in self.rate_limits:
            raise ValueError(f"Invalid tier: {tier}")
        
        # Generate secure random API key
        api_key = f"isk_{secrets.token_urlsafe(32)}"
        
        # Store API key metadata
        self.api_keys[api_key] = {
            'user_id': user_id,
            'tier': tier,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(days=expiry_days),
            'is_active': True,
            'total_requests': 0,
            'last_used': None
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validate API key and return validation status, error message, and key metadata
        Returns: (is_valid, error_message, key_metadata)
        """
        # Check if key exists
        if api_key not in self.api_keys:
            return False, "Invalid API key", None
        
        key_data = self.api_keys[api_key]
        
        # Check if key is blocked
        if api_key in self.blocked_keys:
            return False, "API key has been blocked", None
        
        # Check if key is active
        if not key_data['is_active']:
            return False, "API key has been deactivated", None
        
        # Check if key has expired
        if datetime.now() > key_data['expires_at']:
            return False, "API key has expired", None
        
        return True, None, key_data
    
    def check_permissions(self, api_key: str, required_permission: str) -> Tuple[bool, Optional[str]]:
        """
        Check if API key has required permission
        Returns: (has_permission, error_message)
        """
        is_valid, error_msg, key_data = self.validate_api_key(api_key)
        
        if not is_valid:
            return False, error_msg
        
        tier = key_data['tier']
        allowed_permissions = self.permissions.get(tier, [])
        
        if required_permission not in allowed_permissions:
            return False, f"Permission denied: '{required_permission}' not available for {tier} tier"
        
        return True, None
    
    def check_rate_limit(self, api_key: str) -> Tuple[bool, Optional[str], Dict]:
        """
        Check rate limits for API key
        Returns: (within_limit, error_message, rate_limit_info)
        """
        is_valid, error_msg, key_data = self.validate_api_key(api_key)
        
        if not is_valid:
            return False, error_msg, {}
        
        tier = key_data['tier']
        limits = self.rate_limits[tier]
        
        # Initialize rate limit counters if not exists
        if api_key not in self.rate_limit_counters:
            self.rate_limit_counters[api_key] = {
                'minute': {'count': 0, 'reset_at': datetime.now() + timedelta(minutes=1)},
                'day': {'count': 0, 'reset_at': datetime.now() + timedelta(days=1)}
            }
        
        counters = self.rate_limit_counters[api_key]
        current_time = datetime.now()
        
        # Reset minute counter if needed
        if current_time > counters['minute']['reset_at']:
            counters['minute'] = {'count': 0, 'reset_at': current_time + timedelta(minutes=1)}
        
        # Reset day counter if needed
        if current_time > counters['day']['reset_at']:
            counters['day'] = {'count': 0, 'reset_at': current_time + timedelta(days=1)}
        
        # Check minute limit
        if counters['minute']['count'] >= limits['requests_per_minute']:
            seconds_until_reset = int((counters['minute']['reset_at'] - current_time).total_seconds())
            return False, f"Rate limit exceeded: {limits['requests_per_minute']} requests/minute. Retry in {seconds_until_reset}s", {
                'limit': limits['requests_per_minute'],
                'remaining': 0,
                'reset_in_seconds': seconds_until_reset
            }
        
        # Check day limit
        if counters['day']['count'] >= limits['requests_per_day']:
            seconds_until_reset = int((counters['day']['reset_at'] - current_time).total_seconds())
            return False, f"Daily rate limit exceeded: {limits['requests_per_day']} requests/day. Retry in {seconds_until_reset}s", {
                'limit': limits['requests_per_day'],
                'remaining': 0,
                'reset_in_seconds': seconds_until_reset
            }
        
        # Calculate remaining requests
        rate_info = {
            'minute_limit': limits['requests_per_minute'],
            'minute_remaining': limits['requests_per_minute'] - counters['minute']['count'],
            'day_limit': limits['requests_per_day'],
            'day_remaining': limits['requests_per_day'] - counters['day']['count']
        }
        
        return True, None, rate_info
    
    def log_request(self, api_key: str, endpoint: str, success: bool, 
                   latency_ms: float, error_msg: Optional[str] = None):
        """Log API request for usage tracking and analytics"""
        if api_key in self.api_keys:
            key_data = self.api_keys[api_key]
            
            # Update key metadata
            key_data['last_used'] = datetime.now()
            key_data['total_requests'] += 1
            
            # Increment rate limit counters
            if api_key in self.rate_limit_counters:
                self.rate_limit_counters[api_key]['minute']['count'] += 1
                self.rate_limit_counters[api_key]['day']['count'] += 1
            
            # Store usage log
            log_entry = {
                'timestamp': datetime.now(),
                'api_key': api_key,
                'user_id': key_data['user_id'],
                'tier': key_data['tier'],
                'endpoint': endpoint,
                'success': success,
                'latency_ms': latency_ms,
                'error': error_msg
            }
            self.usage_logs.append(log_entry)
    
    def authenticate_request(self, api_key: str, endpoint: str, 
                            required_permission: str) -> Tuple[bool, str, Dict]:
        """
        Complete authentication workflow for incoming API requests
        Returns: (is_authenticated, message, metadata)
        """
        # Validate API key
        is_valid, error_msg, key_data = self.validate_api_key(api_key)
        if not is_valid:
            return False, error_msg, {'status': 'invalid_key'}
        
        # Check permissions
        has_permission, perm_error = self.check_permissions(api_key, required_permission)
        if not has_permission:
            return False, perm_error, {'status': 'permission_denied', 'tier': key_data['tier']}
        
        # Check rate limits
        within_limit, limit_error, rate_info = self.check_rate_limit(api_key)
        if not within_limit:
            return False, limit_error, {'status': 'rate_limited', 'rate_info': rate_info}
        
        # Authentication successful
        return True, "Authentication successful", {
            'status': 'authenticated',
            'user_id': key_data['user_id'],
            'tier': key_data['tier'],
            'rate_info': rate_info
        }
    
    def block_api_key(self, api_key: str, reason: str):
        """Block an API key (e.g., for abuse)"""
        if api_key in self.api_keys:
            self.blocked_keys.add(api_key)
            self.api_keys[api_key]['is_active'] = False
            print(f"API key blocked: {api_key[:20]}... Reason: {reason}")
    
    def get_usage_statistics(self, api_key: Optional[str] = None) -> Dict:
        """Get usage statistics for specific key or all keys"""
        if api_key:
            logs = [log for log in self.usage_logs if log['api_key'] == api_key]
        else:
            logs = self.usage_logs
        
        if not logs:
            return {'total_requests': 0, 'success_rate': 0, 'avg_latency_ms': 0}
        
        total = len(logs)
        successful = sum(1 for log in logs if log['success'])
        avg_latency = sum(log['latency_ms'] for log in logs) / total
        
        return {
            'total_requests': total,
            'successful_requests': successful,
            'failed_requests': total - successful,
            'success_rate': successful / total,
            'avg_latency_ms': round(avg_latency, 2)
        }

# Initialize the authentication middleware
auth_middleware = APIAuthenticationMiddleware()

# Demo: Create API keys for different tiers
demo_keys = {}
for tier in ['free', 'basic', 'premium', 'enterprise']:
    key = auth_middleware.generate_api_key(
        user_id=f"user_{tier}",
        tier=tier,
        expiry_days=365
    )
    demo_keys[tier] = key

print("=" * 80)
print("API AUTHENTICATION MIDDLEWARE - INITIALIZED")
print("=" * 80)
print(f"\n✓ Middleware ready for IntentScope prediction and analytics systems")
print(f"✓ Total tiers configured: {len(auth_middleware.rate_limits)}")
print(f"✓ Demo API keys generated: {len(demo_keys)}")

print(f"\n{'Tier':<15} {'Rate Limit (req/min)':<25} {'Permissions':<50}")
print("-" * 90)
for tier in ['free', 'basic', 'premium', 'enterprise']:
    limits = auth_middleware.rate_limits[tier]
    perms = ', '.join(auth_middleware.permissions[tier])
    print(f"{tier:<15} {limits['requests_per_minute']:<25} {perms:<50}")

print(f"\n{'Demo Keys':<15} {'API Key (truncated)':<40} {'Status':<20}")
print("-" * 75)
for tier, key in demo_keys.items():
    print(f"{tier:<15} {key[:35]}... {'Active' if auth_middleware.api_keys[key]['is_active'] else 'Inactive':<20}")

print("\n" + "=" * 80)
print("AUTHENTICATION FUNCTIONS AVAILABLE")
print("=" * 80)
print("✓ auth_middleware.authenticate_request(api_key, endpoint, permission)")
print("✓ auth_middleware.validate_api_key(api_key)")
print("✓ auth_middleware.check_permissions(api_key, permission)")
print("✓ auth_middleware.check_rate_limit(api_key)")
print("✓ auth_middleware.log_request(api_key, endpoint, success, latency_ms)")
print("✓ auth_middleware.block_api_key(api_key, reason)")
print("✓ auth_middleware.get_usage_statistics(api_key)")
print("=" * 80)
