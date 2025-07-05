"""
Unit tests for configuration management.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from customer_snapshot.utils.config import Config
from tests.fixtures import TEST_ENV_VARS


class TestConfig:
    """Test cases for Config class."""

    def test_config_initialization_with_defaults(self, temp_dir):
        """Test config initialization with default values."""
        config = Config()
        
        assert config.default_model == "claude-3-5-sonnet-20240620"
        assert config.max_tokens == 4000
        assert config.temperature == 0.0
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100
        assert config.max_file_size == 50 * 1024 * 1024
        assert ".vtt" in config.allowed_extensions
        assert ".txt" in config.allowed_extensions

    def test_config_initialization_with_env_vars(self, temp_dir):
        """Test config initialization with environment variables."""
        # Set environment variables
        for key, value in TEST_ENV_VARS.items():
            os.environ[key] = value
        
        config = Config()
        
        assert config.anthropic_api_key == "test_anthropic_key_123"
        assert config.voyage_api_key == "test_voyage_key_456"
        assert config.tavily_api_key == "test_tavily_key_789"
        assert config.max_tokens == 2000
        assert config.temperature == 0.1
        assert config.debug is True
        assert config.chunk_size == 300

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        os.environ["ANTHROPIC_API_KEY"] = "valid_key"
        
        config = Config()
        # Should not raise any exception
        config.validate()

    def test_config_validation_missing_api_key(self):
        """Test validation failure with missing API key."""
        # Ensure no API key is set
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        
        config = Config()
        
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            config.validate()

    def test_config_validation_invalid_values(self):
        """Test validation with invalid configuration values."""
        os.environ["ANTHROPIC_API_KEY"] = "valid_key"
        os.environ["MAX_TOKENS"] = "-100"
        os.environ["TEMPERATURE"] = "2.0"
        
        config = Config()
        
        with pytest.raises(ValueError, match="Configuration errors"):
            config.validate()

    def test_config_to_dict(self):
        """Test configuration serialization to dictionary."""
        os.environ["ANTHROPIC_API_KEY"] = "test_key"
        
        config = Config()
        config_dict = config.to_dict()
        
        assert "default_model" in config_dict
        assert "max_tokens" in config_dict
        assert "api_keys_configured" in config_dict
        assert config_dict["api_keys_configured"]["anthropic"] is True
        
        # Ensure sensitive data is not included
        assert "anthropic_api_key" not in config_dict

    def test_config_from_env_file(self, temp_dir):
        """Test configuration from specific .env file."""
        env_file = temp_dir / ".env.test"
        env_file.write_text("""
ANTHROPIC_API_KEY=test_key_from_file
MAX_TOKENS=1500
DEBUG=true
        """.strip())
        
        config = Config.from_env_file(str(env_file))
        
        assert config.anthropic_api_key == "test_key_from_file"
        assert config.max_tokens == 1500
        assert config.debug is True

    def test_config_directory_creation(self, temp_dir):
        """Test that configuration creates necessary directories."""
        config = Config()
        # Override to use temp directory
        config.data_dir = temp_dir / "test_data"
        config.input_dir = config.data_dir / "input"
        config.output_dir = config.data_dir / "output"
        config.templates_dir = config.data_dir / "templates"
        
        config._ensure_directories()
        
        assert config.data_dir.exists()
        assert config.input_dir.exists()
        assert config.output_dir.exists()
        assert config.templates_dir.exists()

    def test_config_get_default(self):
        """Test getting default configuration."""
        config = Config.get_default()
        
        assert isinstance(config, Config)
        assert config.default_model == "claude-3-5-sonnet-20240620"

    @pytest.mark.parametrize("env_var,expected_type", [
        ("MAX_TOKENS", int),
        ("TEMPERATURE", float),
        ("DEBUG", bool),
        ("CHUNK_SIZE", int),
        ("CHUNK_OVERLAP", int),
        ("MAX_FILE_SIZE", int),
    ])
    def test_config_type_conversion(self, env_var, expected_type):
        """Test that environment variables are properly converted to correct types."""
        test_values = {
            "MAX_TOKENS": "1000",
            "TEMPERATURE": "0.5",
            "DEBUG": "true",
            "CHUNK_SIZE": "250",
            "CHUNK_OVERLAP": "50",
            "MAX_FILE_SIZE": "10485760"
        }
        
        os.environ[env_var] = test_values[env_var]
        config = Config()
        
        attr_name = env_var.lower()
        if attr_name == "max_file_size":
            value = config.max_file_size
        elif attr_name == "max_tokens":
            value = config.max_tokens
        elif attr_name == "temperature":
            value = config.temperature
        elif attr_name == "debug":
            value = config.debug
        elif attr_name == "chunk_size":
            value = config.chunk_size
        elif attr_name == "chunk_overlap":
            value = config.chunk_overlap
        
        assert isinstance(value, expected_type)

    def test_config_allowed_extensions_parsing(self):
        """Test parsing of allowed extensions from environment variable."""
        os.environ["ALLOWED_EXTENSIONS"] = ".vtt,.txt,.md,.html"
        
        config = Config()
        
        assert ".vtt" in config.allowed_extensions
        assert ".txt" in config.allowed_extensions
        assert ".md" in config.allowed_extensions
        assert ".html" in config.allowed_extensions
        assert len(config.allowed_extensions) == 4