# Testing Implementation Plan for PicASpot Backend

## Executive Summary

**AI Implementation Directive**: This document provides mandatory instructions for AI agents to implement a comprehensive testing strategy for the PicASpot backend API. AI agents MUST follow this plan exactly, ensuring all tests run within Docker containers only, after initializing the full project stack via Docker Compose. Follow industry best practices for FastAPI applications with PostgreSQL/PostGIS, Redis, Celery, and Docker environments. The plan includes unit, integration, and end-to-end tests with proper fixtures, mocking strategies, and CI/CD integration.

---

## Current State Analysis

### Technology Stack
- **Framework**: FastAPI (0.122.0+) with Python 3.14
- **Database**: PostgreSQL 18 with PostGIS 3.6 extension (using SQLAlchemy 2.0 + AsyncPG)
- **Cache/Queue**: Redis 8.2.2
- **Task Queue**: Celery 5.5.3 with Flower monitoring
- **Container Orchestration**: Docker Compose
- **Testing Tools Already Configured**: pytest, pytest-asyncio, pytest-cov, pytest-mock, httpx, aiosqlite, faker

### Existing Setup
✅ **Strengths**:
- Test dependencies already in `pyproject.toml` (dev group)
- Pytest configuration in place with coverage settings
- Test markers defined (unit, integration, e2e, slow)
- Async test support configured
- Code coverage reporting configured (HTML + terminal)

❌ **Gaps**:
- No actual test files implemented (only `__init__.py` in tests/)
- No test fixtures defined
- No test database configuration
- No Docker Compose test environment
- No CI/CD pipeline configuration
- No test data factories setup

### Application Architecture
- **Modules**: auth, user, area, landmark, unlock (implied)
- **Patterns**: Repository pattern, Service layer, Dependency injection
- **Features**: JWT authentication, rate limiting, email verification, password reset, geospatial queries
- **Background Tasks**: Celery tasks for email sending
- **Middleware**: Rate limiter, request logging, timezone handling, CORS

---

## Testing Strategy Overview

### Test Pyramid Distribution
```
                    /\
                   /  \
                  / E2E \          ~10% - Full system tests
                 /--------\
                /          \
               / Integration \     ~30% - API + DB + Redis tests
              /--------------\
             /                \
            /   Unit Tests     \   ~60% - Pure logic tests
           /--------------------\
```

### Test Levels

#### 1. Unit Tests (60% of test suite)
- **Scope**: Individual functions, methods, and classes in isolation
- **Isolation**: Mock all external dependencies (DB, Redis, external APIs)
- **Speed**: Fast (<1ms per test)
- **Coverage Target**: 80%+ for business logic

#### 2. Integration Tests (30% of test suite)
- **Scope**: Multiple components working together
- **Database**: Real PostgreSQL with PostGIS (test instance)
- **Redis**: Real Redis instance
- **Speed**: Moderate (10-100ms per test)
- **Coverage Target**: Critical user flows and data persistence

#### 3. End-to-End Tests (10% of test suite)
- **Scope**: Full system through HTTP API
- **Environment**: Complete Docker Compose stack
- **Speed**: Slow (100ms-1s per test)
- **Coverage Target**: Main user journeys and critical paths

---

## Implementation Phases

### Phase 1: Foundation Setup (Week 1)

#### 1.1 Test Infrastructure

**File: `tests/conftest.py`**
- Global pytest fixtures and configuration
- Test database setup/teardown
- Test Redis setup/teardown
- Factory fixtures for test data
- Authentication helper fixtures
- Async client fixtures

**File: `tests/fixtures/__init__.py`**
- Modular fixture organization

**File: `tests/fixtures/database.py`**
- `test_engine`: Async SQLAlchemy engine for test DB
- `test_session_maker`: Session factory for tests
- `test_session`: Per-test database session
- `apply_migrations`: Alembic migration fixture

**File: `tests/fixtures/redis.py`**
- `test_redis_client`: Redis client for tests
- `redis_cleanup`: Redis data cleanup between tests

