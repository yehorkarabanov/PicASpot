# FastAPI Best Practices Recommendations for PicASpot

## Executive Summary
This document outlines remaining recommendations for improving the PicASpot FastAPI backend. Many best practices have already been implemented (see `features.md` for completed items). This document focuses on what still needs to be done to achieve production-grade quality.

**Last Updated:** 2025-11-30

---

## Implementation Status Legend
- ⚠️ **HIGH PRIORITY** - Critical for production readiness
- 🔶 **MEDIUM PRIORITY** - Important for scalability and maintainability
- 🔵 **LOW PRIORITY** - Nice to have, enhances user experience
- ✅ **COMPLETED** - See features.md for details

---

## 1. Testing & Quality Assurance

### 1.1 Implement Comprehensive Test Suite
**Priority:** ⚠️ **HIGH**

**Current State:**
- Test infrastructure configured (pytest, pytest-asyncio, httpx, faker)
- `tests/` directory exists but no tests implemented
- 0% code coverage

**Recommendations:**
```
☐ Unit tests for services and repositories
☐ Integration tests for API endpoints
☐ Authentication flow tests
☐ Database transaction tests
☐ Mock external dependencies (email, Redis)
☐ Test error cases and edge conditions
☐ Aim for >80% code coverage
```

**Suggested Test Structure:**
```
tests/
  ├── conftest.py              # Shared fixtures
  ├── unit/
  │   ├── test_auth_service.py
  │   ├── test_user_service.py
  │   ├── test_area_service.py
  │   ├── test_landmark_service.py
  │   ├── test_security.py
  │   └── test_repositories.py
  ├── integration/
  │   ├── test_auth_endpoints.py
  │   ├── test_user_endpoints.py
  │   ├── test_area_endpoints.py
  │   ├── test_landmark_endpoints.py
  │   └── test_unlock_endpoints.py
  └── e2e/
      ├── test_user_registration_flow.py
      └── test_landmark_unlock_flow.py
```

**Example Test Fixtures:**
```python
# conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from app.database.base import Base
from app.main import app

@pytest.fixture
async def test_db():
    # Use in-memory SQLite for tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def client(test_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def authenticated_client(client, test_db):
    # Create test user and get token
    # Return client with auth headers
    pass
```

**Benefits:**
- Catch bugs before production
- Confidence in refactoring
- Documentation through tests
- Regression prevention

---

### 1.2 Add CI/CD Pipeline
**Priority:** 🔶 **MEDIUM**

**Current State:**
- No automated testing on commits/PRs
- Manual deployment process

**Recommendations:**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install uv
        uses: astral-sh/setup-uv@v1
      
      - name: Install dependencies
        run: uv sync --extra test
      
      - name: Run linting
        run: uv run ruff check .
      
      - name: Run tests
        run: uv run pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

**Additional Workflows:**
```
☐ Linting and formatting check
☐ Type checking with mypy
☐ Security scanning (Bandit, Safety)
☐ Dependency vulnerability checks
☐ Automated deployment on main branch
☐ Docker image builds and pushes
```

**Benefits:**
- Automated quality checks
- Faster feedback loops
- Prevent broken code from merging
- Consistent build environment

---

## 2. Security Enhancements

### 2.1 Implement Refresh Token Mechanism
**Priority:** ⚠️ **HIGH**

**Current State:**
- Only access tokens implemented
- No token rotation
- No token revocation mechanism
- Users must re-login when token expires

