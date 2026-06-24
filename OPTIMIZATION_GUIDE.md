# Optimization & Security Guide

## 1. Query Optimization Strategies

### Database Indexing
All critical queries have indexed columns created in `app/models/db.py`:

```python
# Example indexes
Index('idx_user_points', 'total_points')
Index('idx_match_status_scheduled', 'status', 'scheduled_at')
Index('idx_prediction_user_created', 'user_id', 'created_at')
```

**Key indexes:**
- `users.total_points` → Leaderboard ranking queries
- `matches.status, scheduled_at` → Filtering upcoming matches
- `predictions.user_id, created_at` → User prediction history
- `subscriptions.user_id, expires_at` → Premium status check
- `audit_logs.created_at` → Historical queries

### Query Patterns

#### 1. Get User Leaderboard (Top 100)
```python
# GOOD: Indexed query, limit 100
SELECT * FROM users 
WHERE total_points > 0 
ORDER BY total_points DESC 
LIMIT 100;
```

#### 2. Get User Predictions for Match
```python
# GOOD: Composite index
SELECT * FROM predictions 
WHERE user_id = $1 AND match_id = $2;
```

#### 3. Get Active Subscriptions
```python
# GOOD: Indexed, uses WHERE clause
SELECT * FROM subscriptions 
WHERE user_id = $1 
AND status = 'active' 
AND expires_at > NOW();
```

#### 4. Get Recent Matches
```python
# GOOD: Uses index on scheduled_at
SELECT * FROM matches 
WHERE status = 'upcoming' 
AND scheduled_at BETWEEN NOW() AND NOW() + INTERVAL '7 days' 
ORDER BY scheduled_at ASC;
```

### Caching Strategy

#### Redis Caching Layers

```
Cache Key Patterns:
├── user:{user_id}:profile          # User profile data (5 min TTL)
├── user:{user_id}:points           # User points/streak (1 min TTL)
├── user:{user_id}:accuracy         # Accuracy stats (5 min TTL)
├── match:{match_id}:current        # Current match state (30 sec TTL)
├── match:{match_id}:probability    # Win probability (15 sec TTL)
├── leaderboard:top_100             # Leaderboard cache (2 min TTL)
└── subscriptions:active:{user_id}  # Active subscription (10 min TTL)
```

#### Cache Invalidation

```python
# On prediction submitted
INVALIDATE:
  - user:{user_id}:points
  - user:{user_id}:accuracy
  - leaderboard:top_100

# On match update
INVALIDATE:
  - match:{match_id}:current
  - match:{match_id}:probability
  - All connected WebSocket clients (via Redis pub/sub)

# On subscription status change
INVALIDATE:
  - subscriptions:active:{user_id}
  - user:{user_id}:profile
```

### N+1 Query Prevention

Use database joins and eager loading:

```python
# BAD: N+1 queries
user = get_user(user_id)
predictions = get_predictions(user_id)  # Separate query per result

# GOOD: Single joined query
SELECT u.*, p.* FROM users u
JOIN predictions p ON u.id = p.user_id
WHERE u.id = $1;
```

---

## 2. Security Features Implemented

### Authentication & Authorization

#### JWT Token Verification
- ✅ Supabase JWT validation
- ✅ Token expiration (1 hour)
- ✅ Refresh token rotation (30 days)
- ✅ Blacklist for revoked tokens

```python
# File: app/core/security.py
@router.post("/auth/login")
async def login(request: LoginRequest):
    # Verify with Supabase
    # Return access token + refresh token
    # Log authentication event
```

#### Role-Based Access Control (RBAC)

```python
# Dependency example
async def require_premium(token_data: TokenData = Depends(get_current_user)):
    """Verify user has active premium subscription."""
    subscription = await check_active_subscription(token_data.user_id)
    if not subscription:
        raise HTTPException(status_code=403, detail="Premium required")
    return token_data
```

### API Security

#### 1. Rate Limiting
- ✅ 1000 requests per minute per IP
- ✅ Configurable per endpoint
- ✅ Redis-backed (production)
- ✅ Custom error response

```python
# Middleware: app/core/middleware.py
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting: 1000 req/min per IP"""
```

#### 2. Security Headers
- ✅ `X-Content-Type-Options: nosniff` (prevent MIME sniffing)
- ✅ `X-Frame-Options: DENY` (prevent clickjacking)
- ✅ `X-XSS-Protection: 1; mode=block` (XSS protection)
- ✅ `Strict-Transport-Security: max-age=31536000` (HTTPS only)
- ✅ `Content-Security-Policy: default-src 'self'` (CSP)

#### 3. Input Validation
- ✅ Pydantic v2 schema validation on all requests
- ✅ Email validation (`EmailStr`)
- ✅ Password minimum 8 characters
- ✅ Field type checking
- ✅ String length limits

```python
class SignupRequest(BaseModel):
    email: EmailStr  # Email format validation
    password: str = Field(..., min_length=8)  # Min 8 chars
    username: str = Field(..., min_length=3, max_length=20)  # Length limits
```

#### 4. SQL Injection Prevention
- ✅ All queries use parameterized statements
- ✅ ORM handles sanitization (SQLAlchemy)
- ✅ No string concatenation in queries

#### 5. Authorization
- ✅ Every authenticated endpoint checks token
- ✅ User can only access their own data
- ✅ Admin operations require elevated permissions
- ✅ Server-to-server webhooks have IP whitelist

