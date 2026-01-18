"""
Tests for Product Repository.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from repositories.product import ProductRepository
from models.product import Product


class TestProductRepositoryInit:
    """Tests for ProductRepository initialization."""
    
    def test_initialization(self):
        """Test ProductRepository can be initialized."""
        mock_session = MagicMock()
        repo = ProductRepository(session=mock_session)
        assert repo.session == mock_session
    
    def test_initialization_no_session(self):
        """Test ProductRepository can be initialized without session."""
        repo = ProductRepository()
        assert repo.session is None
    
    def test_session_setter(self):
        """Test session setter."""
        repo = ProductRepository()
        mock_session = MagicMock()
        repo.session = mock_session
        assert repo.session == mock_session


class TestProductRepositoryRetrieve:
    """Tests for ProductRepository retrieve methods."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()
    
    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)
    
    def test_retrieve_record_by_id(self, repo, mock_session):
        """Test retrieving by ID."""
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Test Product"
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_product
        mock_session.query.return_value = mock_query
        
        result = repo.retrieve_record_by_id(1)
        
        mock_session.query.assert_called()
    
    def test_retrieve_record_by_urn(self, repo, mock_session):
        """Test retrieving by URN."""
        mock_product = MagicMock(spec=Product)
        mock_product.urn = "test-product-urn"
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_product
        mock_session.query.return_value = mock_query
        
        result = repo.retrieve_record_by_urn("test-product-urn")
        
        mock_session.query.assert_called()
    
    def test_retrieve_record_by_name(self, repo, mock_session):
        """Test retrieving by name."""
        mock_product = MagicMock(spec=Product)
        mock_product.name = "Test Product"
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_product
        mock_session.query.return_value = mock_query
        
        result = repo.retrieve_record_by_name("Test Product")
        
        mock_session.query.assert_called()
    
    def test_retrieve_records_by_filter(self, repo, mock_session):
        """Test retrieving multiple records."""
        mock_products = [
            MagicMock(spec=Product, id=1),
            MagicMock(spec=Product, id=2),
        ]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_products
        mock_session.query.return_value = mock_query
        
        result = repo.retrieve_all_active()
        mock_session.query.assert_called()


class TestProductRepositoryCreate:
    """Tests for ProductRepository create methods."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        session = MagicMock()
        session.add = MagicMock()
        session.commit = MagicMock()
        session.refresh = MagicMock()
        return session
    
    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)
    
    def test_create_record(self, repo, mock_session):
        """Test creating a new record."""
        mock_product = MagicMock(spec=Product)
        
        result = repo.create_record(mock_product)
        
        mock_session.add.assert_called_once_with(mock_product)
        mock_session.commit.assert_called_once()


class TestProductRepositoryUpdate:
    """Tests for ProductRepository update methods."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()
    
    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)
    
    def test_update_record(self, repo, mock_session):
        """Test updating a record."""
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Old Name"
        
        result = repo.update_record(
            record=mock_product,
            name="New Name"
        )
        
        mock_session.commit.assert_called()


class TestProductRepositoryDelete:
    """Tests for ProductRepository delete methods."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()
    
    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)
    
    def test_soft_delete(self, repo, mock_session):
        """Test soft deleting a record."""
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.is_deleted = False
        
        result = repo.soft_delete(mock_product)
        
        mock_session.commit.assert_called()


class TestProductRepositoryList:
    """Tests for ProductRepository list methods."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()
    
    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)
    
    def test_retrieve_all_active(self, repo, mock_session):
        """Test retrieving all active records."""
        mock_products = [
            MagicMock(spec=Product, id=1, name="Product 1"),
            MagicMock(spec=Product, id=2, name="Product 2"),
        ]
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_products
        mock_session.query.return_value = mock_query
        
        result = repo.retrieve_all_active()
        
        mock_session.query.assert_called()
    
    def test_count_active(self, repo, mock_session):
        """Test counting active records."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_session.query.return_value = mock_query
        
        result = repo.count_active()
        
        mock_session.query.assert_called()
