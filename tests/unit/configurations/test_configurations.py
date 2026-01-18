"""
Tests for configuration loader classes.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock


class TestDBConfiguration:
    """Tests for DBConfiguration."""

    def test_import(self):
        """Test DBConfiguration can be imported."""
        from configurations.db import DBConfiguration
        assert DBConfiguration is not None

    @patch('builtins.open')
    @patch('json.load')
    def test_get_config_returns_dto(self, mock_json_load, mock_open):
        """Test get_config returns proper DTO."""
        mock_json_load.return_value = {
            "user_name": "test",
            "password": "test123",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "connection_string": "postgresql://{user_name}:{password}@{host}:{port}/{database}"
        }
        
        from configurations.db import DBConfiguration
        config = DBConfiguration()
        result = config.get_config()
        
        assert result is not None


class TestCacheConfiguration:
    """Tests for CacheConfiguration."""

    def test_import(self):
        """Test CacheConfiguration can be imported."""
        from configurations.cache import CacheConfiguration
        assert CacheConfiguration is not None

    @patch('builtins.open')
    @patch('json.load')
    def test_get_config_returns_dto(self, mock_json_load, mock_open):
        """Test get_config returns proper DTO."""
        mock_json_load.return_value = {
            "host": "localhost",
            "port": 6379,
            "password": "test123"
        }
        
        from configurations.cache import CacheConfiguration
        config = CacheConfiguration()
        result = config.get_config()
        
        assert result is not None


class TestSecurityConfiguration:
    """Tests for SecurityConfiguration."""

    def test_import(self):
        """Test SecurityConfiguration can be imported."""
        from configurations.security import SecurityConfiguration
        assert SecurityConfiguration is not None