**Recommendations:**
```python
# Add to User model or create separate RefreshToken model
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(unique=True, index=True)
    expires_at: Mapped[datetime.datetime]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    revoked: Mapped[bool] = mapped_column(default=False)
    
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

# Update security.py
def create_refresh_token(user_id: str, expires_delta: timedelta = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(days=30)  # 30 days
    
    expire = datetime.now(timezone.utc) + expires_delta
    token = secrets.token_urlsafe(32)
    
    # Store in database with expiry
    return token

# Add endpoints
@router.post("/refresh")
async def refresh_access_token(
    refresh_token: str = Body(...),
    auth_service: AuthServiceDep = Depends()
) -> AccessToken:
    # Validate refresh token
    # Issue new access token
    # Optionally rotate refresh token
    pass

@router.post("/logout")
async def logout(
    refresh_token: str = Body(...),
    current_user: CurrentUserDep = Depends()
) -> BaseReturn:
    # Revoke refresh token
    # Optionally blacklist access token in Redis
    pass
```

**Implementation Checklist:**
```
☐ Create RefreshToken model with database table
☐ Add create_refresh_token() function
☐ Return both access and refresh tokens on login
☐ Implement /auth/refresh endpoint
☐ Implement /auth/logout endpoint with token revocation
☐ Add token rotation (issue new refresh token on refresh)
☐ Clean up expired tokens (Celery periodic task)
☐ Update frontend to handle token refresh
```

**Benefits:**
- Better user experience (stay logged in)
- Improved security (short-lived access tokens)
- Token revocation on logout
- "Remember me" functionality

---

### 2.2 Add Security Headers Middleware
**Priority:** 🔶 **MEDIUM**

**Current State:**
- No security headers set
- Vulnerable to XSS, clickjacking, MIME sniffing

**Recommendations:**
```python
# app/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent XSS attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HTTPS enforcement (if not behind reverse proxy)
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'"
        )
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), microphone=(), camera=()"
        )
        
        return response

# Register in main.py
app.add_middleware(SecurityHeadersMiddleware)
```

**Additional Options:**
```python
# For production with reverse proxy
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)
```

**Benefits:**
- Protection against common web vulnerabilities
- Defense in depth
- Better security audit scores
- Compliance with security standards

---

### 2.3 Implement CSRF Protection
**Priority:** 🔶 **MEDIUM**

**Current State:**
- No CSRF protection
- API uses bearer token auth (lower risk)
- If cookies are used in future, CSRF is necessary

**Recommendations:**
```python
# If using cookies for authentication (future consideration)
from fastapi_csrf_protect import CsrfProtect

@app.post("/auth/login")
async def login(
    credentials: UserLogin,
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf(request)
    # Login logic
    
# OR validate Origin/Referer headers
class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            origin = request.headers.get("origin")
            referer = request.headers.get("referer")
            
            if not self._is_valid_origin(origin, referer):
                return JSONResponse(
                    status_code=403,
                    content={"message": "Invalid origin"}
                )
        
        return await call_next(request)
```

**Note:** Current implementation with bearer tokens has lower CSRF risk, but this should be implemented if:
- Cookies are used for authentication
- Session-based auth is added
- Compliance requirements mandate it

---

## 3. API Improvements

### 3.1 Implement Pagination
**Priority:** ⚠️ **HIGH**

**Current State:**
- `get_all()` methods return all records without pagination
- Will cause performance issues as data grows
- No pagination in list endpoints

**Recommendations:**
```python
# app/core/schemas.py
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class PageParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    size: int = Field(20, ge=1, le=100, description="Items per page (max 100)")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

class PageResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: list[T] = Field(default_factory=list)
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page")
    size: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")
    
    @classmethod
    def create(cls, items: list[T], total: int, page: int, size: int):
        pages = (total + size - 1) // size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

# Update base repository
class BaseRepository:
    async def get_paginated(
        self,
        page: int = 1,
        size: int = 20,
        filter_criteria: dict | None = None,
        load_options: list | None = None,
        order_by = None
    ) -> tuple[list[T], int]:
        """Get paginated results and total count"""
        query = select(self.model)
        
        if filter_criteria:
            for key, value in filter_criteria.items():
                query = query.where(getattr(self.model, key) == value)
        
        if load_options:
            query = query.options(*load_options)
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # Get paginated results
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        
        return items, total

# Update router
@router.get("/areas")
async def list_areas(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    area_service: AreaServiceDep = Depends()
) -> PageResponse[AreaResponse]:
    items, total = await area_service.get_paginated_areas(page, size)
    return PageResponse.create(items, total, page, size)
```

