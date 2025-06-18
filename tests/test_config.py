"""Test configuration module."""

import pytest
from fdapi_mcp.config import ServerConfig, FDAPIConfig


def test_fdapi_config_defaults():
    """Test FDAPI configuration defaults."""
    config = FDAPIConfig()

    assert config.base_url == "https://api.example.com"
    assert config.api_key is None
    assert config.timeout == 30
    assert config.max_retries == 3


def test_fdapi_config_custom():
    """Test FDAPI configuration with custom values."""
    config = FDAPIConfig(
        base_url="https://custom.api.com",
        api_key="test-key-123",
        timeout=60,
        max_retries=5
    )

    assert config.base_url == "https://custom.api.com"
    assert config.api_key == "test-key-123"
    assert config.timeout == 60
    assert config.max_retries == 5


def test_server_config_defaults():
    """Test server configuration defaults."""
    config = ServerConfig()

    assert config.host == "localhost"
    assert config.port == 8000
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.log_format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Check FDAPI config
    assert isinstance(config.fdapi, FDAPIConfig)
    assert config.fdapi.base_url == "https://api.example.com"


def test_server_config_load():
    """Test server configuration loading."""
    config = ServerConfig.load()

    assert isinstance(config, ServerConfig)
    assert isinstance(config.fdapi, FDAPIConfig)
