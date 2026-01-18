"""
Tests for Product CRUD Service.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from services.product.crud import ProductCRUDService
from services.product.abstraction import IProductService
from dtos.requests.product.create import ProductCreateRequestDTO
from dtos.requests.product.update import ProductUpdateRequestDTO
from models.product import Product
from errors.not_found_error import NotFoundError


class TestProductCRUDServiceInit:
    """Tests for ProductCRUDService initialization."""
    
    def test_initialization(self):
        """Test ProductCRUDService can be initialized."""
        mock_repo = MagicMock()
        service = ProductCRUDService(
            urn="test-urn",
            repository=mock_repo
        )
        assert service.urn == "test-urn"
        assert service.repository == mock_repo
    
    def test_initialization_with_all_params(self):
        """Test ProductCRUDService with all parameters."""
        mock_repo = MagicMock()
        service = ProductCRUDService(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test_api",
            user_id=123,
            repository=mock_repo
        )
        assert service.urn == "test-urn"
        assert service.user_urn == "user-urn"
        assert service.api_name == "test_api"
        assert service.user_id == 123


class TestProductCRUDServiceCreate:
    """Tests for ProductCRUDService create operation."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        repo = MagicMock()
        repo.create_record = MagicMock()
        repo.retrieve_record_by_name = MagicMock(return_value=None)
        return repo
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            user_id=1,
            repository=mock_repo
        )
    
    @pytest.mark.asyncio
    async def test_create_product(self, service, mock_repo):
        """Test creating a product."""
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.urn = "product-urn"
        
        mock_repo.create_record.return_value = mock_product
        
        request_dto = ProductCreateRequestDTO(
            reference_number="ref-123",
            name="Test Product",
            description="A test product"
        )
        
        result = await service.create(request_dto)
        mock_repo.create_record.assert_called_once()


class TestProductCRUDServiceGet:
    """Tests for ProductCRUDService get operation."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            repository=mock_repo
        )
    
    @pytest.mark.asyncio
    async def test_get_product_by_id(self, service, mock_repo):
        """Test getting a product by ID."""
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.urn = "prod-urn"
        mock_product.description = "Test desc"
        mock_product.is_active = True
        
        mock_repo.retrieve_record_by_id.return_value = mock_product
        
        result = await service.get_by_id(1)
        mock_repo.retrieve_record_by_id.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_product_not_found(self, service, mock_repo):
        """Test getting non-existent product raises error."""
        mock_repo.retrieve_record_by_id.return_value = None
        
        with pytest.raises(NotFoundError):
            await service.get_by_id(999)


class TestProductCRUDServiceUpdate:
    """Tests for ProductCRUDService update operation."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            user_id=1,
            repository=mock_repo
        )
    
    @pytest.mark.asyncio
    async def test_update_product(self, service, mock_repo):
        """Test updating a product."""
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Old Name"
        mock_product.urn = "prod-urn"
        mock_product.description = "Old desc"
        mock_product.is_active = True
        
        mock_repo.retrieve_record_by_id.return_value = mock_product
        mock_repo.update_record.return_value = mock_product
        
        request_dto = ProductUpdateRequestDTO(
            reference_number="ref-123",
            name="New Name",
            description="Updated description"
        )
        
        result = await service.update(1, request_dto)
        mock_repo.retrieve_record_by_id.assert_called()


class TestProductCRUDServiceDelete:
    """Tests for ProductCRUDService delete operation."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            repository=mock_repo
        )
    
    @pytest.mark.asyncio
    async def test_delete_product(self, service, mock_repo):
        """Test deleting a product."""
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        
        mock_repo.retrieve_record_by_id.return_value = mock_product
        mock_repo.delete_record.return_value = True
        
        result = await service.delete(1)
        mock_repo.retrieve_record_by_id.assert_called()
    
    @pytest.mark.asyncio
    async def test_delete_product_not_found(self, service, mock_repo):
        """Test deleting non-existent product raises error."""
        mock_repo.retrieve_record_by_id.return_value = None
        
        with pytest.raises(NotFoundError):
            await service.delete(999)


class TestProductCRUDServiceList:
    """Tests for ProductCRUDService list operation."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            repository=mock_repo
        )
    
    @pytest.mark.asyncio
    async def test_list_products(self, service, mock_repo):
        """Test listing products."""
        mock_products = [
            MagicMock(spec=Product, id=1, name="Product 1", urn="p1", description="d1", is_active=True),
            MagicMock(spec=Product, id=2, name="Product 2", urn="p2", description="d2", is_active=True),
        ]
        
        mock_repo.retrieve_records_by_filter.return_value = mock_products
        
        result = await service.list()
        assert result is not None


class TestIProductService:
    """Tests for IProductService abstraction."""
    
    def test_is_abstract(self):
        """Test IProductService has abstract methods."""
        assert hasattr(IProductService, '__abstractmethods__') or hasattr(IProductService, 'run')
