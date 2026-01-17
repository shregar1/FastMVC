# FastMVC

A production-grade FastAPI application framework implementing the Model-View-Controller (MVC) architectural pattern with comprehensive security, logging, and scalability features.

## Features

- **MVC Architecture**: Clean separation of concerns with controllers, services, and repositories
- **Type Safety**: Full Pydantic validation and type hints throughout
- **Security**: JWT authentication, rate limiting, security headers, input validation
- **Database**: SQLAlchemy ORM with PostgreSQL support
- **Caching**: Redis integration for caching and rate limiting
- **Logging**: Structured logging with Loguru
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fastmvc
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Configure database and cache:
```bash
# Edit config/db/config.json
# Edit config/cache/config.json
```

6. Run the application:
```bash
python app.py
```

Or with uvicorn:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| POST | `/user/register` | User registration | No |
| POST | `/user/login` | User authentication | No |
| POST | `/user/logout` | Session termination | Yes |

## Project Structure

```
fastmvc/
├── abstractions/        # Base classes and interfaces
│   ├── controller.py    # IController base class
│   ├── service.py       # IService base class
│   ├── repository.py    # IRepository base class
│   ├── dependency.py    # IDependency base class
│   ├── utility.py       # IUtility base class
│   ├── factory.py       # IFactory base class
│   └── error.py         # IError base class
│
├── config/              # Configuration files
│   ├── db/              # Database configuration
│   ├── cache/           # Redis configuration
│   └── security/        # Security configuration
│
├── configurations/      # Configuration loaders
│   ├── db.py           # Database config loader
│   ├── cache.py        # Cache config loader
│   └── security.py     # Security config loader
│
├── constants/           # Application constants
│   ├── api_lk.py       # API logical keys
│   ├── api_status.py   # Response status values
│   ├── default.py      # Default values
│   ├── payload_type.py # Content types
│   ├── regular_expression.py  # Validation patterns
│   └── db/             # Database constants
│
├── controllers/         # HTTP request handlers
│   ├── apis/           # API versioned controllers
│   │   └── v1/         # Version 1 controllers
│   └── user/           # User controllers
│       ├── login.py    # Login endpoint
│       ├── logout.py   # Logout endpoint
│       └── register.py # Registration endpoint
│
├── dependencies/        # FastAPI dependency injection
│   ├── db.py           # Database session dependency
│   ├── cache.py        # Redis dependency
│   ├── repositories/   # Repository factories
│   ├── services/       # Service factories
│   └── utilities/      # Utility factories
│
├── dtos/               # Data Transfer Objects
│   ├── base.py         # Enhanced base model
│   ├── configurations/ # Config DTOs
│   ├── requests/       # Request DTOs
│   └── responses/      # Response DTOs
│
├── errors/             # Custom exceptions
│   ├── bad_input_error.py
│   ├── not_found_error.py
│   └── unexpected_response_error.py
│
├── middlewares/        # Request/response middleware
│   ├── authetication.py    # JWT authentication
│   ├── rate_limit.py       # Rate limiting
│   ├── request_context.py  # URN and timing
│   └── security_headers.py # Security headers
│
├── models/             # SQLAlchemy ORM models
│   └── user.py         # User model
│
├── repositories/       # Data access layer
│   └── user.py         # User repository
│
├── services/           # Business logic layer
│   ├── apis/           # API services
│   └── user/           # User services
│       ├── login.py    # Login service
│       ├── logout.py   # Logout service
│       └── registration.py  # Registration service
│
├── utilities/          # Helper utilities
│   ├── dictionary.py   # Dict manipulation
│   ├── jwt.py          # JWT operations
│   └── validation.py   # Input validation
│
├── app.py              # Application entry point
├── start_utils.py      # Startup configuration
├── setup.py            # Package setup
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Docker Compose
```

## Architecture

### Request Flow

```
HTTP Request
    │
    ▼
┌─────────────────────────────────────┐
│         Middleware Stack            │
│  (Context → Rate Limit → Auth →    │
│   Security Headers)                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│           Controller                │
│  (Validate → Call Service → Format)│
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│            Service                  │
│    (Business Logic → Return DTO)   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│           Repository                │
│     (Database Operations)           │
└─────────────────────────────────────┘
```

### Response Format

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

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `SECRET_KEY` | JWT signing secret | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | 1440 |
| `BCRYPT_SALT` | Password hashing salt | Required |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Rate limit/min | 60 |
| `RATE_LIMIT_REQUESTS_PER_HOUR` | Rate limit/hour | 1000 |

### Database Configuration

`config/db/config.json`:
```json
{
    "user_name": "postgres",
    "password": "your-password",
    "host": "localhost",
    "port": 5432,
    "database": "fastmvc",
    "connection_string": "postgresql://{user_name}:{password}@{host}:{port}/{database}"
}
```

### Cache Configuration

`config/cache/config.json`:
```json
{
    "host": "localhost",
    "port": 6379,
    "password": "your-redis-password"
}
```

## Security Features

- **JWT Authentication**: Secure token-based auth with configurable expiry
- **Password Hashing**: Bcrypt password hashing
- **Rate Limiting**: Sliding window algorithm with configurable limits
- **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- **Input Validation**: SQL injection, XSS, path traversal detection
- **Request Tracing**: Unique URN for each request

## Docker

Build and run with Docker:

```bash
docker-compose up --build
```

Or build standalone:

```bash
docker build -t fastmvc .
docker run -p 8000:8000 fastmvc
```

## Development

### Adding a New Endpoint

1. Create request/response DTOs in `dtos/`
2. Create service in `services/`
3. Create controller in `controllers/`
4. Create dependency factories in `dependencies/`
5. Register route in controller's `__init__.py`

### Running Tests

```bash
pytest tests/
```

## Documentation

Each module has its own README.md with detailed documentation:

- [Abstractions](abstractions/README.md)
- [Configurations](configurations/README.md)
- [Constants](constants/README.md)
- [Controllers](controllers/README.md)
- [Dependencies](dependencies/README.md)
- [DTOs](dtos/README.md)
- [Errors](errors/README.md)
- [Middlewares](middlewares/README.md)
- [Models](models/README.md)
- [Repositories](repositories/README.md)
- [Services](services/README.md)
- [Utilities](utilities/README.md)

## License

MIT License - see [LICENSE](LICENSE) for details.
