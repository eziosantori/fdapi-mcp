"""FDAPI MCP Server - A Model Context Protocol server for FDAPI integration."""

__version__ = "0.1.0"
__author__ = "FDAPI MCP Team"
__description__ = "A Model Context Protocol server for FDAPI integration"

# Import main components for easier access
from .config import ServerConfig, FDAPIConfig
from .client import FDAPIClient
from .exceptions import (
    FDAPIError,
    FDAPIConnectionError,
    FDAPIResponseError,
    FDAPIAuthenticationError,
    FDAPIValidationError,
    FDAPINotFoundError,
    FDAPIRateLimitError,
)
from .models import (
    AlbumEntity,
    DocumentEntity,
    ArticleEntity,
    LiveEntity,
    ListResponse,
    ErrorResponse,
    EntityType,
    AnyEntity,
)
from .mcp_server import FDAPIServerMCP, create_mcp_server

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",

    # Configuration
    "ServerConfig",
    "FDAPIConfig",

    # Client
    "FDAPIClient",

    # Exceptions
    "FDAPIError",
    "FDAPIConnectionError",
    "FDAPIResponseError",
    "FDAPIAuthenticationError",
    "FDAPIValidationError",
    "FDAPINotFoundError",
    "FDAPIRateLimitError",

    # Models
    "AlbumEntity",
    "DocumentEntity",
    "ArticleEntity",
    "LiveEntity",
    "ListResponse",
    "ErrorResponse",
    "EntityType",
    "AnyEntity",

    # MCP Server
    "FDAPIServerMCP",
    "create_mcp_server",
]