**File: `tests/fixtures/app.py`**
- `test_app`: FastAPI application with test overrides
- `async_client`: AsyncClient from httpx for API testing
- `authenticated_client`: Client with valid JWT token

**File: `tests/factories/user_factory.py`**
- User model factories using Faker
- Different user roles (admin, regular user)
- Email verification states

**File: `tests/factories/landmark_factory.py`**
- Landmark model factories with geospatial data
- Valid coordinate generation

**File: `tests/factories/area_factory.py`**
- Area model factories with polygons
- Hierarchical area relationships

#### 1.3 Test Utilities

**File: `tests/utils/helpers.py`**
- `create_test_user()`: Helper to create users in tests
- `generate_token()`: Generate JWT tokens for authentication
- `create_geojson_point()`: Helper for valid GeoJSON data
- `assert_datetime_equal()`: Compare datetimes with timezone handling

**File: `tests/utils/assertions.py`**
- Custom assertion helpers for API responses
- GeoJSON validation helpers
- Pagination assertion helpers

### Phase 2: Unit Tests (Weeks 2-3)

#### 2.1 Core Module Tests

**File: `tests/unit/core/test_exceptions.py`**
- Test custom exception classes
- Verify HTTP status codes
- Test exception details and headers

**File: `tests/unit/core/test_utils.py`**
- Test utility functions
- Password validation
- Email validation
- Datetime utilities

**File: `tests/unit/core/test_response.py`**
- Test response schema structures
- Timezone conversion in responses

#### 2.2 Authentication & Security Tests

**File: `tests/unit/auth/test_security.py`**
- Password hashing verification
- Password verification (correct/incorrect)
- JWT token creation
- JWT token decoding
- Token expiration validation
- Verification token creation/validation
- Token blacklisting logic

**File: `tests/unit/auth/test_service.py`**
- `test_register_new_user()`: Happy path
- `test_register_duplicate_email()`: Should raise BadRequestError
- `test_register_duplicate_username()`: Should raise BadRequestError
- `test_login_valid_credentials()`: Returns tokens
- `test_login_invalid_password()`: Raises AuthenticationError
- `test_login_unverified_email()`: Should handle appropriately
- `test_verify_email_valid_token()`: Marks user as verified
- `test_verify_email_invalid_token()`: Raises error
- `test_password_reset_request()`: Creates reset token
- `test_password_reset_complete()`: Updates password

**File: `tests/unit/auth/test_schemas.py`**
- Schema validation tests
- Email format validation
- Password complexity requirements
- Response model serialization

#### 2.3 Repository Tests

**File: `tests/unit/repositories/test_base_repository.py`**
- Mock SQLAlchemy session
- Test CRUD operations with mocked results
- Test query building
- Test timezone handling in base repository

**File: `tests/unit/repositories/test_user_repository.py`**
- `test_get_by_email_or_username()`: Query logic
- Test with mocked database results
- Edge cases (None results, multiple matches)

**File: `tests/unit/repositories/test_landmark_repository.py`**
- Geospatial query mocking
- Nearby landmark queries
- Distance calculations

**File: `tests/unit/repositories/test_area_repository.py`**
- Hierarchical queries
- Parent-child relationships
- Cascade delete logic

#### 2.4 Service Layer Tests

**File: `tests/unit/user/test_service.py`**
- User profile updates
- User deletion
- Permission checks
- Mock repository calls

**File: `tests/unit/landmark/test_service.py`**
- Landmark creation validation
- Coordinate validation
- Authorization checks (creator/admin)
- Mock repository and dependencies

**File: `tests/unit/area/test_service.py`**
- Area creation with geometry
- Polygon validation
- Hierarchical area logic
- Mock geospatial operations

#### 2.5 Middleware Tests

**File: `tests/unit/middleware/test_ratelimiter.py`**
- Rate limit enforcement
- Redis mock for rate limit counters
- Path-specific rate limiting
- Rate limit header verification

**File: `tests/unit/middleware/test_timezone.py`**
- Timezone extraction from headers
- Default timezone fallback
- Invalid timezone handling

**File: `tests/unit/middleware/test_logging.py`**
- Request logging verification
- Sensitive data masking
- Performance timing