**Implementation Checklist:**
```
☐ Create PageParams and PageResponse schemas
☐ Add get_paginated method to BaseRepository
☐ Update service layer methods
☐ Update all list endpoints to use pagination
☐ Add sorting support (order_by parameter)
☐ Add cursor-based pagination for infinite scroll (optional)
☐ Update frontend to handle paginated responses
```

**Benefits:**
- Scalability for large datasets
- Better API performance
- Reduced memory usage
- Improved user experience

---

### 3.2 Add Filtering and Sorting
**Priority:** 🔶 **MEDIUM**

**Current State:**
- Limited filtering options
- No sorting capabilities
- Hard to query specific data

**Recommendations:**
```python
# app/core/schemas.py
class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class FilterParams(BaseModel):
    """Generic filter parameters"""
    search: str | None = Field(None, description="Search term")
    sort_by: str | None = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")

# Domain-specific filters
class AreaFilterParams(FilterParams):
    is_verified: bool | None = None
    parent_area_id: UUID | None = None
    created_by: UUID | None = None

class LandmarkFilterParams(FilterParams):
    area_id: UUID | None = None
    difficulty: int | None = None
    is_verified: bool | None = None

# Update repository
class BaseRepository:
    def _apply_filters(self, query, filter_params: FilterParams):
        """Apply filters to query"""
        if hasattr(filter_params, "search") and filter_params.search:
            # Implement search logic per model
            pass
        
        # Apply field filters
        for field, value in filter_params.dict(exclude_unset=True).items():
            if value is not None and hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        
        return query
    
    def _apply_sorting(self, query, sort_by: str, sort_order: SortOrder):
        """Apply sorting to query"""
        if sort_by and hasattr(self.model, sort_by):
            column = getattr(self.model, sort_by)
            if sort_order == SortOrder.DESC:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        return query

# Update endpoints
@router.get("/areas")
async def list_areas(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    filters: AreaFilterParams = Depends(),
    area_service: AreaServiceDep = Depends()
):
    items, total = await area_service.get_filtered_areas(page, size, filters)
    return PageResponse.create(items, total, page, size)
```

**Implementation Checklist:**
```
☐ Create filter parameter schemas
☐ Add filtering logic to repository
☐ Add sorting logic to repository
☐ Update service layer
☐ Update all list endpoints
☐ Add full-text search for text fields (optional)
☐ Document filter options in OpenAPI
```

**Benefits:**
- Better data discovery
- Flexible querying
- Improved API usability
- Support for complex use cases

---

### 3.3 Enhance OpenAPI Documentation
**Priority:** 🔵 **LOW**

**Current State:**
- Basic OpenAPI documentation auto-generated
- Missing detailed descriptions
- No examples for complex schemas

**Recommendations:**
```python
# Add detailed descriptions to endpoints
@router.post(
    "/areas",
    response_model=AreaReturn,
    summary="Create a new area",
    description="""
    Create a new geographic area. Areas can be hierarchical with parent areas.
    
    **Permissions:**
    - Any authenticated user can create an area
    - Newly created areas start as unverified
    - Superusers can verify areas
    
    **Notes:**
    - Name must be unique within the parent area
    - If parent_area_id is provided, it must exist
    """,
    responses={
        201: {"description": "Area created successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Authentication required"},
        404: {"description": "Parent area not found"},
    }
)
async def create_area(...):
    pass

# Add examples to schemas
class AreaCreate(BaseModel):
    name: str = Field(
        ...,
        description="Name of the area",
        example="Downtown Los Angeles"
    )
    description: str | None = Field(
        None,
        description="Detailed description of the area",
        example="Historic downtown district with landmarks"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Downtown Los Angeles",
                "description": "Historic downtown district",
                "parent_area_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }

# Customize OpenAPI schema
app = FastAPI(
    title="PicASpot API",
    description="""
    PicASpot is a location-based discovery and achievement platform.
    Users can discover landmarks, unlock achievements, and share their experiences.
    
    ## Authentication
    Most endpoints require authentication using JWT bearer tokens.
    Use the `/auth/login` endpoint to obtain a token.
    
    ## Rate Limiting
    Authentication endpoints are rate-limited to prevent abuse:
    - Login: 5 requests per minute
    - Registration: 5 requests per minute
    
    ## Pagination
    List endpoints support pagination with `page` and `size` parameters.
    """,
    version="1.0.0",
    contact={
        "name": "PicASpot Team",
        "email": "support@picaspot.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)
```

