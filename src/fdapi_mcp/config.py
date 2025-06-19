"""Configuration management for FDAPI MCP Server."""

import os
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class FDAPIConfig(BaseSettings):
    """FDAPI client configuration with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="FDAPI_", env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    base_url: str = Field(
        ...,  # ... means required
        description="Base URL for FDAPI endpoints (required via FDAPI_BASE_URL)"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication (future use)"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    default_language: str = Field(
        default="en-gb",
        description="Default language for content requests"
    )

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format and requirement."""
        if not v:
            raise ValueError(
                "FDAPI base URL is required - set FDAPI_BASE_URL environment variable"
            )
        if not v.startswith(('http://', 'https://')):
            raise ValueError(
                "FDAPI base URL must start with http:// or https://"
            )
        return v.rstrip('/')


class ServerConfig(BaseSettings):
    """Server configuration with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="FDAPI_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server settings
    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # FDAPI settings - load separately to use FDAPI_ prefix
    def get_fdapi_config(self) -> FDAPIConfig:
        """Get FDAPI configuration with proper environment variable support."""
        return FDAPIConfig()

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )

    @classmethod
    def load(cls) -> "ServerConfig":
        """Load configuration from environment and .env file."""
        return cls()


# Global configuration instance
config = ServerConfig.load()
