"""
FastMVC Application Entry Point.

This is the main FastAPI application module that initializes the web server,
configures middleware, registers routes, and handles application lifecycle events.

Usage:
    Run directly:
        python app.py

    Or with uvicorn:
        uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Environment Variables:
    HOST: Server host address (default: 0.0.0.0)
    PORT: Server port (default: 8000)
    RATE_LIMIT_REQUESTS_PER_MINUTE: Rate limit per minute
    RATE_LIMIT_REQUESTS_PER_HOUR: Rate limit per hour
    RATE_LIMIT_BURST_LIMIT: Maximum burst requests

Endpoints:
    GET /health - Health check endpoint
    POST /user/login - User authentication
    POST /user/register - New user registration
    POST /user/logout - Session termination
"""

import os
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from http import HTTPStatus
from loguru import logger

from constants.default import Default
from controllers.user import router as UserRouter

from middlewares.authetication import AuthenticationMiddleware
from middlewares.rate_limit import (
    RateLimitMiddleware, RateLimitConfig
)
from middlewares.security_headers import (
    SecurityHeadersMiddleware,
    SecurityHeadersConfig
)
from middlewares.request_context import RequestContextMiddleware


# Initialize FastAPI application
app = FastAPI(
    title="FastMVC API",
    description="Production-grade FastAPI application with MVC architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Load environment variables
load_dotenv()
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
    os.getenv(
        "RATE_LIMIT_REQUESTS_PER_MINUTE",
        Default.RATE_LIMIT_REQUESTS_PER_MINUTE,
    )
)
RATE_LIMIT_REQUESTS_PER_HOUR: int = int(
    os.getenv(
        "RATE_LIMIT_REQUESTS_PER_HOUR",
        Default.RATE_LIMIT_REQUESTS_PER_HOUR,
    )
)
RATE_LIMIT_WINDOW_SECONDS: int = int(
    os.getenv(
        "RATE_LIMIT_WINDOW_SECONDS",
        Default.RATE_LIMIT_WINDOW_SECONDS,
    )
)
RATE_LIMIT_BURST_LIMIT: int = int(
    os.getenv(
        "RATE_LIMIT_BURST_LIMIT",
        Default.RATE_LIMIT_BURST_LIMIT,
    )
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Global exception handler for request validation errors.

    Transforms Pydantic validation errors into a structured JSON response
    format consistent with the application's error handling pattern.

    Args:
        request: The incoming FastAPI request object.
        exc: The RequestValidationError exception instance.

    Returns:
        JSONResponse: Structured error response with validation details.

    Response Format:
        {
            "transactionUrn": "urn:req:abc123",
            "responseMessage": "Bad or missing input.",
            "responseKey": "error_bad_input",
            "errors": [{"loc": [...], "msg": "...", "type": "..."}]
        }
    """
    logger.error(f"Validation error: {exc.errors()}")
    # Remove internal context from error messages
    for error in exc.errors():
        if "ctx" in error:
            error.pop("ctx")
    response_payload: dict = {
        "transactionUrn": getattr(request.state, "urn", None),
        "responseMessage": "Bad or missing input.",
        "responseKey": "error_bad_input",
        "errors": exc.errors(),
    }
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=response_payload,
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Used by load balancers, container orchestrators, and monitoring systems
    to verify the application is running and responsive.

    Returns:
        dict: {"status": "ok"} indicating healthy status.

    Example:
        >>> curl http://localhost:8000/health
        {"status": "ok"}
    """
    logger.info("Health check endpoint called")
    return {"status": "ok"}


# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Trusted Host Middleware - Prevents host header attacks
app.add_middleware(middleware_class=TrustedHostMiddleware, allowed_hosts=["*"])

# CORS Middleware - Cross-Origin Resource Sharing
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Custom Middleware Stack (order matters - last added = first executed)
logger.info("Initializing middleware stack")

# Security Headers Middleware - CSP, HSTS, X-Frame-Options, etc.
security_config = SecurityHeadersConfig(
    enable_hsts=True,
    enable_csp=True,
    hsts_max_age=31536000,
    hsts_include_subdomains=True
)
app.add_middleware(SecurityHeadersMiddleware, **security_config.__dict__)

# Rate Limiting Middleware - Protects against abuse
rate_limit_config = RateLimitConfig(
    requests_per_minute=RATE_LIMIT_REQUESTS_PER_MINUTE,
    requests_per_hour=RATE_LIMIT_REQUESTS_PER_HOUR,
    burst_limit=RATE_LIMIT_BURST_LIMIT,
    enable_sliding_window=True,
    enable_token_bucket=False
)
app.add_middleware(RateLimitMiddleware, config=rate_limit_config)

# Authentication Middleware - JWT validation
app.add_middleware(AuthenticationMiddleware)

# Request Context Middleware - URN generation and timing (must be first)
app.add_middleware(RequestContextMiddleware)

logger.info("Initialized middleware stack")

# =============================================================================
# ROUTER CONFIGURATION
# =============================================================================

logger.info("Initializing routers")
app.include_router(UserRouter, tags=["User"])
logger.info("Initialized routers")


# =============================================================================
# LIFECYCLE EVENTS
# =============================================================================

@app.on_event("startup")
async def on_startup():
    """
    Application startup event handler.

    Called when the FastAPI application starts. Use for:
    - Initializing database connections
    - Loading cached data
    - Starting background tasks
    - Logging startup information
    """
    logger.info("Application startup event triggered")
    logger.info(f"FastMVC API starting on {HOST}:{PORT}")


@app.on_event("shutdown")
async def on_shutdown():
    """
    Application shutdown event handler.

    Called when the FastAPI application shuts down. Use for:
    - Closing database connections
    - Flushing caches
    - Stopping background tasks
    - Cleanup operations
    """
    logger.info("Application shutdown event triggered")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