**Implementation Checklist:**
```
☐ Add detailed descriptions to all endpoints
☐ Add examples to request/response schemas
☐ Document error responses
☐ Add API overview documentation
☐ Document authentication flow
☐ Add code examples for common operations
☐ Generate client SDKs (optional)
```

---

## 4. Performance & Scalability

### 4.1 Implement Caching Strategy
**Priority:** 🔶 **MEDIUM**

**Current State:**
- No caching implemented
- Database queries on every request
- Redis available but underutilized

**Recommendations:**
```python
# app/core/cache.py
from functools import wraps
import json
import hashlib
from typing import Any, Callable

from app.database.redis import get_redis_client

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(
    prefix: str,
    ttl: int = 300,  # 5 minutes default
    key_builder: Callable | None = None
):
    """Decorator to cache function results in Redis"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                key = f"{prefix}:{key_builder(*args, **kwargs)}"
            else:
                key = f"{prefix}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            redis = await get_redis_client()
            cached_value = await redis.get(key)
            
            if cached_value:
                return json.loads(cached_value)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await redis.setex(
                key,
                ttl,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

# Usage in service layer
class AreaService:
    @cached(prefix="area", ttl=600)  # Cache for 10 minutes
    async def get_area_by_id(self, area_id: UUID) -> AreaResponse:
        area = await self.area_repository.get_by_id(area_id)
        if not area:
            raise NotFoundError("Area not found")
        return AreaResponse.model_validate_with_timezone(area, self.timezone)
    
    async def update_area(self, area_id: UUID, data: AreaUpdate):
        # Update area
        result = await self._update_area_logic(area_id, data)
        
        # Invalidate cache
        redis = await get_redis_client()
        await redis.delete(f"area:{area_id}")
        
        return result

# Cache frequently accessed data
@cached(prefix="areas:verified", ttl=3600)  # 1 hour
async def get_verified_areas():
    # Expensive query that doesn't change often
    pass
```

**Caching Strategy:**
```
☐ Cache individual resource lookups (area, landmark, user)
☐ Cache expensive aggregations and counts
☐ Cache verified areas/landmarks lists
☐ Cache user profile data
☐ Implement cache invalidation on updates
☐ Add cache warming for popular data
☐ Monitor cache hit rates
☐ Use Redis TTL for automatic expiration
```

**Cache Invalidation Patterns:**
- **Time-based:** TTL expiration (simplest)
- **Event-based:** Invalidate on updates
- **Pattern-based:** Delete by key pattern
- **Tag-based:** Group related cache entries

**Benefits:**
- Reduced database load
- Faster response times
- Better scalability
- Cost savings (fewer DB queries)

---

### 4.2 Add Database Connection Monitoring
**Priority:** 🔵 **LOW**

**Current State:**
- Connection pooling configured
- No monitoring or alerting

**Recommendations:**
```python
# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    """Expose metrics for monitoring"""
    pool = engine.pool
    return {
        "database": {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow()
        },
        "redis": {
            "connected": await check_redis_health()
        }
    }

# Add slow query logging
import time

class QueryTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        if duration > 1.0:  # Log queries over 1 second
            logger.warning(
                f"Slow request: {request.method} {request.url.path}",
                extra={"duration": duration}
            )
        
        return response
```

