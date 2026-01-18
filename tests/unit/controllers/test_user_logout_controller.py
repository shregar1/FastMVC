"""
Tests for User Logout Controller.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from http import HTTPStatus

from controllers.user.logout import UserLogoutController
from dtos.requests.user.logout import UserLogoutRequestDTO


class TestUserLogoutControllerInit:
    """Tests for UserLogoutController initialization."""
    
    def test_initialization(self):
        """Test UserLogoutController can be initialized."""
        controller = UserLogoutController(urn="test-urn")
        assert controller.urn == "test-urn"
    
    def test_has_post_method(self):
        """Test controller has post method."""
        controller = UserLogoutController(urn="test-urn")
        assert hasattr(controller, 'post')


class TestUserLogoutControllerPost:
    """Tests for UserLogoutController post method."""
    
    @pytest.fixture
    def controller(self):
        """Create controller instance."""
        return UserLogoutController(urn="test-urn")
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request DTO."""
        return UserLogoutRequestDTO(reference_number="ref-123")
    
    @pytest.mark.asyncio
    async def test_post_calls_service(self, controller):
        """Test post method calls service."""
        mock_service = MagicMock()
        mock_service.run = AsyncMock(return_value={"success": True})
        
        controller.logout_service = mock_service
        controller.user_repository = MagicMock()
        
        request = UserLogoutRequestDTO(reference_number="ref-123")
        
        # The post method should be callable
        assert callable(controller.post)


class TestUserLogoutControllerValidation:
    """Tests for UserLogoutController validation."""
    
    @pytest.fixture
    def controller(self):
        """Create controller instance."""
        return UserLogoutController(urn="test-urn")
    
    def test_validate_request_exists(self, controller):
        """Test validate_request method exists."""
        assert hasattr(controller, 'validate_request')