### Phase 3: Integration Tests (Weeks 4-5)

#### 3.1 Database Integration Tests

**File: `tests/integration/test_database.py`**
- Database connection pooling
- Transaction rollback behavior
- Concurrent session handling
- Connection health checks

**File: `tests/integration/repositories/test_user_repository_integration.py`**
- Real database CRUD operations
- Transaction commits and rollbacks
- Unique constraint violations
- Foreign key relationships

**File: `tests/integration/repositories/test_landmark_repository_integration.py`**
- PostGIS spatial queries
- ST_DWithin queries for nearby landmarks
- Geometry storage and retrieval
- Spatial indexing verification

**File: `tests/integration/repositories/test_area_repository_integration.py`**
- Polygon storage with PostGIS
- Area overlap detection
- Point-in-polygon queries
- Hierarchical cascading deletes

#### 3.2 Redis Integration Tests

**File: `tests/integration/test_redis.py`**
- Redis connection and health checks
- Token storage and retrieval
- Token expiration
- Rate limit counter operations
- Cache invalidation

#### 3.3 Service Integration Tests

**File: `tests/integration/auth/test_auth_service_integration.py`**
- Full registration flow with DB
- Email verification with Redis tokens
- Password reset with Redis tokens
- Login with DB user lookup
- Token refresh flow

**File: `tests/integration/user/test_user_service_integration.py`**
- User profile updates persisted to DB
- User deletion with cascade effects
- Permission checks with real roles

**File: `tests/integration/landmark/test_landmark_service_integration.py`**
- Landmark creation with geospatial data
- Landmark search with distance calculations
- Authorization with real user sessions
- Landmark updates and deletions

**File: `tests/integration/area/test_area_service_integration.py`**
- Area creation with polygons
- Nested area relationships
- Area deletion with children
- Area update validations

#### 3.4 Celery Task Tests

**File: `tests/integration/celery/test_email_tasks.py`**
- Mock email backend
- Verify task execution
- Task retry logic
- Task failure handling
- Email template rendering

**File: `tests/integration/celery/test_celery_worker.py`**
- Worker startup and connection
- Task routing
- Task result storage

### Phase 4: End-to-End API Tests (Week 6)

#### 4.1 Authentication Flow E2E

**File: `tests/e2e/test_auth_flow.py`**
- Complete user registration journey
- Email verification click simulation
- Login and token usage
- Password reset complete flow
- Token refresh flow
- Rate limiting on auth endpoints

#### 4.2 User Management E2E

**File: `tests/e2e/test_user_management.py`**
- User profile retrieval
- User profile update
- User deletion
- Admin user operations
- Permission boundaries

#### 4.3 Landmark CRUD E2E

**File: `tests/e2e/test_landmark_crud.py`**
- Create landmark with authentication
- Retrieve landmark details
- Update own landmark
- Delete own landmark
- Search landmarks by proximity
- Pagination testing

#### 4.4 Area Management E2E

**File: `tests/e2e/test_area_management.py`**
- Create area with polygon
- Create nested areas
- Retrieve area hierarchy
- Update area boundaries
- Delete area with children
- Area search and filtering

#### 4.5 Error Handling E2E

**File: `tests/e2e/test_error_scenarios.py`**
- 404 Not Found responses
- 401 Unauthorized access
- 403 Forbidden operations
- 400 Bad Request validation
- 422 Unprocessable Entity
- 429 Rate limit exceeded
- 500 Internal server errors

#### 4.6 Health and Monitoring E2E

**File: `tests/e2e/test_health_checks.py`**
- `/health` endpoint with healthy services
- `/health` endpoint with unhealthy DB
- `/health` endpoint with unhealthy Redis
- Root endpoint accessibility

### Phase 5: Performance and Load Tests (Week 7)

#### 5.1 Performance Tests

**File: `tests/performance/test_api_performance.py`**
- Response time benchmarks
- Database query count optimization
- N+1 query detection
- Endpoint latency profiling

**File: `tests/performance/test_geospatial_performance.py`**
- Spatial query performance
- Large dataset handling
- Index utilization verification

#### 5.2 Load Tests (Optional - Locust/K6)