---

## 5. Background Job Improvements

### 5.1 Add Retry Logic and Error Handling
**Priority:** 🔶 **MEDIUM**

**Current State:**
- Celery tasks have no retry logic
- Failed tasks are not tracked
- No dead letter queue

**Recommendations:**
```python
# app/celery/tasks/email_tasks/tasks.py
from celery import Task
from celery.exceptions import MaxRetriesExceededError

class EmailTask(Task):
    """Base task with error handling"""
    autoretry_for = (SMTPException, ConnectionError)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True  # Exponential backoff
    retry_backoff_max = 600  # Max 10 minutes
    retry_jitter = True  # Add randomness to prevent thundering herd

@celery.task(
    bind=True,
    base=EmailTask,
    name="send_verification_email"
)
def user_verify_mail_event(
    self,
    recipient: str,
    link: str,
    username: str
):
    try:
        logger.info(f"Sending verification email to {recipient}")
        message = create_message(
            recipients=[recipient],
            subject=f"{settings.PROJECT_NAME} | Verify Your Email",
            body={
                "verification_link": link,
                "username": username,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "year": str(datetime.now().year),
            },
        )
        async_to_sync(mail.send_message)(message, "verify.html")
        logger.info(f"Verification email sent to {recipient}")
        
    except Exception as exc:
        logger.error(
            f"Failed to send email to {recipient}: {exc}",
            exc_info=True
        )
        
        try:
            raise self.retry(exc=exc, countdown=60)  # Retry after 60 seconds
        except MaxRetriesExceededError:
            # Send to dead letter queue or alert admins
            logger.critical(
                f"Max retries exceeded for email to {recipient}",
                extra={"recipient": recipient, "username": username}
            )
            # TODO: Store in failed_emails table or send alert

# Add periodic task to clean up old tokens
from celery.schedules import crontab

@celery.task(name="cleanup_expired_tokens")
def cleanup_expired_tokens():
    """Remove expired tokens from Redis (runs daily)"""
    logger.info("Starting token cleanup")
    # Implement cleanup logic
    pass

# Configure periodic tasks
celery.conf.beat_schedule = {
    'cleanup-tokens-daily': {
        'task': 'cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}
```

**Implementation Checklist:**
```
☐ Add base task class with error handling
☐ Configure retry logic for email tasks
☐ Add exponential backoff
☐ Log task failures
☐ Create failed task tracking table
☐ Add dead letter queue handling
☐ Implement periodic cleanup tasks
☐ Monitor task queue length
☐ Set up alerts for task failures
```

---

## 6. Authorization & Access Control

### 6.1 Implement Role-Based Access Control (RBAC)
**Priority:** 🔶 **MEDIUM**

**Current State:**
- Only `is_superuser` boolean flag
- No granular permissions
- All-or-nothing access control

