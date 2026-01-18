"""
Tests for middleware classes.
"""

import pytest
import time
from unittest.mock import MagicMock, patch, AsyncMock
from http import HTTPStatus, HTTPMethod

from middlewares.security_headers import SecurityHeadersConfig, SecurityHeadersMiddleware
from middlewares.rate_limit import RateLimitConfig, RateLimitStore, RateLimitMiddleware
from middlewares.request_context import RequestContextMiddleware


class TestSecurityHeadersConfig:
    """Tests for SecurityHeadersConfig."""

    def test_default_initialization(self):
        """Test default configuration values."""
        config = SecurityHeadersConfig()
        assert config.enable_hsts is True
        assert config.enable_csp is True
        assert config.csp_report_only is False
        assert config.hsts_max_age == 31536000
        assert config.hsts_include_subdomains is True
        assert config.hsts_preload is False
        assert config.frame_options == "DENY"
        assert config.content_type_options == "nosniff"
        assert config.xss_protection == "1; mode=block"
        assert config.referrer_policy == "strict-origin-when-cross-origin"

    def test_custom_initialization(self):
        """Test custom configuration values."""
        config = SecurityHeadersConfig(
            enable_hsts=False,
            enable_csp=False,
            hsts_max_age=86400,
            frame_options="SAMEORIGIN"
        )
        assert config.enable_hsts is False
        assert config.enable_csp is False
        assert config.hsts_max_age == 86400
        assert config.frame_options == "SAMEORIGIN"

    def test_get_hsts_header_basic(self):
        """Test HSTS header generation."""
        config = SecurityHeadersConfig()
        header = config.get_hsts_header()
        assert "max-age=31536000" in header
        assert "includeSubDomains" in header

    def test_get_hsts_header_with_preload(self):
        """Test HSTS header with preload."""
        config = SecurityHeadersConfig(hsts_preload=True)
        header = config.get_hsts_header()
        assert "preload" in header

    def test_get_hsts_header_without_subdomains(self):
        """Test HSTS header without subdomains."""
        config = SecurityHeadersConfig(hsts_include_subdomains=False)
        header = config.get_hsts_header()
        assert "includeSubDomains" not in header

    def test_get_csp_header_name_normal(self):
        """Test CSP header name for normal mode."""
        config = SecurityHeadersConfig(csp_report_only=False)
        assert config.get_csp_header_name() == "Content-Security-Policy"

    def test_get_csp_header_name_report_only(self):
        """Test CSP header name for report-only mode."""
        config = SecurityHeadersConfig(csp_report_only=True)
        assert config.get_csp_header_name() == "Content-Security-Policy-Report-Only"


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware."""

    @pytest.fixture
    def app(self):
        """Create mock app."""
        return MagicMock()

    @pytest.fixture
    def middleware(self, app):
        """Create SecurityHeadersMiddleware instance."""
        return SecurityHeadersMiddleware(app)

    def test_initialization(self, middleware):
        """Test middleware initialization."""
        assert middleware.enable_hsts is True
        assert middleware.enable_csp is True
        assert middleware.x_frame_options == "DENY"
        assert middleware.x_content_type_options == "nosniff"

    def test_initialization_custom(self, app):
        """Test middleware with custom options."""
        middleware = SecurityHeadersMiddleware(
            app,
            enable_hsts=False,
            enable_csp=False,
            x_frame_options="SAMEORIGIN"
        )
        assert middleware.enable_hsts is False
        assert middleware.enable_csp is False
        assert middleware.x_frame_options == "SAMEORIGIN"

    def test_default_csp(self, middleware):
        """Test default CSP generation."""
        csp = middleware._get_default_csp()
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "style-src" in csp

    def test_default_permissions_policy(self, middleware):
        """Test default permissions policy generation."""
        policy = middleware._get_default_permissions_policy()
        assert "camera=()" in policy
        assert "microphone=()" in policy
        assert "geolocation=()" in policy

    @pytest.mark.asyncio
    async def test_dispatch_adds_headers(self, app):
        """Test dispatch adds security headers."""
        middleware = SecurityHeadersMiddleware(app)
        
        request = MagicMock()
        request.url.path = "/api/test"
        request.method = "GET"
        
        response = MagicMock()
        response.headers = {}
        
        async def call_next(req):
            return response
        
        result = await middleware.dispatch(request, call_next)
        
        assert "X-Frame-Options" in result.headers
        assert "X-Content-Type-Options" in result.headers
        assert "X-XSS-Protection" in result.headers
        assert "Referrer-Policy" in result.headers


class TestRateLimitConfig:
    """Tests for RateLimitConfig."""

    def test_default_initialization(self):
        """Test default configuration values."""
        config = RateLimitConfig()
        assert config.requests_per_minute > 0
        assert config.requests_per_hour > 0
        assert config.burst_limit > 0
        assert config.window_size > 0
        assert config.enable_sliding_window is True

    def test_custom_initialization(self):
        """Test custom configuration values."""
        config = RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=500,
            burst_limit=5,
            window_size=120
        )
        assert config.requests_per_minute == 30
        assert config.requests_per_hour == 500
        assert config.burst_limit == 5
        assert config.window_size == 120


class TestRateLimitStore:
    """Tests for RateLimitStore."""

    @pytest.fixture
    def store(self):
        """Create RateLimitStore instance."""
        return RateLimitStore()

    @pytest.mark.asyncio
    async def test_check_sliding_window_allowed(self, store):
        """Test sliding window allows requests under limit."""
        allowed, count = await store.check_sliding_window("test-key", 10, 60)
        assert allowed is True
        assert count == 1

    @pytest.mark.asyncio
    async def test_check_sliding_window_increments(self, store):
        """Test sliding window increments count."""
        await store.check_sliding_window("test-key", 10, 60)
        allowed, count = await store.check_sliding_window("test-key", 10, 60)
        assert allowed is True
        assert count == 2

    @pytest.mark.asyncio
    async def test_check_sliding_window_limit_exceeded(self, store):
        """Test sliding window blocks when limit exceeded."""
        for _ in range(5):
            await store.check_sliding_window("test-key", 5, 60)
        
        allowed, count = await store.check_sliding_window("test-key", 5, 60)
        assert allowed is False

    @pytest.mark.asyncio
    async def test_cleanup_old_entries(self, store):
        """Test cleanup removes old entries."""
        # Add an entry
        await store.check_sliding_window("old-key", 10, 60)
        
        # Cleanup should work without errors
        await store.cleanup_old_entries(max_age=0)


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware."""

    def test_rate_limit_config_initialization(self):
        """Test RateLimitConfig initialization."""
        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000
        )
        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000

    def test_rate_limit_store_initialization(self):
        """Test RateLimitStore initialization."""
        store = RateLimitStore()
        assert store is not None
        assert store._sliding_windows is not None


class TestRequestContextMiddleware:
    """Tests for RequestContextMiddleware."""

    def test_middleware_can_be_created(self):
        """Test RequestContextMiddleware can be instantiated."""
        app = MagicMock()
        middleware = RequestContextMiddleware(app)
        assert middleware is not None
        assert middleware.app == app