**File: `tests/load/locustfile.py`**
- Concurrent user simulation
- Read/write ratio testing
- Peak load handling
- Resource utilization monitoring

### Phase 6: CI/CD Integration (Week 8)

#### 6.1 GitHub Actions Workflow

**File: `.github/workflows/test.yml`**
```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgis/postgis:18-3.6-alpine
        env:
          POSTGRES_DB: test_picaspot
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:8.2.2-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      
      - name: Install dependencies
        run: |
          cd src/backend
          uv sync
      
      - name: Run database migrations
        run: |
          cd src/backend
          uv run alembic upgrade head
        env:
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
          POSTGRES_DB: test_picaspot
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
      
      - name: Run unit tests
        run: |
          cd src/backend
          uv run pytest tests/unit -v --cov=app --cov-report=xml
      
      - name: Run integration tests
        run: |
          cd src/backend
          uv run pytest tests/integration -v --cov=app --cov-append --cov-report=xml
      
      - name: Run e2e tests
        run: |
          cd src/backend
          uv run pytest tests/e2e -v --cov=app --cov-append --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./src/backend/coverage.xml
          flags: backend
          name: backend-coverage
      
      - name: Check coverage threshold
        run: |
          cd src/backend
          uv run pytest --cov=app --cov-report=term --cov-fail-under=80
```

#### 6.2 Pre-commit Hooks

**File: `.pre-commit-config.yaml`**
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: bash -c 'cd src/backend && uv run pytest tests/unit -v'
        language: system
        pass_filenames: false
        always_run: true
      
      - id: pytest-check
        name: Check test coverage
        entry: bash -c 'cd src/backend && uv run pytest --cov=app --cov-report=term --cov-fail-under=70'
        language: system
        pass_filenames: false
        always_run: true
```

#### 6.3 Test Scripts

**File: `src/backend/scripts/run_tests.sh`**
```bash
#!/bin/bash
# Run all tests with coverage

set -e

echo "Starting test databases..."
docker-compose -f docker-compose.test.yaml up -d

echo "Waiting for databases to be ready..."
sleep 5

echo "Running migrations..."
uv run alembic upgrade head

echo "Running unit tests..."
uv run pytest tests/unit -v -m "unit" --cov=app --cov-report=html --cov-report=term

echo "Running integration tests..."
uv run pytest tests/integration -v -m "integration" --cov=app --cov-append --cov-report=html --cov-report=term

echo "Running e2e tests..."
uv run pytest tests/e2e -v -m "e2e" --cov=app --cov-append --cov-report=html --cov-report=term

echo "Stopping test databases..."
docker-compose -f docker-compose.test.yaml down

echo "Tests completed! Coverage report: htmlcov/index.html"
```

**File: `src/backend/scripts/run_tests.ps1`** (Windows PowerShell)
```powershell
# Run all tests with coverage

Write-Host "Starting test databases..." -ForegroundColor Green
docker-compose -f docker-compose.test.yaml up -d

Write-Host "Waiting for databases to be ready..." -ForegroundColor Green
Start-Sleep -Seconds 5

Write-Host "Running migrations..." -ForegroundColor Green
uv run alembic upgrade head

Write-Host "Running unit tests..." -ForegroundColor Green
uv run pytest tests/unit -v -m "unit" --cov=app --cov-report=html --cov-report=term

Write-Host "Running integration tests..." -ForegroundColor Green
uv run pytest tests/integration -v -m "integration" --cov=app --cov-append --cov-report=html --cov-report=term

Write-Host "Running e2e tests..." -ForegroundColor Green
uv run pytest tests/e2e -v -m "e2e" --cov=app --cov-append --cov-report=html --cov-report=term

Write-Host "Stopping test databases..." -ForegroundColor Green
docker-compose -f docker-compose.test.yaml down

