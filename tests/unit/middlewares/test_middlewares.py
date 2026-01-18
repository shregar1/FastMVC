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

    @pytest.mark.asyncio
    @patch('middlewares.request_context.ulid_new')
    async def test_dispatch_sets_request_urn(self, mock_ulid):
        """Test dispatch sets request URN."""
        mock_ulid.return_value.str = "test-urn-12345"
        
        app = MagicMock()
        middleware = RequestContextMiddleware(app)
        
        request = MagicMock()
        request.state = MagicMock()
        
        response = MagicMock()
        response.headers = {}
        
        async def call_next(req):
            return response
        
        result = await middleware.dispatch(request, call_next)
        
        assert request.state.urn == "test-urn-12345"

    @pytest.mark.asyncio
    @patch('middlewares.request_context.ulid_new')
    async def test_dispatch_sets_process_time(self, mock_ulid):
        """Test dispatch sets process time header."""
        mock_ulid.return_value.str = "test-urn"
        
        app = MagicMock()
        middleware = RequestContextMiddleware(app)
        
        request = MagicMock()
        request.state = MagicMock()
        
        response = MagicMock()
        response.headers = {}
        
        async def call_next(req):
            return response
        
        result = await middleware.dispatch(request, call_next)
        
        assert "X-Process-Time" in result.headers


