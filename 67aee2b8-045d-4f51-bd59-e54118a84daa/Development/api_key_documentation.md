# 🔑 API Key Generator System Documentation

## Overview
A secure API key generation and management system with cryptographic security, expiration management, rate limiting, and comprehensive analytics tracking.

## Features

### ✅ Core Capabilities
- **Secure Key Generation**: Uses Python's `secrets` module for cryptographically strong random key generation
- **Expiration Management**: Configurable expiration dates for time-limited access
- **Rate Limiting**: Daily request limits to prevent abuse
- **Permission-Based Access Control**: Granular permissions (read, write, delete, admin)
- **Usage Analytics**: Track all API key usage with detailed logs
- **Key Validation**: Real-time validation checking expiration and rate limits
- **Key Revocation**: Ability to deactivate keys instantly

## API Key Types

### 1. Admin Key
- **Permissions**: read, write, delete, admin
- **Rate Limit**: 10,000 requests/day
- **Expires**: 365 days
- **Use Case**: Full system access for internal administrators

### 2. Developer Key
- **Permissions**: read, write
- **Rate Limit**: 5,000 requests/day
- **Expires**: 90 days
- **Use Case**: Standard developer access for building integrations

### 3. Friend Test Key (Shareable)
- **Permissions**: read only
- **Rate Limit**: 100 requests/day
- **Expires**: 30 days
- **Use Case**: Safe sharing with friends for testing with limited access

## Security Features

### Key Storage
- Keys are hashed using SHA-256 before storage
- Never store raw API keys in production
- Metadata stored separately from keys

### Validation Checks
1. **Key Existence**: Verify key exists in system
2. **Active Status**: Check if key has been revoked
3. **Expiration**: Validate against expiration timestamp
4. **Rate Limiting**: Enforce daily request limits

### Usage Tracking
- Every API call is logged with timestamp
- Track endpoint accessed
- Monitor success/failure rates
- Calculate remaining daily quota

## Usage Example

```python
# Initialize the generator
generator = APIKeyGenerator()

# Generate a new API key
api_key = generator.generate_key(
    name="My API Key",
    permissions=['read'],
    expires_days=30,
    rate_limit=100,
    notes="Test key for development"
)

# Validate the key
is_valid, reason, metadata = generator.validate_key(api_key['key'])

# Log usage
generator.log_usage(api_key['key'], '/api/endpoint', success=True)

# Get analytics
analytics = generator.get_analytics(api_key['key'])

# Revoke key if needed
generator.revoke_key(api_key['key'])
```

## Integration Guide

### 1. Middleware Setup
Add key validation to your API middleware:

```python
def validate_api_key_middleware(request):
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    is_valid, reason, metadata = generator.validate_key(api_key)
    
    if not is_valid:
        return {'error': reason}, 401
    
    # Log the usage
    generator.log_usage(api_key, request.path, success=True)
    
    return metadata
```

### 2. Permission Checking
Enforce permissions based on key metadata:

```python
def check_permission(metadata, required_permission):
    if required_permission not in metadata['permissions']:
        raise PermissionError(f"Key does not have '{required_permission}' permission")
```

### 3. Rate Limit Headers
Return rate limit info in response headers:

```python
def add_rate_limit_headers(response, api_key):
    analytics = generator.get_analytics(api_key)
    metadata = analytics['metadata']
    
    response.headers['X-RateLimit-Limit'] = str(metadata['rate_limit'])
    response.headers['X-RateLimit-Remaining'] = str(
        metadata['rate_limit'] - analytics['total_requests']
    )
    return response
```

## Analytics Dashboard

Track key usage metrics:
- Total requests per key
- Success/failure rates
- First and last usage timestamps
- Remaining daily quota
- Permission usage patterns

## Best Practices

### For Administrators
1. Rotate admin keys quarterly
2. Review key analytics monthly
3. Revoke unused keys immediately
4. Use minimum required permissions

### For Developers
1. Never commit API keys to version control
2. Store keys in environment variables
3. Rotate keys before expiration
4. Monitor rate limit usage

### For Sharing
1. Use read-only test keys
2. Set short expiration periods (7-30 days)
3. Set conservative rate limits
4. Revoke immediately after testing

## Error Handling

Common error scenarios:
- **Invalid API key**: Key not found in system
- **API key expired**: Current date exceeds expiration
- **API key deactivated**: Key has been revoked
- **Rate limit exceeded**: Daily quota reached

## Production Recommendations

1. **Database Storage**: Use PostgreSQL or Redis for key metadata
2. **Encryption**: Encrypt key hashes at rest
3. **Audit Logging**: Log all validation attempts
4. **Monitoring**: Set up alerts for unusual patterns
5. **Backup**: Regular backups of key metadata
6. **SSL/TLS**: Always use HTTPS for API endpoints

## System Status

✅ API Key Generator System is operational and ready for use
✅ Shareable test key generated and validated
✅ Analytics tracking enabled
✅ Rate limiting active