Write-Host "Tests completed! Coverage report: htmlcov/index.html" -ForegroundColor Green
```

**File: `src/backend/scripts/run_unit_tests.sh`** (Quick unit tests only)
```bash
#!/bin/bash
uv run pytest tests/unit -v -m "unit" --cov=app --cov-report=term-missing
```

**File: `src/backend/scripts/run_unit_tests.ps1`** (Windows)
```powershell
uv run pytest tests/unit -v -m "unit" --cov=app --cov-report=term-missing
```

---

## Testing Best Practices

### 1. Test Naming Convention
```python
# Pattern: test_<function_name>_<scenario>_<expected_result>
def test_register_with_valid_data_creates_user():
    pass

def test_login_with_invalid_password_raises_authentication_error():
    pass

def test_get_landmark_by_id_returns_correct_landmark():
    pass
```

### 2. Arrange-Act-Assert (AAA) Pattern
```python
async def test_create_landmark(test_session):
    # Arrange
    user = await create_test_user(test_session)
    landmark_data = LandmarkCreate(
        name="Test Landmark",
        latitude=51.5074,
        longitude=-0.1278
    )
    
    # Act
    result = await landmark_service.create_landmark(landmark_data, user.id)
    
    # Assert
    assert result.name == "Test Landmark"
    assert result.latitude == 51.5074
```

### 3. Fixture Scope Management
```python
# Module-scoped for expensive setup (DB connection)
@pytest.fixture(scope="module")
async def test_engine():
    pass

# Function-scoped for clean state per test (default)
@pytest.fixture(scope="function")
async def test_session():
    pass
```

### 4. Async Test Handling
```python
# Use pytest-asyncio with asyncio_mode="auto"
@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 200
```

### 5. Parameterized Tests
```python
@pytest.mark.parametrize("email,username,should_pass", [
    ("valid@email.com", "validuser", True),
    ("invalid-email", "validuser", False),
    ("valid@email.com", "ab", False),  # Too short
])
async def test_registration_validation(email, username, should_pass):
    pass
```

### 6. Mock External Services
```python
@pytest.fixture
def mock_email_service(mocker):
    """Mock Celery email tasks"""
    return mocker.patch("app.celery.tasks.user_verify_mail_event.delay")

async def test_register_sends_verification_email(mock_email_service):
    # Test registration
    assert mock_email_service.called
```

### 7. Database Transaction Isolation
```python
@pytest.fixture
async def test_session():
    """Each test gets a fresh session with rollback"""
    async with async_session_maker() as session:
        async with session.begin():
            yield session
            await session.rollback()  # Rollback after test
```

### 8. Test Data Factories
```python
class UserFactory:
    @staticmethod
    async def create(session, **kwargs):
        defaults = {
            "email": fake.email(),
            "username": fake.user_name(),
            "hashed_password": get_password_hash("password123"),
            "is_verified": True,
            "is_superuser": False,
        }
        defaults.update(kwargs)
        user = User(**defaults)
        session.add(user)
        await session.commit()
        return user