class TestAuthenticationMiddleware:
    """Tests for AuthenticationMiddleware."""

    @pytest.fixture
    def mock_app(self):
        """Create mock app."""
        return MagicMock()

    @pytest.mark.asyncio
    @patch('middlewares.authetication.unprotected_routes', {'/health', '/docs'})
    @patch('middlewares.authetication.callback_routes', set())
    @patch('middlewares.authetication.logger')
    async def test_unprotected_route_passes_through(self, mock_logger, mock_app):
        """Test unprotected routes pass through without auth."""
        from middlewares.authetication import AuthenticationMiddleware
        
        middleware = AuthenticationMiddleware(mock_app)
        
        request = MagicMock()
        request.state = MagicMock()
        request.state.urn = "test-urn"
        request.url.path = "/health"
        request.method = "GET"
        
        expected_response = MagicMock()
        
        async def call_next(req):
            return expected_response
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == expected_response

    @pytest.mark.asyncio
    @patch('middlewares.authetication.unprotected_routes', set())
    @patch('middlewares.authetication.callback_routes', set())
    @patch('middlewares.authetication.logger')
    async def test_options_request_passes_through(self, mock_logger, mock_app):
        """Test OPTIONS requests pass through."""
        from middlewares.authetication import AuthenticationMiddleware
        from http import HTTPMethod
        
        middleware = AuthenticationMiddleware(mock_app)
        
        request = MagicMock()
        request.state = MagicMock()
        request.state.urn = "test-urn"
        request.url.path = "/api/protected"
        request.method = HTTPMethod.OPTIONS
        
        expected_response = MagicMock()
        
        async def call_next(req):
            return expected_response
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == expected_response

    @pytest.mark.asyncio
    @patch('middlewares.authetication.unprotected_routes', set())
    @patch('middlewares.authetication.callback_routes', set())
    @patch('middlewares.authetication.logger')
    async def test_missing_token_returns_unauthorized(self, mock_logger, mock_app):
        """Test missing token returns 401."""
        from middlewares.authetication import AuthenticationMiddleware
        
        middleware = AuthenticationMiddleware(mock_app)
        
        request = MagicMock()
        request.state = MagicMock()
        request.state.urn = "test-urn"
        request.url.path = "/api/protected"
        request.method = "GET"
        request.headers = {}
        request.headers.get = MagicMock(return_value=None)
        
        async def call_next(req):
            return MagicMock()
        
        result = await middleware.dispatch(request, call_next)
        
        assert result.status_code == 401

    @pytest.mark.asyncio
    @patch('middlewares.authetication.unprotected_routes', set())
    @patch('middlewares.authetication.callback_routes', set())
    @patch('middlewares.authetication.logger')
    async def test_invalid_token_format_returns_unauthorized(self, mock_logger, mock_app):
        """Test invalid token format returns 401."""
        from middlewares.authetication import AuthenticationMiddleware
        
        middleware = AuthenticationMiddleware(mock_app)
        
        request = MagicMock()
        request.state = MagicMock()
        request.state.urn = "test-urn"
        request.url.path = "/api/protected"
        request.method = "GET"
        request.headers = {"authorization": "InvalidFormat token"}
        request.headers.get = MagicMock(return_value="InvalidFormat token")
        
        async def call_next(req):
            return MagicMock()
        
        result = await middleware.dispatch(request, call_next)
        
        assert result.status_code == 401

    @pytest.mark.asyncio
    @patch('middlewares.authetication.unprotected_routes', set())
    @patch('middlewares.authetication.callback_routes', set())
    @patch('middlewares.authetication.logger')
    @patch('middlewares.authetication.JWTUtility')
    @patch('middlewares.authetication.UserRepository')
    @patch('middlewares.authetication.db_session')
    async def test_valid_token_with_user_passes(self, mock_db, mock_repo_class, mock_jwt_class, mock_logger, mock_app):
        """Test valid token with existing user passes."""
        from middlewares.authetication import AuthenticationMiddleware
        
        # Setup JWT mock
        mock_jwt = MagicMock()
        mock_jwt.decode_token.return_value = {"user_id": 1, "user_urn": "user-urn-123"}
        mock_jwt_class.return_value = mock_jwt
        
        # Setup repo mock
        mock_repo = MagicMock()
        mock_repo.retrieve_record_by_id_and_is_logged_in.return_value = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        middleware = AuthenticationMiddleware(mock_app)
        
        request = MagicMock()
        request.state = MagicMock()
        request.state.urn = "test-urn"
        request.url.path = "/api/protected"
        request.method = "GET"
        request.headers = {"authorization": "Bearer valid-token"}
        request.headers.get = MagicMock(return_value="Bearer valid-token")
        
        expected_response = MagicMock()
        
        async def call_next(req):
            return expected_response
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == expected_response
        assert request.state.user_id == 1
        assert request.state.user_urn == "user-urn-123"

    @pytest.mark.asyncio
    @patch('middlewares.authetication.unprotected_routes', set())
    @patch('middlewares.authetication.callback_routes', set())
    @patch('middlewares.authetication.logger')
    @patch('middlewares.authetication.JWTUtility')
    @patch('middlewares.authetication.UserRepository')
    @patch('middlewares.authetication.db_session')
    async def test_valid_token_user_not_logged_in(self, mock_db, mock_repo_class, mock_jwt_class, mock_logger, mock_app):
        """Test valid token but user not logged in returns 401."""
        from middlewares.authetication import AuthenticationMiddleware
        
        # Setup JWT mock
        mock_jwt = MagicMock()
        mock_jwt.decode_token.return_value = {"user_id": 1, "user_urn": "user-urn-123"}
        mock_jwt_class.return_value = mock_jwt
        
        # Setup repo mock - user not found (not logged in)
        mock_repo = MagicMock()
        mock_repo.retrieve_record_by_id_and_is_logged_in.return_value = None
        mock_repo_class.return_value = mock_repo
        
        middleware = AuthenticationMiddleware(mock_app)
        
        request = MagicMock()
        request.state = MagicMock()
        request.state.urn = "test-urn"
        request.url.path = "/api/protected"
        request.method = "GET"
        request.headers = {"authorization": "Bearer valid-token"}
        request.headers.get = MagicMock(return_value="Bearer valid-token")
        
        async def call_next(req):
            return MagicMock()
        
        result = await middleware.dispatch(request, call_next)
        
        assert result.status_code == 401

    @pytest.mark.asyncio
    @patch('middlewares.authetication.unprotected_routes', set())
    @patch('middlewares.authetication.callback_routes', set())
    @patch('middlewares.authetication.logger')
    @patch('middlewares.authetication.JWTUtility')
    async def test_jwt_decode_error_returns_unauthorized(self, mock_jwt_class, mock_logger, mock_app):
        """Test JWT decode error returns 401."""
        from middlewares.authetication import AuthenticationMiddleware
        
        # Setup JWT mock to raise exception
        mock_jwt = MagicMock()
        mock_jwt.decode_token.side_effect = Exception("Invalid token")
        mock_jwt_class.return_value = mock_jwt
        
        middleware = AuthenticationMiddleware(mock_app)
        
        request = MagicMock()
        request.state = MagicMock()
        request.state.urn = "test-urn"
        request.url.path = "/api/protected"
        request.method = "GET"
        request.headers = {"authorization": "Bearer invalid-token"}
        request.headers.get = MagicMock(return_value="Bearer invalid-token")
        
        async def call_next(req):
            return MagicMock()
        
        result = await middleware.dispatch(request, call_next)
        
        assert result.status_code == 401
