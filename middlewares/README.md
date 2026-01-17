# Middlewares

## Overview

The `middlewares` module provides FastAPI middleware components that process all HTTP requests and responses. Middlewares add cross-cutting concerns like authentication, rate limiting, security headers, and request context.

## Purpose

**Middleware** in FastAPI/Starlette:

- Intercepts every request before it reaches route handlers
- Can modify requests and responses
- Implements cross-cutting concerns uniformly
- Executes in a defined order (first added = outermost)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HTTP Request                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               RequestContextMiddleware                       │
│              (Add URN, timestamp)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                RateLimitMiddleware                           │
│           (Check rate limits, add headers)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              AuthenticationMiddleware                        │
│           (Validate JWT, set user context)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              SecurityHeadersMiddleware                       │
│           (Add CSP, HSTS, X-Frame-Options)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Route Handler                              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### RequestContextMiddleware (`request_context.py`)

Generates unique request identifier (URN) and tracks timing.

```python
from middlewares.request_context import RequestContextMiddleware

app.add_middleware(RequestContextMiddleware)
```

**Features:**
- Generates ULID-based URN for each request
- Adds `request.state.urn` for downstream access
- Tracks request start time
- Adds `X-Process-Time` and `X-Request-URN` response headers

**Response Headers:**
```
X-Process-Time: 0:00:00.045123
X-Request-URN: 01ARZ3NDEKTSV4RRFFQ69G5FAV
```

### AuthenticationMiddleware (`authetication.py`)

Validates JWT tokens and enforces authentication on protected routes.

```python
from middlewares.authetication import AuthenticationMiddleware

app.add_middleware(AuthenticationMiddleware)
```

**Features:**
- Skips unprotected routes and OPTIONS requests
- Validates JWT from Authorization header
- Verifies user is logged in via database
- Sets `request.state.user_id` and `request.state.user_urn`
- Returns 401 Unauthorized for invalid/missing tokens

**Error Response:**
```json
{
    "transactionUrn": "...",
    "status": "FAILED",
    "responseMessage": "JWT Authentication failed.",
    "responseKey": "error_authetication_error"
}
```

### RateLimitMiddleware (`rate_limit.py`)

Protects against abuse with configurable rate limiting.

```python
from middlewares.rate_limit import RateLimitMiddleware, RateLimitConfig

config = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_limit=10
)

app.add_middleware(RateLimitMiddleware, config=config)
```

**Features:**
- Sliding window rate limiting algorithm
- Per-client tracking via IP address
- Configurable limits per minute/hour
- Automatic cleanup of old entries
- Rate limit headers in responses

**Response Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1609459200
Retry-After: 60
```

**Rate Limit Error (429):**
```json
{
    "transactionUrn": "...",
    "status": "FAILED",
    "responseMessage": "Rate limit exceeded. Please try again later.",
    "responseKey": "error_rate_limit_exceeded",
    "data": {
        "exceeded_limits": ["sliding_minute"],
        "retry_after": 60
    }
}
```

### SecurityHeadersMiddleware (`security_headers.py`)

Adds security headers to all responses for browser protection.

```python
from middlewares.security_headers import SecurityHeadersMiddleware

app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=True,
    enable_csp=True
)
```

**Headers Added:**
| Header | Purpose |
|--------|---------|
| `Content-Security-Policy` | Prevent XSS and injection attacks |
| `Strict-Transport-Security` | Force HTTPS connections |
| `X-Frame-Options` | Prevent clickjacking (DENY) |
| `X-Content-Type-Options` | Prevent MIME sniffing (nosniff) |
| `X-XSS-Protection` | Legacy XSS filter |
| `Referrer-Policy` | Control referrer information |
| `Permissions-Policy` | Restrict browser features |
| `X-Download-Options` | IE download protection |
| `X-Permitted-Cross-Domain-Policies` | Flash cross-domain policy |

## Middleware Order

Order matters! Middlewares are added in reverse execution order:

```python
# Last added = first executed
app.add_middleware(SecurityHeadersMiddleware)      # 4th
app.add_middleware(AuthenticationMiddleware)        # 3rd
app.add_middleware(RateLimitMiddleware)             # 2nd
app.add_middleware(RequestContextMiddleware)        # 1st
```

**Execution Order:**
1. RequestContextMiddleware (add URN)
2. RateLimitMiddleware (check limits)
3. AuthenticationMiddleware (validate token)
4. SecurityHeadersMiddleware (add headers on response)

## Configuration

### RateLimitConfig

```python
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    window_size: int = 60
    enable_sliding_window: bool = True
    enable_token_bucket: bool = False
    enable_fixed_window: bool = False
```

### SecurityHeadersConfig

```python
class SecurityHeadersConfig:
    enable_hsts: bool = True
    enable_csp: bool = True
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    frame_options: str = "DENY"
    content_type_options: str = "nosniff"
    xss_protection: str = "1; mode=block"
    referrer_policy: str = "strict-origin-when-cross-origin"
```

## Protected vs Unprotected Routes

Routes are configured in `start_utils.py`:

```python
unprotected_routes = {
    "/user/login",
    "/user/register",
    "/docs",
    "/openapi.json",
    "/health"
}

callback_routes = set()  # Webhook endpoints
```

## Best Practices

1. **Order carefully**: Request context must be first
2. **Log appropriately**: Debug for flow, Error for failures
3. **Handle errors gracefully**: Return proper JSON responses
4. **Use configuration**: Don't hardcode values
5. **Test thoroughly**: Middleware affects all requests

## File Structure

```
middlewares/
├── __init__.py
├── README.md
├── authetication.py       # JWT authentication
├── rate_limit.py          # Rate limiting
├── request_context.py     # Request URN and timing
└── security_headers.py    # Security response headers
```
