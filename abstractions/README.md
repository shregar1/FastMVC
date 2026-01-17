# Abstractions

## Overview

The `abstractions` module provides base classes and interfaces that define the architectural contracts for the FastMVC framework. These abstractions enforce consistent patterns across all layers of the application.

## Purpose

In software engineering, **abstractions** promote:

- **Loose coupling**: Components depend on interfaces, not implementations
- **Testability**: Easy to mock dependencies for unit testing
- **Consistency**: Standardized patterns across the codebase
- **Extensibility**: New implementations can be added without modifying existing code

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Controllers                             │
│              (IController - Request handling)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Services                               │
│              (IService - Business logic)                     │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────┐  ┌─────────────────┐
│   Repositories  │  │  Utilities  │  │    Factories    │
│  (IRepository)  │  │  (IUtility) │  │   (IFactory)    │
└─────────────────┘  └─────────────┘  └─────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Database                               │
│                   (SQLAlchemy ORM)                           │
└─────────────────────────────────────────────────────────────┘
```

## Components

### IController (`controller.py`)

Base class for HTTP request handlers.

```python
from abstractions.controller import IController

class UserController(IController):
    async def validate_request(self, urn, user_urn, request_payload, ...):
        await super().validate_request(...)
        # Custom validation logic
```

**Key Features:**
- Request context tracking (URN, user info)
- Structured logging with request correlation
- Request validation hooks

### IService (`service.py`)

Base class for business logic services.

```python
from abstractions.service import IService

class UserRegistrationService(IService):
    def run(self, request_dto: RegistrationDTO) -> dict:
        # Business logic implementation
        return {"status": "success", "user_id": "..."}
```

**Key Features:**
- Abstract `run()` method for business logic
- Request context propagation
- Structured logging

### IRepository (`repository.py`)

Base class for data access layer.

```python
from abstractions.repository import IRepository

class UserRepository(IRepository):
    def __init__(self, session, **kwargs):
        super().__init__(model=UserModel, **kwargs)
        self.session = session
```

**Key Features:**
- Built-in CRUD operations
- LRU cache support for query results
- Execution time logging
- Soft delete support

### IDependency (`dependency.py`)

Base class for FastAPI dependency injection.

```python
from abstractions.dependency import IDependency

class DatabaseDependency(IDependency):
    def get_session(self):
        return self._session
```

**Key Features:**
- Request context propagation
- Structured logging
- Reusable across routes

### IFactory (`factory.py`)

Base class for Factory pattern implementation.

```python
from abstractions.factory import IFactory

class ServiceFactory(IFactory):
    def create_user_service(self) -> UserService:
        return UserService(urn=self.urn, ...)
```

**Key Features:**
- Object creation encapsulation
- Dependency wiring
- Request context propagation

### IUtility (`utility.py`)

Base class for utility/helper components.

```python
from abstractions.utility import IUtility

class JWTUtility(IUtility):
    def generate_token(self, payload: dict) -> str:
        # Token generation logic
        return token
```

**Key Features:**
- Cross-cutting functionality
- Request context awareness
- Structured logging

### IError (`error.py`)

Base exception class for application errors.

```python
from abstractions.error import IError

class NotFoundError(IError):
    def __init__(self, resource: str, **kwargs):
        super().__init__(**kwargs)
        self.resource = resource
        self.message = f"{resource} not found"
```

**Key Features:**
- Request context preservation
- Structured error logging
- Consistent error handling

## Common Properties

All abstractions share these common properties:

| Property | Type | Description |
|----------|------|-------------|
| `urn` | `str` | Unique Request Number for distributed tracing |
| `user_urn` | `str` | User's unique resource name |
| `api_name` | `str` | Name of the API endpoint |
| `user_id` | `str/int` | Database identifier of the user |
| `logger` | `Logger` | Structured logger bound with context |

## Best Practices

1. **Always call super().__init__()** in subclass constructors
2. **Use request context** for logging and tracing
3. **Implement abstract methods** as defined by the interface
4. **Keep business logic in services**, not controllers
5. **Use repositories for data access**, not direct queries in services

## File Structure

```
abstractions/
├── __init__.py          # Package exports
├── controller.py        # IController - HTTP request handling
├── dependency.py        # IDependency - FastAPI DI
├── error.py            # IError - Custom exceptions
├── factory.py          # IFactory - Object creation
├── repository.py       # IRepository - Data access
├── service.py          # IService - Business logic
├── utility.py          # IUtility - Helper functions
└── README.md           # This documentation
```