```

### 9. Authentication in Tests
```python
@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers for authenticated requests"""
    token = create_access_token(sub=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}

async def test_protected_endpoint(async_client, auth_headers):
    response = await async_client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
```

### 10. Geospatial Test Data
```python
def create_test_point(lat: float = 51.5074, lon: float = -0.1278):
    """Create valid GeoJSON point"""
    return {
        "type": "Point",
        "coordinates": [lon, lat]  # Note: GeoJSON is [lon, lat]
    }

def create_test_polygon():
    """Create valid GeoJSON polygon"""
    return {
        "type": "Polygon",
        "coordinates": [[
            [-0.1, 51.5],
            [-0.1, 51.6],
            [-0.2, 51.6],
            [-0.2, 51.5],
            [-0.1, 51.5]
        ]]
    }
```

---

## Test Coverage Goals

### Coverage Targets by Module

| Module | Unit Test Coverage | Integration Test Coverage | Total Target |
|--------|-------------------|---------------------------|--------------|
| `app/auth/` | 90% | 80% | 85%+ |
| `app/user/` | 85% | 75% | 80%+ |
| `app/landmark/` | 85% | 80% | 82%+ |
| `app/area/` | 85% | 80% | 82%+ |
| `app/core/` | 90% | 70% | 80%+ |
| `app/database/` | 75% | 85% | 80%+ |
| `app/middleware/` | 85% | 70% | 80%+ |
| `app/celery/` | 70% | 80% | 75%+ |
| **Overall** | **85%** | **78%** | **80%+** |

### Coverage Exclusions
- `__init__.py` files (imports only)
- `alembic/` migrations (tested via integration)
- `settings.py` (configuration)
- Type checking blocks (`if TYPE_CHECKING:`)
- Abstract base classes
- Unreachable code paths

---

## Testing Tools & Dependencies

### Core Testing Framework
- **pytest** (9.0.1+): Main testing framework
- **pytest-asyncio** (0.24.0+): Async test support
- **pytest-cov** (6.0.0+): Code coverage reporting
- **pytest-mock** (3.14.0+): Mocking and patching

### Additional Testing Tools
- **httpx** (0.28.0+): Async HTTP client for API testing
- **aiosqlite** (0.20.0+): SQLite async for lightweight testing (optional)
- **faker** (37.11.0+): Realistic fake data generation
- **freezegun**: Time mocking for datetime-dependent tests
- **pytest-xdist**: Parallel test execution
- **pytest-timeout**: Test timeout enforcement
- **pytest-env**: Environment variable management
- **factory-boy**: Advanced test data factories (optional)

### Code Quality Tools
- **ruff**: Linting and code formatting
- **mypy**: Static type checking
- **bandit**: Security vulnerability scanning
- **safety**: Dependency vulnerability checking

---

## Environment Configuration

### Test Environment Variables (`.env.test`)
```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=test_picaspot
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_PASSWORD=test_password

# Application
SECRET_KEY=test_secret_key_change_in_production_12345678901234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_SECONDS=3600
PROJECT_NAME=PicASpot Test
DOMAIN=localhost
BACKEND_DEBUG=true
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Email (Mock)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=test@example.com
SMTP_PASSWORD=test
EMAILS_FROM_EMAIL=noreply@picaspot.test
EMAIL_FROM_NAME=PicASpot Test
EMAIL_VERIFY_PATH=/verify
EMAIL_RESET_PASSWORD_PATH=/reset-password

# Service
SERVICE_NAME=test_backend

# Admin (disabled in tests)
ADMIN_EMAIL=false
ADMIN_PASSWORD=false
USER_EMAIL=false
USER_PASSWORD=false

# Ports
BACKEND_PORT_INTERNAL=8000
FLOWER_PORT_INTERNAL=5555
MAILHOG_UI_PORT_INTERNAL=8025
MAILHOG_PORT_INTERNAL=1025
REDIS_PORT_INTERNAL=6379
POSTGRES_PORT_INTERNAL=5432
HTTP_PORT=80
HTTPS_PORT=443
```

---

## Test Data Management

### Test Database Strategy

#### Option 1: Separate Test Database (Recommended)
- Use dedicated PostgreSQL instance for tests
- Run migrations before test suite
- Faster than SQLite for integration tests
- Supports PostGIS extensions
- Matches production environment

#### Option 2: In-Memory SQLite (Unit Tests Only)
- Fast for isolated unit tests
- No PostGIS support (limited for spatial features)
- Good for repository pattern tests without geospatial queries

#### Hybrid Approach (Recommended)
- **Unit tests**: Mock database or lightweight in-memory
- **Integration tests**: Real PostgreSQL with PostGIS
- **E2E tests**: Full Docker Compose environment

### Data Reset Strategies

#### Per-Test Cleanup
```python
@pytest.fixture(autouse=True)
async def clean_database(test_session):
    """Clean database after each test"""
    yield
    await test_session.rollback()
```

#### Transaction Rollback
```python
@pytest.fixture
async def test_session():
    async with async_session_maker() as session:
        async with session.begin():
            yield session
            await session.rollback()
```

#### Full Database Reset (Between Test Classes)
```python
@pytest.fixture(scope="class")
async def reset_database():
    """Drop and recreate all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
```

---

## Mocking Strategies

### 1. Database Mocking (Unit Tests)
```python
@pytest.fixture
def mock_session(mocker):
    session = mocker.AsyncMock()
    session.execute = mocker.AsyncMock()
    session.commit = mocker.AsyncMock()
    return session
