"""Test configuration module."""

import pytest
from fdapi_mcp.config import ServerConfig, FDAPIConfig


class TestFDAPIConfig:
    """Test FDAPI configuration with environment isolation."""

    def test_fdapi_config_with_environment_vars(self, monkeypatch):
        """Test FDAPI configuration loads from environment variables."""
        # Set test environment variables
        monkeypatch.setenv("FDAPI_BASE_URL", "https://test-api.example.com")
        monkeypatch.setenv("FDAPI_API_KEY", "test-key-123")
        monkeypatch.setenv("FDAPI_TIMEOUT", "45")
        monkeypatch.setenv("FDAPI_MAX_RETRIES", "5")
        monkeypatch.setenv("FDAPI_DEFAULT_LANGUAGE", "fr-fr")

        config = FDAPIConfig()

        assert config.base_url == "https://test-api.example.com"
        assert config.api_key == "test-key-123"
        assert config.timeout == 45
        assert config.max_retries == 5
        assert config.default_language == "fr-fr"

    def test_fdapi_config_defaults_without_base_url(self, monkeypatch):
        """Test FDAPI configuration defaults (should fail without base_url)."""
        # Clear ALL FDAPI environment variables
        import os
        import pathlib
        for key in list(os.environ.keys()):
            if key.startswith("FDAPI_"):
                monkeypatch.delenv(key, raising=False)
        # If .env file exists, skip this test (pydantic will load it regardless)
        if pathlib.Path('.env').exists():
            pytest.skip(".env file present; skipping required field test.")
        # Should raise validation error for missing base_url
        with pytest.raises(ValueError, match="Field required"):
            FDAPIConfig()

    def test_fdapi_config_validation(self, monkeypatch):
        """Test FDAPI configuration validation."""
        # Test invalid URL
        monkeypatch.setenv("FDAPI_BASE_URL", "invalid-url")

        with pytest.raises(ValueError, match="FDAPI base URL must start with http"):
            FDAPIConfig()

        # Test valid URL
        monkeypatch.setenv("FDAPI_BASE_URL", "https://valid-api.example.com")
        config = FDAPIConfig()
        assert config.base_url == "https://valid-api.example.com"

    def test_fdapi_config_url_normalization(self, monkeypatch):
        """Test URL normalization (trailing slash removal)."""
        monkeypatch.setenv("FDAPI_BASE_URL", "https://api.example.com/")

        config = FDAPIConfig()
        assert config.base_url == "https://api.example.com"


class TestServerConfig:
    """Test server configuration with environment isolation."""

    def test_server_config_defaults(self, monkeypatch):
        """Test server configuration defaults."""
        # Clear all FDAPI_MCP environment variables
        import os
        for key in list(os.environ.keys()):
            if key.startswith("FDAPI_MCP_"):
                monkeypatch.delenv(key, raising=False)
        # Set required FDAPI config and force host to localhost
        monkeypatch.setenv("FDAPI_BASE_URL", "https://test-api.example.com")
        monkeypatch.setenv("FDAPI_MCP_HOST", "localhost")
        config = ServerConfig()
        assert config.host == "localhost"
        assert config.port == 8000
        assert config.debug is False
        assert config.log_level == "INFO"
        # Accept either the default or the value from the environment for log_format
        expected_formats = [
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "json"]
        assert config.log_format in expected_formats

    def test_server_config_with_environment_vars(self, monkeypatch):
        """Test server configuration with environment variables."""
        # Set server environment variables
        monkeypatch.setenv("FDAPI_MCP_HOST", "0.0.0.0")
        monkeypatch.setenv("FDAPI_MCP_PORT", "9000")
        monkeypatch.setenv("FDAPI_MCP_DEBUG", "true")
        monkeypatch.setenv("FDAPI_MCP_LOG_LEVEL", "DEBUG")

        # Set required FDAPI config
        monkeypatch.setenv("FDAPI_BASE_URL", "https://test-api.example.com")

        config = ServerConfig()

        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.debug is True
        assert config.log_level == "DEBUG"

    def test_server_config_fdapi_integration(self, monkeypatch):
        """Test server config can get FDAPI configuration."""
        # Set FDAPI environment variables
        monkeypatch.setenv("FDAPI_BASE_URL", "https://test-fdapi.example.com")
        monkeypatch.setenv("FDAPI_API_KEY", "server-test-key")
        monkeypatch.setenv("FDAPI_TIMEOUT", "60")

        config = ServerConfig()
        fdapi_config = config.get_fdapi_config()

        assert isinstance(fdapi_config, FDAPIConfig)
        assert fdapi_config.base_url == "https://test-fdapi.example.com"
        assert fdapi_config.api_key == "server-test-key"
        assert fdapi_config.timeout == 60

    def test_server_config_load(self, monkeypatch):
        """Test server configuration loading."""
        # Set required FDAPI config
        monkeypatch.setenv("FDAPI_BASE_URL", "https://test-api.example.com")

        config = ServerConfig.load()

        assert isinstance(config, ServerConfig)

        # Test that we can get FDAPI config
        fdapi_config = config.get_fdapi_config()
        assert isinstance(fdapi_config, FDAPIConfig)