**Recommendations:**
```python
# app/auth/models.py
from enum import Enum as PyEnum

class RoleEnum(str, PyEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

class PermissionEnum(str, PyEnum):
    # Area permissions
    AREA_CREATE = "area:create"
    AREA_READ = "area:read"
    AREA_UPDATE_OWN = "area:update:own"
    AREA_UPDATE_ANY = "area:update:any"
    AREA_DELETE_OWN = "area:delete:own"
    AREA_DELETE_ANY = "area:delete:any"
    AREA_VERIFY = "area:verify"
    
    # Landmark permissions
    LANDMARK_CREATE = "landmark:create"
    LANDMARK_READ = "landmark:read"
    LANDMARK_UPDATE_OWN = "landmark:update:own"
    LANDMARK_UPDATE_ANY = "landmark:update:any"
    LANDMARK_DELETE_OWN = "landmark:delete:own"
    LANDMARK_DELETE_ANY = "landmark:delete:any"
    LANDMARK_VERIFY = "landmark:verify"
    
    # User permissions
    USER_READ = "user:read"
    USER_UPDATE_OWN = "user:update:own"
    USER_UPDATE_ANY = "user:update:any"
    USER_DELETE_ANY = "user:delete:any"

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles"
    )
    users: Mapped[list["User"]] = relationship(back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    
    roles: Mapped[list["Role"]] = relationship(
        secondary="role_permissions",
        back_populates="permissions"
    )

class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"),
        primary_key=True
    )

# Update User model
class User(Base):
    # ... existing fields ...
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1)  # Default to USER
    role: Mapped["Role"] = relationship(back_populates="users")

# app/auth/dependencies.py
def require_permission(permission: PermissionEnum):
    """Dependency to check user has specific permission"""
    async def check_permission(current_user: CurrentUserDep):
        user_permissions = [
            p.name for p in current_user.role.permissions
        ]
        
        if permission.value not in user_permissions:
            raise ForbiddenError(
                f"Permission '{permission.value}' required"
            )
        
        return current_user
    
    return Depends(check_permission)

# Usage in endpoints
@router.delete("/areas/{area_id}")
async def delete_area(
    area_id: UUID,
    current_user: Annotated[
        User,
        require_permission(PermissionEnum.AREA_DELETE_ANY)
    ]
):
    # Only users with AREA_DELETE_ANY permission can access
    pass

# Seed default roles and permissions
async def seed_roles_and_permissions():
    """Create default roles and permissions"""
    # USER role
    user_role = Role(
        name="user",
        permissions=[
            Permission(name=PermissionEnum.AREA_CREATE),
            Permission(name=PermissionEnum.AREA_READ),
            Permission(name=PermissionEnum.AREA_UPDATE_OWN),
            Permission(name=PermissionEnum.AREA_DELETE_OWN),
            # ... other user permissions
        ]
    )
    
    # MODERATOR role (can verify content)
    moderator_role = Role(
        name="moderator",
        permissions=user_role.permissions + [
            Permission(name=PermissionEnum.AREA_VERIFY),
            Permission(name=PermissionEnum.LANDMARK_VERIFY),
            # ... other moderator permissions
        ]
    )
    
    # ADMIN role (all permissions)
    admin_role = Role(
        name="admin",
        permissions=[Permission(name=p) for p in PermissionEnum]
    )
```

**Implementation Checklist:**
```
☐ Create Role, Permission, and RolePermission models
☐ Create database migration
☐ Seed default roles and permissions
☐ Update User model with role relationship
☐ Create permission checking dependencies
☐ Update endpoints to use permission checks
☐ Migrate is_superuser to admin role
☐ Add role management endpoints (admin only)
☐ Add permission management endpoints (admin only)
```

**Default Roles:**
- **user:** Can create and manage own content
- **moderator:** Can verify content, moderate reports
- **admin:** Full access to all features

---

## 7. Data Management

### 7.1 Implement Soft Deletes
**Priority:** 🔵 **LOW**

**Current State:**
- Hard deletes with CASCADE
- No data recovery capability
- Risk of accidental data loss

