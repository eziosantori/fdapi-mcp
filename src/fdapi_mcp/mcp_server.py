"""FastMCP 2.0 server implementation for FDAPI."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .client import FDAPIClient
from .config import ServerConfig
from .exceptions import FDAPIError, FDAPINotFoundError
from .models import AlbumEntity, DocumentEntity, ArticleEntity, LiveEntity

logger = logging.getLogger(__name__)


class FDAPIServerMCP:
    """FastMCP 2.0 server for FDAPI integration."""

    def __init__(self, config: ServerConfig):
        """Initialize the MCP server.

        Args:
            config: Server configuration
        """
        self.config = config
        self.fdapi_client: Optional[FDAPIClient] = None        # Create FastMCP instance
        self.mcp = FastMCP("FDAPI MCP Server")

        # Register tools
        self._register_tools()

    async def start(self) -> None:
        """Start the server and initialize clients."""
        logger.info("Starting FDAPI MCP Server...")

        # Initialize FDAPI client
        fdapi_config = self.config.get_fdapi_config()
        self.fdapi_client = FDAPIClient(fdapi_config)
        await self.fdapi_client.start()

        # Test connection
        if await self.fdapi_client.health_check():
            logger.info("FDAPI connection successful")
        else:
            logger.warning("FDAPI health check failed - some features may not work")

        logger.info("FDAPI MCP Server started successfully")

    async def stop(self) -> None:
        """Stop the server and cleanup resources."""
        logger.info("Stopping FDAPI MCP Server...")

        if self.fdapi_client:
            await self.fdapi_client.close()

        logger.info("FDAPI MCP Server stopped")

    async def run(self) -> None:
        """Run the server."""
        try:
            await self.start()
            # Keep the server running
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            await self.stop()

    def _register_tools(self) -> None:
        """Register MCP tools."""

        @self.mcp.tool()
        async def fdapi_get_album(
            language: str = Field(...,
                                  description="Language code (e.g., 'en-gb', 'fr-fr')"),
            slug: str = Field(..., description="Album slug identifier")
        ) -> Dict[str, Any]:
            """Get detailed information about a specific album from FDAPI.

            Retrieves complete album details including title, description, and metadata
            for the specified album in the given language.
            """
            if not self.fdapi_client:
                raise FDAPIError("FDAPI client not initialized")

            try:
                path = f"/v1/content/{language}/albums/{slug}"
                data = await self.fdapi_client.get(path)

                # Parse and validate the response
                album = AlbumEntity.model_validate(data)
                return album.model_dump()

            except FDAPIError:
                raise
            except Exception as e:
                logger.error(f"Error getting album {slug}: {e}")
                raise FDAPIError(f"Failed to get album: {e}")

        @self.mcp.tool()
        async def fdapi_list_albums(
            language: str = Field(...,
                                  description="Language code (e.g., 'en-gb', 'fr-fr')"),
            page: int = Field(1, description="Page number for pagination"),
            per_page: int = Field(20, description="Number of items per page")
        ) -> Dict[str, Any]:
            """List albums from FDAPI with pagination support.

            Retrieves a paginated list of albums in the specified language.
            Returns album summaries with basic information.
            """
            if not self.fdapi_client:
                raise FDAPIError("FDAPI client not initialized")

            try:
                path = f"/v1/content/{language}/albums"
                params = {"page": page, "per_page": per_page}
                data = await self.fdapi_client.get(path, params=params)

                # TODO: Parse list response when we have the actual API schema
                return data

            except FDAPIError:
                raise
            except Exception as e:
                logger.error(f"Error listing albums: {e}")
                raise FDAPIError(f"Failed to list albums: {e}")

        @self.mcp.tool()
        async def fdapi_get_document(
            language: str = Field(...,
                                  description="Language code (e.g., 'en-gb', 'fr-fr')"),
            slug: str = Field(..., description="Document slug identifier")
        ) -> Dict[str, Any]:
            """Get detailed information about a specific document from FDAPI.

            Retrieves complete document details including title, content, and metadata
            for the specified document in the given language.
            """
            if not self.fdapi_client:
                raise FDAPIError("FDAPI client not initialized")

            try:
                path = f"/v1/content/{language}/documents/{slug}"
                data = await self.fdapi_client.get(path)

                # Parse and validate the response
                document = DocumentEntity.model_validate(data)
                return document.model_dump()

            except FDAPIError:
                raise
            except Exception as e:
                logger.error(f"Error getting document {slug}: {e}")
                raise FDAPIError(f"Failed to get document: {e}")

        @self.mcp.tool()
        async def fdapi_list_documents(
            language: str = Field(...,
                                  description="Language code (e.g., 'en-gb', 'fr-fr')"),
            page: int = Field(1, description="Page number for pagination"),
            per_page: int = Field(20, description="Number of items per page")
        ) -> Dict[str, Any]:
            """List documents from FDAPI with pagination support.

            Retrieves a paginated list of documents in the specified language.
            Returns document summaries with basic information.
            """
            if not self.fdapi_client:
                raise FDAPIError("FDAPI client not initialized")

            try:
                path = f"/v1/content/{language}/documents"
                params = {"page": page, "per_page": per_page}
                data = await self.fdapi_client.get(path, params=params)

                # TODO: Parse list response when we have the actual API schema
                return data

            except FDAPIError:
                raise
            except Exception as e:
                logger.error(f"Error listing documents: {e}")
                raise FDAPIError(f"Failed to list documents: {e}")

        @self.mcp.tool()
        async def fdapi_get_article(
            language: str = Field(...,
                                  description="Language code (e.g., 'en-gb', 'fr-fr')"),
            slug: str = Field(..., description="Article slug identifier")
        ) -> Dict[str, Any]:
            """Get detailed information about a specific article from FDAPI.

            Retrieves complete article details including title, content, author, and metadata
            for the specified article in the given language.
            """
            if not self.fdapi_client:
                raise FDAPIError("FDAPI client not initialized")

            try:
                path = f"/v1/content/{language}/articles/{slug}"
                data = await self.fdapi_client.get(path)

                # Parse and validate the response
                article = ArticleEntity.model_validate(data)
                return article.model_dump()

            except FDAPIError:
                raise
            except Exception as e:
                logger.error(f"Error getting article {slug}: {e}")
                raise FDAPIError(f"Failed to get article: {e}")        @ self.mcp.tool()

        async def fdapi_health_check() -> Dict[str, Any]:
            """Check the health and connectivity of the FDAPI service.

            Tests the connection to FDAPI and returns status information.
            Useful for troubleshooting connectivity issues.
            """
            if not self.fdapi_client:
                return {"status": "error", "message": "FDAPI client not initialized"}

            try:
                is_healthy = await self.fdapi_client.health_check()
                fdapi_config = self.config.get_fdapi_config()
                return {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "base_url": fdapi_config.base_url,
                    "has_api_key": bool(fdapi_config.api_key),
                    "timeout": fdapi_config.timeout,
                    "max_retries": fdapi_config.max_retries,
                }
            except Exception as e:
                fdapi_config = self.config.get_fdapi_config()
                return {
                    "status": "error",
                    "message": str(e),
                    "base_url": fdapi_config.base_url,
                }


def create_mcp_server(config: ServerConfig) -> FDAPIServerMCP:
    """Create and configure the MCP server.

    Args:
        config: Server configuration

    Returns:
        Configured MCP server instance
    """
    return FDAPIServerMCP(config)
