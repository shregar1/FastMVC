# FastMVC

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade FastAPI framework implementing the Model-View-Controller (MVC) architectural pattern with comprehensive security, logging, and scalability features.

## ✨ Features

- **🏗️ MVC Architecture**: Clean separation of concerns with controllers, services, and repositories
- **🔐 Security**: JWT authentication, rate limiting, security headers, input validation
- **⚡ CLI Tool**: Generate projects and entities with `fastmvc` commands
- **🗄️ Database**: SQLAlchemy ORM with PostgreSQL + Alembic migrations
- **💾 Caching**: Redis integration with decorator-based caching
- **📝 Type Safety**: Full Pydantic v2 validation and type hints
- **📊 Logging**: Structured logging with Loguru
- **📚 Documentation**: Auto-generated OpenAPI/Swagger docs

## 🚀 Quick Start

### Installation

```bash
pip install pyfastmvc
```

### Create a New Project

```bash
# Generate a new FastMVC project
fastmvc generate my_api

# Navigate to project
cd my_api

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start infrastructure (PostgreSQL + Redis)
docker-compose up -d

# Run database migrations
fastmvc migrate upgrade

# Start the server
python -m uvicorn app:app --reload
```

Your API is now running at http://localhost:8000 with docs at http://localhost:8000/docs 🎉

## 🛠️ CLI Commands

### Project Generation

```bash
# Create new project
fastmvc generate my_project

# With options
fastmvc generate my_project --output-dir ~/projects --git --venv --install
```

### Entity Generation (CRUD Scaffolding)

```bash
# Generate complete CRUD for an entity
cd my_project
fastmvc add entity Product

# This creates:
# - models/product.py
# - repositories/product.py
# - services/product/
# - controllers/product/
# - dtos/requests/product/
# - tests/unit/models/test_product.py
```

### Database Migrations

```bash
# Generate migration from model changes
fastmvc migrate generate "add product table"

# Apply all pending migrations
fastmvc migrate upgrade

# Rollback last migration
fastmvc migrate downgrade

# Show migration status
fastmvc migrate status

# Show migration history
fastmvc migrate history
```

### Other Commands

```bash
# Show framework info
fastmvc info

# Show version
fastmvc version
```

## 📁 Project Structure

```
my_project/
├── abstractions/       # Base interfaces & contracts
│   ├── controller.py   # IController base class
│   ├── service.py      # IService base class
│   ├── repository.py   # IRepository base class
│   └── ...
│
├── config/             # JSON configuration files
│   ├── db/            # Database configuration
│   ├── cache/         # Redis configuration
│   └── security/      # Security configuration
│
├── configurations/     # Configuration loaders
│
├── constants/          # Application constants
│
├── controllers/        # HTTP request handlers (routes)
│   └── user/          # User endpoints
│       ├── login.py
│       ├── logout.py
│       └── register.py
│
├── dependencies/       # FastAPI dependency injection
│
├── dtos/              # Data Transfer Objects
│   ├── base.py        # Enhanced base model with validation
│   ├── requests/      # Request DTOs
│   └── responses/     # Response DTOs
│
├── errors/            # Custom exception classes
│
├── middlewares/       # Request/response middleware
│   ├── authentication.py  # JWT authentication
│   ├── rate_limit.py      # Rate limiting
│   ├── request_context.py # Request tracking
│   └── security_headers.py # Security headers
│
├── migrations/        # Alembic database migrations
│   ├── env.py
│   └── versions/
│
├── models/            # SQLAlchemy ORM models
│
├── repositories/      # Data access layer
│
├── services/          # Business logic layer
│
├── tests/             # Test suite
│
├── utilities/         # Helper utilities
│   ├── cache.py       # Redis caching with decorators
│   ├── dictionary.py  # Dict manipulation
│   ├── jwt.py         # JWT operations
│   └── validation.py  # Input validation
│
├── app.py             # FastAPI application entry
├── start_utils.py     # Startup configuration
├── alembic.ini        # Alembic configuration
├── docker-compose.yml # Docker services
└── requirements.txt   # Dependencies
```

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| POST | `/user/register` | User registration | No |
| POST | `/user/login` | User authentication | No |
| POST | `/user/logout` | Session termination | Yes |
| GET | `/docs` | Swagger UI | No |
| GET | `/redoc` | ReDoc | No |

## 🔄 Request Flow

```
HTTP Request
    │
    ▼
┌─────────────────────────────────────┐
│         Middleware Stack            │
│  RequestContext → RateLimit → Auth  │
│         → SecurityHeaders           │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│           Controller                │
│   (Validate Request → Call Service  │
│         → Format Response)          │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│            Service                  │
│     (Business Logic → Use Cache     │
│          → Return DTO)              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│           Repository                │
│      (Database Operations)          │
└─────────────────────────────────────┘
```

## 📋 Response Format

All API responses follow this structure:

```json
{
    "transactionUrn": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "status": "SUCCESS",
    "responseMessage": "Operation completed successfully",
    "responseKey": "success_operation",
    "data": { }
}
```

## 💾 Caching

FastMVC includes a powerful caching utility with decorators:

```python
from utilities.cache import CacheUtility

cache = CacheUtility(redis_client, default_ttl=3600)

# Cache function results
@cache.cached(ttl=300, prefix="user")
async def get_user(user_id: int):
    return await db.fetch_user(user_id)

# Invalidate cache after modifications
@cache.invalidate("user:*")
async def update_user(user_id: int, data: dict):
    return await db.update_user(user_id, data)

# Manual cache operations
cache.set("my_key", {"data": "value"}, ttl=300)
data = cache.get("my_key")
cache.delete("my_key")
cache.delete_pattern("user:*")
```

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based auth with configurable expiry
- **Password Hashing**: Bcrypt password hashing
- **Rate Limiting**: Sliding window algorithm with configurable limits
- **Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **Input Validation**: SQL injection, XSS, path traversal detection
- **Request Tracing**: Unique URN for each request

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT signing secret | Required |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `JWT_EXPIRATION_HOURS` | Token expiry | 24 |
| `BCRYPT_SALT` | Password hashing salt | Required |
| `DATABASE_HOST` | PostgreSQL host | localhost |
| `DATABASE_PORT` | PostgreSQL port | 5432 |
| `DATABASE_NAME` | Database name | fastmvc |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |

## 🐳 Docker

```bash
# Build and run all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific tests
pytest tests/unit/services/ -v
```

## 📖 Documentation

Each module has its own README.md with detailed documentation:

- [Abstractions](abstractions/README.md) - Base interfaces
- [Configurations](configurations/README.md) - Config loaders
- [Constants](constants/README.md) - Application constants
- [Controllers](controllers/README.md) - Route handlers
- [Dependencies](dependencies/README.md) - DI factories
- [DTOs](dtos/README.md) - Data transfer objects
- [Errors](errors/README.md) - Custom exceptions
- [Middlewares](middlewares/README.md) - Request middleware
- [Migrations](migrations/README.md) - Database migrations
- [Models](models/README.md) - SQLAlchemy models
- [Repositories](repositories/README.md) - Data access
- [Services](services/README.md) - Business logic
- [Utilities](utilities/README.md) - Helper functions
- [CLI](fastmvc_cli/README.md) - Command line interface

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ using [FastAPI](https://fastapi.tiangolo.com/)