**Recommendations:**
```python
# app/database/mixins.py
class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        nullable=True,
        index=True,
        default=None
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True
    )
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
    
    def soft_delete(self, user_id: uuid.UUID):
        """Mark entity as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = user_id
    
    def restore(self):
        """Restore soft-deleted entity"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

# Update models
class Area(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "areas"
    # ... existing fields ...

# Update repository to filter out deleted items by default
class BaseRepository:
    async def get_by_id(
        self,
        entity_id: Any,
        include_deleted: bool = False
    ) -> T | None:
        query = select(self.model).where(self.model.id == entity_id)
        
        if hasattr(self.model, "is_deleted") and not include_deleted:
            query = query.where(self.model.is_deleted == False)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def soft_delete(self, entity_id: Any, user_id: UUID) -> bool:
        """Soft delete an entity"""
        obj = await self.get_by_id(entity_id, include_deleted=False)
        if not obj:
            return False
        
        if hasattr(obj, "soft_delete"):
            obj.soft_delete(user_id)
            await self.session.commit()
            return True
        
        # Fallback to hard delete if not soft-deletable
        return await self.delete(entity_id)
    
    async def restore(self, entity_id: Any) -> bool:
        """Restore a soft-deleted entity"""
        obj = await self.get_by_id(entity_id, include_deleted=True)
        if not obj or not obj.is_deleted:
            return False
        
        obj.restore()
        await self.session.commit()
        return True

# Add admin endpoints for data recovery
@router.post("/admin/areas/{area_id}/restore")
async def restore_area(
    area_id: UUID,
    current_user: SuperuserDep
):
    """Restore a soft-deleted area (admin only)"""
    success = await area_repository.restore(area_id)
    if not success:
        raise NotFoundError("Area not found or not deleted")
    return {"message": "Area restored successfully"}
```

**Implementation Checklist:**
```
☐ Create SoftDeleteMixin
☐ Add soft delete fields to models
☐ Create migration
☐ Update repository methods
☐ Update service layer to use soft delete
☐ Add restore endpoints (admin only)
☐ Add permanent delete endpoints (admin only)
☐ Periodic cleanup of old soft-deleted records
```

**Benefits:**
- Data recovery capability
- Audit trail preservation
- Compliance with data retention policies
- User error protection

---

### 7.2 Implement Audit Logging
**Priority:** 🔵 **LOW**

**Current State:**
- Basic operation logging
- No comprehensive audit trail
- Hard to track who changed what

**Recommendations:**
```python
# app/audit/models.py
class AuditAction(str, PyEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    VERIFY = "verify"

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(index=True)
    entity_type: Mapped[str | None] = mapped_column(index=True)  # "area", "landmark", etc.
    entity_id: Mapped[str | None] = mapped_column(index=True)
    changes: Mapped[dict | None] = mapped_column(JSON)  # Before/after values
    ip_address: Mapped[str | None]
    user_agent: Mapped[str | None]
    
    user: Mapped["User"] = relationship()

# app/audit/service.py
class AuditService:
    async def log_action(
        self,
        user_id: UUID | None,
        action: AuditAction,
        entity_type: str | None = None,
        entity_id: str | None = None,
        changes: dict | None = None,
        request: Request | None = None
    ):
        """Log an audit event"""
        audit_entry = {
            "user_id": user_id,
            "action": action.value,
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id else None,
            "changes": changes,
        }
        
        if request:
            audit_entry["ip_address"] = request.client.host
            audit_entry["user_agent"] = request.headers.get("user-agent")
        
        await self.audit_repository.create(audit_entry)

# Usage in service layer
async def update_area(self, area_id: UUID, data: AreaUpdate, user: User):
    old_area = await self.area_repository.get_by_id(area_id)
    updated_area = await self.area_repository.update(area_id, data.dict())
    
    # Log the change
    await self.audit_service.log_action(
        user_id=user.id,
        action=AuditAction.UPDATE,
        entity_type="area",
        entity_id=area_id,
        changes={
            "before": old_area.dict(),
            "after": updated_area.dict()
        }
    )
    
    return updated_area

# Add audit log viewing endpoints
@router.get("/admin/audit-logs")
async def get_audit_logs(
    page: int = 1,
    size: int = 50,
    user_id: UUID | None = None,
    action: AuditAction | None = None,
    entity_type: str | None = None,
    current_user: SuperuserDep = Depends()
):
    """View audit logs (admin only)"""
    # Implement filtering and pagination
    pass
```

---

## 8. Monitoring & Observability

### 8.1 Add Prometheus Metrics
**Priority:** 🔵 **LOW**

**Current State:**
- Basic health check endpoint
- No metrics collection
- No performance monitoring

