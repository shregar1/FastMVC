"""
Tests for FastMVC Project Generator module.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastmvc_cli.generator import ProjectGenerator


class TestProjectGenerator:
    """Tests for ProjectGenerator class."""
    
    def test_initialization(self):
        """Test ProjectGenerator initialization."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir="/tmp"
        )
        assert generator.project_name == "test_project"
        # output_dir might be PosixPath
        assert str(generator.output_dir).endswith("tmp")
    
    def test_initialization_with_options(self):
        """Test ProjectGenerator initialization with options."""
        generator = ProjectGenerator(
            project_name="myapp",
            output_dir="/tmp",
            init_git=True,
            create_venv=True,
            install_deps=True
        )
        assert generator.project_name == "myapp"
        assert generator.init_git is True
        assert generator.create_venv is True
        assert generator.install_deps is True
    
    def test_project_path(self):
        """Test project path generation."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir="/tmp"
        )
        # project_path should contain project_name
        assert "test_project" in str(generator.project_path)
    
    def test_template_dirs_exist(self):
        """Test TEMPLATE_DIRS constant exists."""
        assert hasattr(ProjectGenerator, 'TEMPLATE_DIRS')
        assert isinstance(ProjectGenerator.TEMPLATE_DIRS, list)
    
    def test_template_files_exist(self):
        """Test TEMPLATE_FILES constant exists."""
        assert hasattr(ProjectGenerator, 'TEMPLATE_FILES')
        assert isinstance(ProjectGenerator.TEMPLATE_FILES, list)
    
    def test_has_generate_method(self):
        """Test generator has generate method."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert hasattr(generator, 'generate')
        assert callable(generator.generate)
