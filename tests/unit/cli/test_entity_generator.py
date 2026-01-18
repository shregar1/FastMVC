"""
Tests for FastMVC Entity Generator module.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastmvc_cli.entity_generator import EntityGenerator


class TestEntityGenerator:
    """Tests for EntityGenerator class."""
    
    def test_initialization(self):
        """Test EntityGenerator initialization."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator.entity_name == "Product"
        # project_path might be PosixPath
        assert "project" in str(generator.project_path)
    
    def test_entity_lower_property(self):
        """Test entity_lower property."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator.entity_lower == "product"
    
    def test_has_generate_method(self):
        """Test EntityGenerator has generate method."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert hasattr(generator, 'generate')
        assert callable(generator.generate)


class TestEntityGeneratorTemplates:
    """Tests for EntityGenerator template methods."""
    
    def test_has_model_template(self):
        """Test has model template method."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        # Should have some method for model generation
        assert hasattr(generator, 'generate') or hasattr(generator, '_create_model')
    
    def test_entity_name_property(self):
        """Test entity_name is stored correctly."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator.entity_name == "Product"