**Recommendations:**
```python
# Install: uv add prometheus-client

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_database_connections',
    'Number of active database connections'
)

celery_task_duration = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration',
    ['task_name']
)

# Middleware to collect metrics
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Update database pool metrics
@app.on_event("startup")
async def update_db_metrics():
    while True:
        pool = engine.pool
        active_connections.set(pool.checkedout())
        await asyncio.sleep(15)  # Update every 15 seconds
```

**Grafana Dashboard:**
- HTTP request rate and latency
- Error rate by endpoint
- Database connection pool usage
- Celery task queue length and duration
- Redis hit/miss ratio
- API rate limit hits

---

## 9. Developer Experience

### 9.1 Add Development Tools
**Priority:** 🔵 **LOW**

**Recommendations:**
```
☐ Add database seeding script for development
☐ Add faker-based test data generation
☐ Create Makefile or justfile for common commands
☐ Add pre-commit hooks (ruff, mypy, tests)
☐ Add development documentation
☐ Create API client examples
☐ Add Postman/Insomnia collection
```

**Example Makefile:**
```makefile
.PHONY: help install test lint format migrate seed docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"
	@echo "  make migrate    - Run database migrations"
	@echo "  make seed       - Seed database with test data"

install:
	uv sync --extra test

test:
	uv run pytest -v --cov=app

lint:
	uv run ruff check .

format:
	uv run ruff format .

migrate:
	uv run alembic upgrade head

seed:
	uv run python -m app.scripts.seed_data

docker-up:
	docker compose up -d

docker-down:
	docker compose down
```

---

## 10. Priority Implementation Roadmap

### Phase 1: Critical (Week 1-2)
**Focus: Testing & Token Management**

1. ✅ Implement comprehensive test suite
   - Unit tests for services
   - Integration tests for endpoints
   - >70% code coverage target

2. ✅ Implement refresh token mechanism
   - Database table for refresh tokens
   - Token rotation
   - Logout with revocation

3. ✅ Add pagination to all list endpoints
   - PageParams and PageResponse
   - Update repository layer
   - Update all list endpoints

### Phase 2: High Priority (Week 3-4)
**Focus: Security & Performance**

4. ✅ Security headers middleware
   - XSS protection
   - Clickjacking protection
   - HSTS headers

5. ✅ Implement caching strategy
   - Cache individual resources
   - Cache aggregations
   - Cache invalidation

6. ✅ Add filtering and sorting
   - Filter parameters
   - Sort parameters
   - Search functionality

### Phase 3: Medium Priority (Week 5-6)
**Focus: Resilience & Access Control**

7. ✅ Background job improvements
   - Retry logic
   - Error handling
   - Dead letter queue

8. ✅ RBAC implementation
   - Role and Permission models
   - Permission checking
   - Role management

9. ✅ CI/CD pipeline
   - GitHub Actions
   - Automated testing
   - Deployment automation

### Phase 4: Nice to Have (Ongoing)
**Focus: Monitoring & Polish**

10. ✅ Prometheus metrics
11. ✅ Audit logging
12. ✅ Soft deletes
13. ✅ Enhanced documentation
14. ✅ Development tools

---

## Conclusion

This recommendations document outlines the remaining work needed to bring the PicASpot backend to production-grade quality. Many foundational best practices are already implemented (see `features.md`). 

**Immediate Focus Areas:**
1. **Testing** - Critical for confidence in deployments
2. **Refresh Tokens** - Important for user experience
3. **Pagination** - Essential for scalability

**Next Steps:**
1. Review and prioritize recommendations with the team
2. Create GitHub issues for each recommendation
3. Estimate effort for each item
4. Create sprint plan for implementation
5. Update this document as items are completed

**Maintenance:**
- Review this document quarterly
- Update as new best practices emerge
- Move completed items to features.md
- Keep both documents in sync

---

**Document Version:** 2.0  
**Last Reviewed:** 2025-11-30  
**Next Review:** 2026-02-28

