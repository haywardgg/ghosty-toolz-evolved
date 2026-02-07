"""Tests for validators module."""

import pytest
from src.utils.validators import Validators, ValidationError


class TestValidators:
    """Test suite for Validators class."""

    def test_validate_path_valid(self):
        """Test path validation with valid path."""
        validator = Validators()
        assert validator.validate_path("C:\\Windows") is True

    def test_validate_path_with_traversal(self):
        """Test path validation rejects path traversal."""
        validator = Validators()
        with pytest.raises(ValidationError):
            validator.validate_path("C:\\Windows\\..\\..\\sensitive")

    def test_validate_command_valid(self):
        """Test command validation with valid command."""
        validator = Validators()
        assert validator.validate_command("ipconfig /all") is True

    def test_validate_command_with_injection(self):
        """Test command validation rejects injection attempts."""
        validator = Validators()
        with pytest.raises(ValidationError):
            validator.validate_command("ipconfig; rm -rf /")

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        validator = Validators()
        result = validator.sanitize_filename("test<file>name*.txt")
        assert "<" not in result
        assert ">" not in result
        assert "*" not in result

    def test_validate_port_valid(self):
        """Test port validation with valid port."""
        validator = Validators()
        assert validator.validate_port(8080) is True

    def test_validate_port_invalid(self):
        """Test port validation with invalid port."""
        validator = Validators()
        with pytest.raises(ValidationError):
            validator.validate_port(70000)

    def test_validate_timeout(self):
        """Test timeout validation."""
        validator = Validators()
        assert validator.validate_timeout(30) is True

    def test_validate_timeout_invalid(self):
        """Test timeout validation with invalid value."""
        validator = Validators()
        with pytest.raises(ValidationError):
            validator.validate_timeout(5000)