```

### 2. Redis Mocking
```python
@pytest.fixture
def mock_redis(mocker):
    redis = mocker.AsyncMock()
    redis.get = mocker.AsyncMock(return_value=None)
    redis.setex = mocker.AsyncMock()
    return redis
```

### 3. External API Mocking
```python
@pytest.fixture
def mock_email_service(mocker):
    return mocker.patch("app.celery.tasks.email_tasks.tasks.user_verify_mail_event.delay")
```

### 4. Dependency Override (FastAPI)
```python
@pytest.fixture
def test_app(test_session):
    app.dependency_overrides[get_async_session] = lambda: test_session
    yield app
    app.dependency_overrides.clear()
```

---

## Common Test Scenarios

### Authentication Tests
- ✅ User registration with valid data
- ✅ Registration with duplicate email/username
- ✅ Email verification flow
- ✅ Login with valid credentials
- ✅ Login with invalid password
- ✅ Login with unverified email
- ✅ Token refresh flow
- ✅ Password reset request
- ✅ Password reset completion
- ✅ Access protected endpoints without token
- ✅ Access protected endpoints with expired token
- ✅ Access protected endpoints with invalid token
- ✅ Rate limiting on auth endpoints

### CRUD Operations Tests
- ✅ Create resource with valid data
- ✅ Create resource with invalid data
- ✅ Get resource by ID (exists)
- ✅ Get resource by ID (not found)
- ✅ Update resource (own resource)
- ✅ Update resource (not authorized)
- ✅ Delete resource (own resource)
- ✅ Delete resource (not authorized)
- ✅ List resources with pagination
- ✅ Filter and search resources

### Geospatial Tests
- ✅ Create landmark with valid coordinates
- ✅ Create landmark with invalid coordinates
- ✅ Search landmarks by proximity
- ✅ Calculate distance between points
- ✅ Point-in-polygon queries
- ✅ Area overlap detection
- ✅ Spatial index utilization

### Permission Tests
- ✅ Regular user access
- ✅ Superuser/admin access
- ✅ Resource ownership validation
- ✅ Cross-user resource access denial

### Error Handling Tests
- ✅ 400 Bad Request (validation errors)
- ✅ 401 Unauthorized (missing token)
- ✅ 403 Forbidden (insufficient permissions)
- ✅ 404 Not Found (resource doesn't exist)
- ✅ 422 Unprocessable Entity (semantic errors)
- ✅ 429 Too Many Requests (rate limit)
- ✅ 500 Internal Server Error (caught exceptions)

---

## Continuous Improvement

### Test Metrics to Track
- **Code Coverage**: Target 80%+ overall
- **Test Execution Time**: Unit <5s, Integration <30s, E2E <2min
- **Test Reliability**: Flaky test rate <1%
- **Test Count**: Track growth over time
- **Failure Rate**: Monitor CI/CD failures

### Test Maintenance
- Review and update tests with each feature
- Remove obsolete tests
- Refactor duplicate test logic into fixtures
- Keep test data factories up to date
- Document complex test scenarios

### Performance Optimization
- Run unit tests in parallel (pytest-xdist)
- Use test database in tmpfs for speed
- Cache test dependencies
- Profile slow tests and optimize
- Use appropriate fixture scopes

---

## Implementation Checklist

### Phase 1: Foundation ✅
- [ ] Create `tests/conftest.py` with base fixtures
- [ ] Create `tests/fixtures/` directory structure
- [ ] Implement database fixtures
- [ ] Implement Redis fixtures
- [ ] Implement app and client fixtures
- [ ] Create test data factories
- [ ] Create `docker-compose.test.yaml`
- [ ] Create `.env.test` file
- [ ] Create test utility helpers

### Phase 2: Unit Tests ✅
- [ ] Core module unit tests
- [ ] Authentication unit tests
- [ ] Repository unit tests (mocked)
- [ ] Service layer unit tests (mocked)
- [ ] Middleware unit tests
- [ ] Schema validation tests
- [ ] Utility function tests

### Phase 3: Integration Tests ✅
- [ ] Database integration tests
- [ ] Redis integration tests
- [ ] Repository integration tests (real DB)
- [ ] Service integration tests
- [ ] Celery task tests
- [ ] End-to-end auth flow tests

### Phase 4: E2E Tests ✅
- [ ] Complete API flow tests
- [ ] User management E2E tests
- [ ] Landmark CRUD E2E tests
- [ ] Area management E2E tests
- [ ] Error handling E2E tests
- [ ] Health check tests

### Phase 5: CI/CD ✅
- [ ] GitHub Actions workflow
- [ ] Pre-commit hooks
- [ ] Test scripts (Bash + PowerShell)
- [ ] Coverage reporting
- [ ] Badge integration

### Phase 6: Documentation ✅
- [ ] Test documentation in README
- [ ] Test writing guidelines
- [ ] Fixture usage documentation
- [ ] CI/CD documentation

---

## Expected Outcomes

### Immediate Benefits
1. **Bug Detection**: Catch regressions early in development
2. **Confidence**: Safe refactoring and feature additions
3. **Documentation**: Tests as living documentation
4. **Faster Development**: Rapid feedback on changes

### Long-term Benefits
1. **Code Quality**: Enforced through coverage requirements
2. **Maintainability**: Well-tested code is easier to modify
3. **Onboarding**: New developers understand system through tests
4. **Production Stability**: Fewer bugs reach production

### Success Metrics
- ✅ 80%+ code coverage achieved
- ✅ All tests passing in CI/CD
- ✅ Test suite runs in <5 minutes
- ✅ Zero critical bugs in production for 90 days
- ✅ Team confidence in making changes

---

## Resources and References

### Official Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

### Best Practices
- [Google Testing Blog](https://testing.googleblog.com/)
- [Martin Fowler - Testing Strategies](https://martinfowler.com/testing/)
- [Test Pyramid Concept](https://martinfowler.com/articles/practical-test-pyramid.html)

### Tools
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Faker](https://faker.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [httpx](https://www.python-httpx.org/)

---

## Conclusion

This comprehensive testing plan provides a structured approach to implementing a robust test suite for the PicASpot backend API. By following this plan, you will achieve:

1. **High code coverage** (80%+ target)
2. **Fast feedback loops** through automated testing
3. **Production confidence** with thorough integration tests
4. **Maintainable test code** using fixtures and factories
5. **CI/CD integration** for continuous quality assurance

The phased approach allows for incremental implementation over 8 weeks, with immediate value delivered in early phases. Start with Phase 1 foundation and unit tests, then progressively add integration and E2E tests as the infrastructure matures.

Remember: **Good tests are an investment that pays dividends through reduced bugs, faster development, and increased confidence in your codebase.**

---

## Contact & Support

For questions or clarifications on this testing plan:
- Review the official pytest and FastAPI testing documentation
- Consult the team lead or senior developer
- Reference existing test examples in the codebase
- Update this document as the project evolves

**Document Version**: 1.0  
**Last Updated**: 2025-12-01  
**Maintained By**: Development Team

---

## AI Implementation Instructions

**Critical Requirements for Test Execution:**

1. **Docker Environment Mandatory**: All tests MUST be executed exclusively within Docker containers. No tests shall run directly on the host system to ensure environment consistency and isolation.

2. **Project Initialization**: Before executing any tests, the entire project stack MUST be started using `docker-compose up`. This ensures all services (PostgreSQL, Redis, Celery, etc.) are running and properly configured.

3. **Containerized Test Commands**: Use Docker containers for all test runs. For example:
   - Run unit tests: `docker-compose exec backend uv run pytest tests/unit`
   - Run integration tests: `docker-compose exec backend uv run pytest tests/integration`
   - Run all tests: `docker-compose exec backend uv run pytest`

4. **Environment Consistency**: AI agents implementing tests must verify that the Docker Compose stack is active before proceeding with any test execution.

5. **No Host-Based Testing**: Under no circumstances should tests be run outside of the Docker environment, even for development or debugging purposes.

6. **CI/CD Alignment**: Ensure that CI/CD pipelines also run tests within Docker containers, mirroring the local development environment.
