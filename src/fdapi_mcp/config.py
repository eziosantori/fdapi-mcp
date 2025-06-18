"""Configuration management for FDAPI MCP Server."""

import os
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FDAPIConfig(BaseModel):
    """FDAPI client configuration."""

    base_url: str = Field(
        default="https://api.example.com",  # TODO: Replace with actual FDAPI URL
        description="Base URL for FDAPI endpoints"
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


class ServerConfig(BaseSettings):
    """Server configuration with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="FDAPI_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server settings
    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # FDAPI settings
    fdapi: FDAPIConfig = Field(default_factory=FDAPIConfig)

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