#### 6. Money/Poisha Security
- ✅ All monetary values stored as integers (poisha)
- ✅ Never use floating point for money
- ✅ Conversion: 1 BDT = 100 poisha
- ✅ Validated on all financial endpoints

```python
# In database
price_poisha: Column(Integer)  # NOT Float

# On API level
price_bdt: float = 50.0  # Display only, calculated from poisha
price_poisha: int = 5000  # Source of truth
```

#### 7. Vendor Key Protection
- ✅ API key stored in server environment only
- ✅ Never exposed in client responses
- ✅ No client-side calls to vendor
- ✅ Server proxies all vendor requests

```python
# app/core/config.py
VENDOR_API_KEY: Optional[str] = None  # Loaded from .env only
# Never included in responses or logs
```

#### 8. Sensitive Data Handling
- ✅ Audit logging of sensitive operations
- ✅ Password never logged or returned
- ✅ Refresh tokens in HTTP-only cookies (client side)
- ✅ No personal data in error messages

#### 9. WebSocket Security
- ✅ JWT token validation on connection
- ✅ Per-connection rate limiting
- ✅ Automatic cleanup of stale connections
- ✅ Secure message format with types

---

## 3. Performance Optimization

### Database Connection Pooling
```python
# app/core/config.py - Supabase handles pooling
# Min 5, Max 20 connections
```

### Async Operations
- ✅ FastAPI async/await throughout
- ✅ Non-blocking database queries
- ✅ Non-blocking external API calls
- ✅ Concurrent request handling

### Response Compression
```python
# Added via middleware - gzip compression enabled
response.headers["Content-Encoding"] = "gzip"
```

### CDN Optimization
- ✅ OpenAPI spec available for client caching
- ✅ Static asset serving ready
- ✅ ETag support for caching

### Batch Operations
```python
# Batch prediction settlement
INSERT INTO predictions (...) 
WHERE match_id = $1 AND settled_at IS NULL;
# Single query instead of per-prediction
```

---

## 4. Monitoring & Logging

### Request Logging
- ✅ Request ID tracking (`X-Request-ID` header)
- ✅ Endpoint + method logging
- ✅ Response time logging
- ✅ Client IP logging

### Audit Trail
```python
# AuditLog table tracks:
# - Who (user_id, IP)
# - What (action, resource)
# - When (timestamp)
# - Changes (JSON details)
```

### Error Tracking
- ✅ Unhandled errors logged with full context
- ✅ Error messages don't leak sensitive info
- ✅ Request ID included in error responses

---

## 5. Best Practices Checklist

### Before Going to Production

#### Database
- [ ] Run all migrations
- [ ] Verify all indexes created
- [ ] Test backup/restore process
- [ ] Enable row-level security (RLS) in Supabase

#### Security
- [ ] Update `CORS` allow_origins (remove "*")
- [ ] Enable HTTPS only
- [ ] Set strong `SECRET_KEY`
- [ ] Rotate all API keys
- [ ] Enable rate limiting in production
- [ ] Set up IP whitelist for webhooks

#### Performance
- [ ] Enable Redis caching
- [ ] Set up database query monitoring
- [ ] Configure CDN for static assets
- [ ] Test under expected load

#### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Set up log aggregation (CloudWatch)
- [ ] Set up performance monitoring (New Relic)
- [ ] Create alerts for critical metrics

#### Operations
- [ ] Document deployment process
- [ ] Set up automated backups
- [ ] Plan rollback strategy
- [ ] Test disaster recovery

---

## 6. Future Optimizations

### Phase 2
- [ ] Implement caching layer (Redis)
- [ ] Add database read replicas for scaling
- [ ] Implement GraphQL for flexible queries
- [ ] Add Elasticsearch for full-text search

### Phase 3
- [ ] Implement message queue (for async tasks)
- [ ] Add background job processor (Celery)
- [ ] Implement API versioning strategy
- [ ] Add webhook retry logic with backoff

### Phase 4
- [ ] Implement edge caching (Cloudflare)
- [ ] Add database sharding for massive scale
- [ ] Implement circuit breakers for external APIs
- [ ] Add distributed tracing (Jaeger)

---

## Code Example: Optimized Query Pattern

```python
# app/services/user_service.py

class UserService:
    async def get_user_with_predictions(self, user_id: str, limit: int = 10):
        """
        Get user profile with recent predictions.
        Optimized: Single query with join
        """
        # Check cache first
        cached = await redis.get(f"user:{user_id}:profile")
        if cached:
            return json.loads(cached)

        # Single joined query (no N+1)
        user_data = await db.execute("""
            SELECT 
                u.id, u.email, u.username, u.total_points,
                u.accuracy_percentage, u.current_streak,
                COUNT(p.id) as prediction_count,
                SUM(CASE WHEN p.is_correct THEN 1 ELSE 0 END) as correct_count
            FROM users u
            LEFT JOIN predictions p ON u.id = p.user_id 
                AND p.created_at > NOW() - INTERVAL '30 days'
            WHERE u.id = $1
            GROUP BY u.id
        """, [user_id])

        # Cache result
        await redis.setex(
            f"user:{user_id}:profile",
            300,  # 5 minutes
            json.dumps(user_data)
        )

        return user_data
```

---

**Last Updated:** 2026-06-24
**Version:** 1.0.0
