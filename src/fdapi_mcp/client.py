"""HTTP client for FDAPI endpoints."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from .config import FDAPIConfig
from .exceptions import FDAPIError, FDAPIConnectionError, FDAPIResponseError

logger = logging.getLogger(__name__)


class FDAPIClient:
    """Asynchronous HTTP client for FDAPI endpoints."""

    def __init__(self, config: FDAPIConfig):
        """Initialize the FDAPI client.

        Args:
            config: FDAPI configuration
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "FDAPIClient":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the HTTP client."""
        if self._client is not None:
            return

        headers = {
            "User-Agent": "FDAPI-MCP-Server/0.1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Add API key if configured
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=headers,
            timeout=self.config.timeout,
            follow_redirects=True,
        )
        logger.info(f"FDAPI client started with base URL: {self.config.base_url}")

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("FDAPI client closed")

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client instance."""
        if self._client is None:
            raise FDAPIError(
                "Client not started. Use async context manager or call start() first.")
        return self._client

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the FDAPI.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            json: JSON payload
            **kwargs: Additional httpx request arguments

        Returns:
            Response JSON data

        Raises:
            FDAPIConnectionError: On connection issues
            FDAPIResponseError: On HTTP errors
            FDAPIError: On other errors
        """
        url = path if path.startswith("http") else urljoin("/", path)

        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(
                    f"Making {method} request to {url} (attempt {attempt + 1})")

                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    **kwargs,
                )

                # Log response details
                logger.debug(f"Response status: {response.status_code}")

                # Handle HTTP errors
                if response.status_code >= 400:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        if "message" in error_data:
                            error_msg += f": {error_data['message']}"
                    except Exception:
                        error_msg += f": {response.text}"

                    raise FDAPIResponseError(
                        error_msg, status_code=response.status_code)

                # Parse JSON response
                try:
                    return response.json()
                except Exception as e:
                    raise FDAPIResponseError(f"Failed to parse JSON response: {e}")

            except httpx.ConnectError as e:
                if attempt == self.config.max_retries:
                    raise FDAPIConnectionError(
                        f"Connection failed after {self.config.max_retries + 1} attempts: {e}")
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except httpx.TimeoutException as e:
                if attempt == self.config.max_retries:
                    raise FDAPIConnectionError(
                        f"Request timeout after {self.config.max_retries + 1} attempts: {e}")
                logger.warning(f"Timeout attempt {attempt + 1}, retrying...")
                await asyncio.sleep(2 ** attempt)

        raise FDAPIError("Request failed after all retry attempts")

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self.request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request.

        Args:
            path: API endpoint path
            json: JSON payload
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self.request("POST", path, json=json, params=params)

    async def health_check(self) -> bool:
        """Check if the FDAPI is accessible.

        Returns:
            True if accessible, False otherwise
        """
        try:
            # Try a simple endpoint to check connectivity
            # TODO: Replace with actual health check endpoint when known
            await self.get("/v1/health")
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
