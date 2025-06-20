"""Integration tests for FDAPI client connectivity."""

import os
import pytest
import httpx
import respx
from unittest.mock import AsyncMock

from fdapi_mcp.client import FDAPIClient
from fdapi_mcp.config import FDAPIConfig
from fdapi_mcp.exceptions import FDAPIConnectionError, FDAPIResponseError, FDAPIError


class TestFDAPIIntegration:
    """Integration tests for FDAPI client with real connectivity scenarios."""

    @pytest.fixture
    def mock_env_vars(self, monkeypatch):
        """Set up test environment variables."""
        monkeypatch.setenv("FDAPI_BASE_URL", "https://test-fdapi.example.com")
        monkeypatch.setenv("FDAPI_API_KEY", "test-api-key-123")
        monkeypatch.setenv("FDAPI_TIMEOUT", "10")
        monkeypatch.setenv("FDAPI_MAX_RETRIES", "2")
        monkeypatch.setenv("FDAPI_DEFAULT_LANGUAGE", "en-gb")

    @pytest.fixture
    def mock_env_vars_no_auth(self, monkeypatch):
        """Set up test environment variables without authentication."""
        monkeypatch.setenv("FDAPI_BASE_URL", "https://test-fdapi.example.com")
        monkeypatch.setenv("FDAPI_TIMEOUT", "10")
        monkeypatch.setenv("FDAPI_MAX_RETRIES", "2")
        monkeypatch.setenv("FDAPI_DEFAULT_LANGUAGE", "en-gb")
        # Ensure API key is not set
        monkeypatch.delenv("FDAPI_API_KEY", raising=False)

    @pytest.fixture
    def mock_config(self, mock_env_vars):
        """Create a test configuration using environment variables."""
        return FDAPIConfig()

    @pytest.fixture
    def mock_config_no_auth(self, mock_env_vars_no_auth):
        """Create a test configuration without authentication."""
        return FDAPIConfig()

    @pytest.mark.asyncio
    async def test_client_context_manager(self, mock_config):
        """Test client can be used as async context manager."""
        async with FDAPIClient(mock_config) as client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)
            assert str(client._client.base_url) == mock_config.base_url

        # Client should be closed after context exit
        assert client._client is None

    @pytest.mark.asyncio
    async def test_client_manual_lifecycle(self, mock_config):
        """Test manual client start/stop lifecycle."""
        client = FDAPIClient(mock_config)

        # Initially not started
        assert client._client is None

        # Start client
        await client.start()
        assert client._client is not None

        # Close client
        await client.close()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_client_headers_with_auth(self, mock_config):
        """Test client sets correct headers with authentication."""
        async with FDAPIClient(mock_config) as client:
            headers = client._client.headers

            assert headers["User-Agent"] == "FDAPI-MCP-Server/0.1.0"
            assert headers["Accept"] == "application/json"
            assert headers["Content-Type"] == "application/json"
            assert headers["Authorization"] == "Bearer test-api-key-123"

    @pytest.mark.asyncio
    async def test_client_headers_without_auth(self, mock_config_no_auth):
        """Test client sets correct headers without authentication."""
        async with FDAPIClient(mock_config_no_auth) as client:
            headers = client._client.headers

            assert headers["User-Agent"] == "FDAPI-MCP-Server/0.1.0"
            assert headers["Accept"] == "application/json"
            assert headers["Content-Type"] == "application/json"
            assert "Authorization" not in headers

    @pytest.mark.asyncio
    @respx.mock
    async def test_successful_get_request(self, mock_config):
        """Test successful GET request."""
        # Mock successful response
        respx.get(f"{mock_config.base_url}/v1/content/en-gb/albums/test-album").mock(
            return_value=httpx.Response(
                200, json={"id": "test-album", "title": "Test Album"})
        )

        async with FDAPIClient(mock_config) as client:
            response = await client.get("/v1/content/en-gb/albums/test-album")

            assert response["id"] == "test-album"
            assert response["title"] == "Test Album"

    @pytest.mark.asyncio
    @respx.mock
    async def test_successful_post_request(self, mock_config):
        """Test successful POST request."""
        # Mock successful response
        respx.post(f"{mock_config.base_url}/v1/forms/submit").mock(
            return_value=httpx.Response(
                201, json={"status": "submitted", "id": "form-123"})
        )

        payload = {"name": "Test User", "email": "test@example.com"}

        async with FDAPIClient(mock_config) as client:
            response = await client.post("/v1/forms/submit", json=payload)

            assert response["status"] == "submitted"
            assert response["id"] == "form-123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_paginated_request(self, mock_config):
        """Test paginated GET request."""
        # Mock paginated response
        respx.get(f"{mock_config.base_url}/v1/content/en-gb/albums").mock(
            return_value=httpx.Response(200, json={
                "items": [
                    {"id": "album-1", "title": "Album 1"},
                    {"id": "album-2", "title": "Album 2"}
                ],
                "pagination": {
                    "total": 10,
                    "page": 1,
                    "limit": 2,
                    "has_next": True
                }
            })
        )

        async with FDAPIClient(mock_config) as client:
            response = await client.get("/v1/content/en-gb/albums", params={"page": 1, "limit": 2})

            assert len(response["items"]) == 2
            assert response["pagination"]["total"] == 10
            assert response["pagination"]["has_next"] is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_404_error_handling(self, mock_config):
        """Test 404 error handling."""
        # Mock 404 response
        respx.get(f"{mock_config.base_url}/v1/content/en-gb/albums/nonexistent").mock(
            return_value=httpx.Response(404, json={"error": "Album not found"})
        )

        async with FDAPIClient(mock_config) as client:
            with pytest.raises(FDAPIResponseError) as exc_info:
                await client.get("/v1/content/en-gb/albums/nonexistent")

            assert exc_info.value.status_code == 404
            assert "Album not found" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_500_error_handling(self, mock_config):
        """Test 500 error handling."""
        # Mock 500 response
        respx.get(f"{mock_config.base_url}/v1/content/en-gb/albums/error").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )

        async with FDAPIClient(mock_config) as client:
            with pytest.raises(FDAPIResponseError) as exc_info:
                await client.get("/v1/content/en-gb/albums/error")

            assert exc_info.value.status_code == 500
            assert "Internal server error" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_check_success(self, mock_config):
        """Test health check success."""
        # Mock health check endpoint
        respx.get(f"{mock_config.base_url}/v1/health").mock(
            return_value=httpx.Response(200, json={"status": "healthy"})
        )

        async with FDAPIClient(mock_config) as client:
            result = await client.health_check()
            assert result is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_check_failure(self, mock_config):
        """Test health check failure."""
        # Mock failed health check
        respx.get(f"{mock_config.base_url}/v1/health").mock(
            return_value=httpx.Response(503, json={"status": "unhealthy"})
        )

        async with FDAPIClient(mock_config) as client:
            result = await client.health_check()
            assert result is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_connection_error_handling(self, mock_config):
        """Test connection error handling."""
        # Mock connection timeout
        respx.get(f"{mock_config.base_url}/v1/health").mock(
            side_effect=httpx.ConnectTimeout("Connection timeout")
        )

        async with FDAPIClient(mock_config) as client:
            result = await client.health_check()
            assert result is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_retry_mechanism(self, mock_config):
        """Test retry mechanism for transient failures."""
        # First request fails, second succeeds
        respx.get(f"{mock_config.base_url}/v1/content/en-gb/albums/test").mock(
            side_effect=[
                httpx.Response(500, json={"error": "Temporary error"}),
                httpx.Response(200, json={"id": "test", "title": "Test Album"})
            ]
        )

        async with FDAPIClient(mock_config) as client:
            response = await client.get("/v1/content/en-gb/albums/test")
            assert response["id"] == "test"
            assert response["title"] == "Test Album"

    @pytest.mark.asyncio
    @respx.mock
    async def test_retry_exhaustion(self, mock_config):
        """Test retry exhaustion."""
        # Mock repeated failures
        respx.get(f"{mock_config.base_url}/v1/health").mock(
            side_effect=httpx.Response(500, json={"error": "Persistent error"})
        )

        async with FDAPIClient(mock_config) as client:
            result = await client.health_check()
            assert result is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_network_error_handling(self, mock_config):
        """Test network error handling."""
        # Mock network error
        respx.get(f"{mock_config.base_url}/v1/health").mock(
            side_effect=httpx.NetworkError("Network error")
        )

        async with FDAPIClient(mock_config) as client:
            result = await client.health_check()
            assert result is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_content_caching_headers(self, mock_config):
        """Test content caching headers are respected."""
        # Mock response with caching headers
        respx.get(f"{mock_config.base_url}/v1/content/en-gb/albums/test-album").mock(
            return_value=httpx.Response(
                200,
                json={"id": "test-album", "title": "Test Album"},
                headers={"Cache-Control": "max-age=300"}
            )
        )

        async with FDAPIClient(mock_config) as client:
            response = await client.get("/v1/content/en-gb/albums/test-album")
            assert response["id"] == "test-album"

    @pytest.mark.asyncio
    @respx.mock
    async def test_language_specific_requests(self, mock_config):
        """Test requests with different language parameters."""
        languages = ["en-gb", "es-es", "fr-fr", "de-de", "it-it", "pt-pt"]

        for lang in languages:
            respx.get(f"{mock_config.base_url}/v1/content/{lang}/albums/test").mock(
                return_value=httpx.Response(
                    200,
                    json={"id": "test", "title": f"Test in {lang}", "language": lang}
                )
            )

        async with FDAPIClient(mock_config) as client:
            for lang in languages:
                response = await client.get(f"/v1/content/{lang}/albums/test")
                assert response["language"] == lang


class TestFDAPIConfigurationIntegration:
    """Integration tests for configuration scenarios."""

    @pytest.mark.asyncio
    async def test_environment_variable_configuration(self, monkeypatch):
        """Test client with configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("FDAPI_BASE_URL", "https://env-test.example.com")
        monkeypatch.setenv("FDAPI_API_KEY", "env-api-key")
        monkeypatch.setenv("FDAPI_TIMEOUT", "60")
        monkeypatch.setenv("FDAPI_MAX_RETRIES", "5")

        # Create config that reads from environment
        config = FDAPIConfig()

        # Verify config loaded from environment
        assert config.base_url == "https://env-test.example.com"
        assert config.api_key == "env-api-key"
        assert config.timeout == 60
        assert config.max_retries == 5

        async with FDAPIClient(config) as client:
            assert str(client._client.base_url) == "https://env-test.example.com"
            assert client._client.headers["Authorization"] == "Bearer env-api-key"
            assert client._client.timeout.read == 60.0

    @pytest.mark.asyncio
    @respx.mock
    async def test_different_content_types_endpoints(self, mock_config):
        """Test integration with different content type endpoints."""
        content_types = [
            "albums", "documents", "photos", "stories", "tags", "events",
            "brightcove-videos", "diva-videos", "hero-videos", "jwplayer-videos", "forms"
        ]

        for content_type in content_types:
            respx.get(f"{mock_config.base_url}/v1/content/en-gb/{content_type}").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "items": [{"id": f"{content_type}-1", "type": content_type}],
                        "pagination": {"total": 1}
                    }
                )
            )

        async with FDAPIClient(mock_config) as client:
            for content_type in content_types:
                response = await client.get(f"/v1/content/en-gb/{content_type}")
                assert response["items"][0]["type"] == content_type
                assert response["pagination"]["total"] == 1


@pytest.mark.asyncio
@pytest.mark.slow
class TestRealConnectivityScenarios:
    """Tests that simulate real connectivity scenarios (marked as slow)."""

    @pytest.fixture
    def real_config(self, monkeypatch):
        """Configuration for testing against a real or mock FDAPI instance."""
        # Use httpbin.org for testing real HTTP connectivity
        monkeypatch.setenv("FDAPI_BASE_URL", os.environ.get(
            "FDAPI_TEST_URL", "https://httpbin.org"))
        monkeypatch.setenv("FDAPI_TIMEOUT", "5")
        monkeypatch.setenv("FDAPI_MAX_RETRIES", "1")
        monkeypatch.delenv("FDAPI_API_KEY", raising=False)
        return FDAPIConfig()

    @pytest.mark.asyncio
    async def test_real_http_connectivity(self, real_config):
        """Test real HTTP connectivity using httpbin.org as test endpoint."""
        async with FDAPIClient(real_config) as client:
            # Use httpbin.org's json endpoint for testing
            try:
                response = await client.get("/json")
                # httpbin.org returns a JSON object
                assert isinstance(response, dict)
            except Exception as e:
                # If httpbin.org is unavailable, skip the test
                pytest.skip(f"Real connectivity test failed: {e}")

    @pytest.mark.asyncio
    async def test_invalid_domain_connection(self, monkeypatch):
        """Test connection to invalid domain."""
        monkeypatch.setenv(
            "FDAPI_BASE_URL", "https://this-domain-should-not-exist-12345.com")
        monkeypatch.setenv("FDAPI_TIMEOUT", "2")
        monkeypatch.setenv("FDAPI_MAX_RETRIES", "1")
        config = FDAPIConfig()

        async with FDAPIClient(config) as client:
            # health_check() method catches exceptions and returns False
            result = await client.health_check()
            assert result is False

            # Direct request should raise exception
            with pytest.raises(FDAPIConnectionError):
                await client.get("/v1/test")

    @pytest.mark.asyncio
    async def test_client_context_manager(self, mock_config):
        """Test client can be used as async context manager."""
        async with FDAPIClient(mock_config) as client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)
            assert str(client._client.base_url) == "https://test-fdapi.example.com"

        # Client should be closed after context exit
        assert client._client is None

    @pytest.mark.asyncio
    async def test_client_manual_lifecycle(self, mock_config):
        """Test manual client start/stop lifecycle."""
        client = FDAPIClient(mock_config)

        # Initially not started
        assert client._client is None

        # Start client
        await client.start()
        assert client._client is not None

        # Close client
        await client.close()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_client_headers_with_auth(self, mock_config):
        """Test client sets correct headers with authentication."""
        async with FDAPIClient(mock_config) as client:
            headers = client._client.headers

            assert headers["User-Agent"] == "FDAPI-MCP-Server/0.1.0"
            assert headers["Accept"] == "application/json"
            assert headers["Content-Type"] == "application/json"
            assert headers["Authorization"] == "Bearer test-api-key-123"

    @pytest.mark.asyncio
    async def test_client_headers_without_auth(self, mock_config_no_auth):
        """Test client sets correct headers without authentication."""
        async with FDAPIClient(mock_config_no_auth) as client:
            headers = client._client.headers

            assert headers["User-Agent"] == "FDAPI-MCP-Server/0.1.0"
            assert headers["Accept"] == "application/json"
            assert headers["Content-Type"] == "application/json"
            assert "Authorization" not in headers

    @pytest.mark.asyncio
    @respx.mock
    async def test_successful_get_request(self, mock_config):
        """Test successful GET request."""
        # Mock successful response
        respx.get("https://test-fdapi.example.com/v1/content/en-gb/albums/test-album").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "123",
                    "title": "Test Album",
                    "slug": "test-album",
                    "language": "en-gb"
                }
            )
        )

        async with FDAPIClient(mock_config) as client:
            response = await client.get("/v1/content/en-gb/albums/test-album")

            assert response["id"] == "123"
            assert response["title"] == "Test Album"
            assert response["slug"] == "test-album"
            assert response["language"] == "en-gb"

    @pytest.mark.asyncio
    @respx.mock
    async def test_successful_post_request(self, mock_config):
        """Test successful POST request."""
        request_data = {"name": "Test Form", "email": "test@example.com"}

        respx.post("https://test-fdapi.example.com/v1/forms/submit").mock(
            return_value=httpx.Response(
                200,
                json={"status": "success", "id": "form-123"}
            )
        )

        async with FDAPIClient(mock_config) as client:
            response = await client.post("/v1/forms/submit", json=request_data)

            assert response["status"] == "success"
            assert response["id"] == "form-123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_with_query_params(self, mock_config):
        """Test GET request with query parameters."""
        respx.get("https://test-fdapi.example.com/v1/content/en-gb/albums").mock(
            return_value=httpx.Response(
                200,
                json={
                    "items": [
                        {"id": "1", "title": "Album 1"},
                        {"id": "2", "title": "Album 2"}
                    ],
                    "total": 2,
                    "page": 1,
                    "limit": 10
                }
            )
        )

        async with FDAPIClient(mock_config) as client:
            response = await client.get(
                "/v1/content/en-gb/albums",
                params={"page": 1, "limit": 10}
            )

            assert len(response["items"]) == 2
            assert response["total"] == 2
            assert response["page"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_404_error_handling(self, mock_config):
        """Test handling of 404 Not Found errors."""
        respx.get("https://test-fdapi.example.com/v1/content/en-gb/albums/nonexistent").mock(
            return_value=httpx.Response(
                404,
                json={"message": "Album not found", "error": "NOT_FOUND"}
            )
        )

        async with FDAPIClient(mock_config) as client:
            with pytest.raises(FDAPIResponseError) as exc_info:
                await client.get("/v1/content/en-gb/albums/nonexistent")

            assert "HTTP 404" in str(exc_info.value)
            assert "Album not found" in str(exc_info.value)
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @respx.mock
    async def test_500_error_handling(self, mock_config):
        """Test handling of 500 Internal Server Error."""
        respx.get("https://test-fdapi.example.com/v1/content/en-gb/albums/error").mock(
            return_value=httpx.Response(
                500,
                json={"message": "Internal server error"}
            )
        )

        async with FDAPIClient(mock_config) as client:
            with pytest.raises(FDAPIResponseError) as exc_info:
                await client.get("/v1/content/en-gb/albums/error")

            assert "HTTP 500" in str(exc_info.value)
            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    @respx.mock
    async def test_connection_error_with_retry(self, mock_config):
        """Test connection error handling with retry logic."""
        # Mock connection failures
        respx.get("https://test-fdapi.example.com/v1/health").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        async with FDAPIClient(mock_config) as client:
            with pytest.raises(FDAPIConnectionError) as exc_info:
                await client.get("/v1/health")

            assert "Connection failed after 3 attempts" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_error_with_retry(self, mock_config):
        """Test timeout error handling with retry logic."""
        # Mock timeout failures
        respx.get("https://test-fdapi.example.com/v1/health").mock(
            side_effect=httpx.TimeoutException("Request timeout")
        )

        async with FDAPIClient(mock_config) as client:
            with pytest.raises(FDAPIConnectionError) as exc_info:
                await client.get("/v1/health")

            assert "Request timeout after 3 attempts" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_retry_success_after_failure(self, mock_config):
        """Test successful request after initial failures."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise httpx.ConnectError("Connection failed")
            return httpx.Response(200, json={"status": "ok"})

        respx.get("https://test-fdapi.example.com/v1/health").mock(
            side_effect=side_effect
        )

        async with FDAPIClient(mock_config) as client:
            response = await client.get("/v1/health")
            assert response["status"] == "ok"
            assert call_count == 3  # Failed twice, succeeded on third try

    @pytest.mark.asyncio
    @respx.mock
    async def test_invalid_json_response(self, mock_config):
        """Test handling of invalid JSON responses."""
        respx.get("https://test-fdapi.example.com/v1/content/en-gb/albums/test").mock(
            return_value=httpx.Response(200, text="<html>Not JSON</html>")
        )

        async with FDAPIClient(mock_config) as client:
            with pytest.raises(FDAPIResponseError) as exc_info:
                await client.get("/v1/content/en-gb/albums/test")

            assert "Failed to parse JSON response" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_check_success(self, mock_config):
        """Test successful health check."""
        respx.get("https://test-fdapi.example.com/v1/health").mock(
            return_value=httpx.Response(200, json={"status": "healthy"})
        )

        async with FDAPIClient(mock_config) as client:
            result = await client.health_check()
            assert result is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_check_failure(self, mock_config):
        """Test failed health check."""
        respx.get("https://test-fdapi.example.com/v1/health").mock(
            return_value=httpx.Response(500, json={"status": "unhealthy"})
        )

        async with FDAPIClient(mock_config) as client:
            result = await client.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_client_not_started_error(self, mock_config):
        """Test error when trying to use client before starting."""
        client = FDAPIClient(mock_config)

        with pytest.raises(FDAPIError) as exc_info:
            _ = client.client

        assert "Client not started" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_real_fdapi_endpoints_structure(self, mock_config):
        """Test with realistic FDAPI endpoint structures from API spec."""
        # Test album detail endpoint
        respx.get("https://test-fdapi.example.com/v1/content/en-gb/albums/test-album").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "album-123",
                    "title": "Test Album",
                    "slug": "test-album",
                    "description": "A test album",
                    "language": "en-gb",
                    "published_date": "2024-01-01T00:00:00Z",
                    "images": [],
                    "tags": []
                }
            )
        )

        # Test albums listing endpoint
        respx.get("https://test-fdapi.example.com/v1/content/en-gb/albums").mock(
            return_value=httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": "album-123",
                            "title": "Test Album",
                            "slug": "test-album",
                            "language": "en-gb"
                        }
                    ],
                    "pagination": {
                        "page": 1,
                        "limit": 20,
                        "total": 1,
                        "pages": 1
                    }
                }
            )
        )

        async with FDAPIClient(mock_config) as client:
            # Test album detail
            album = await client.get("/v1/content/en-gb/albums/test-album")
            assert album["id"] == "album-123"
            assert album["title"] == "Test Album"
            assert album["language"] == "en-gb"

            # Test albums listing
            albums = await client.get("/v1/content/en-gb/albums")
            assert len(albums["items"]) == 1
            assert albums["pagination"]["total"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_multiple_language_support(self, mock_config):
        """Test support for multiple languages as per API spec."""
        languages = ["en-gb", "fr-fr", "es-es", "ar-sa", "de-de", "nd-nd"]

        for lang in languages:
            respx.get(f"https://test-fdapi.example.com/v1/content/{lang}/albums/test").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "id": "album-123",
                        "title": f"Test Album ({lang})",
                        "language": lang
                    }
                )
            )

        async with FDAPIClient(mock_config) as client:
            for lang in languages:
                response = await client.get(f"/v1/content/{lang}/albums/test")
                assert response["language"] == lang
                assert lang in response["title"]


class TestFDAPIConfigurationIntegration:
    """Integration tests for configuration scenarios."""

    @pytest.fixture
    def mock_env_vars(self, monkeypatch):
        """Set up test environment variables."""
        monkeypatch.setenv("FDAPI_BASE_URL", "https://test-fdapi.example.com")
        monkeypatch.setenv("FDAPI_API_KEY", "test-api-key-123")
        monkeypatch.setenv("FDAPI_TIMEOUT", "10")
        monkeypatch.setenv("FDAPI_MAX_RETRIES", "2")

    @pytest.fixture
    def mock_config(self, mock_env_vars):
        """Create a test configuration using environment variables."""
        return FDAPIConfig()

    @pytest.mark.asyncio
    async def test_environment_variable_configuration(self, monkeypatch):
        """Test client with configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("FDAPI_BASE_URL", "https://env-test.example.com")
        monkeypatch.setenv("FDAPI_API_KEY", "env-api-key")
        monkeypatch.setenv("FDAPI_TIMEOUT", "60")
        # Create config that reads from environment
        monkeypatch.setenv("FDAPI_MAX_RETRIES", "5")
        config = FDAPIConfig()

        # Verify config loaded from environment
        assert config.base_url == "https://env-test.example.com"
        assert config.api_key == "env-api-key"
        assert config.timeout == 60
        assert config.max_retries == 5

        async with FDAPIClient(config) as client:
            assert str(client._client.base_url) == "https://env-test.example.com"
            assert client._client.headers["Authorization"] == "Bearer env-api-key"
            assert client._client.timeout.read == 60.0

    @pytest.mark.asyncio
    @respx.mock
    async def test_different_content_types_endpoints(self, mock_config):
        """Test integration with different content type endpoints."""
        content_types = [
            "albums", "documents", "photos", "stories", "tags", "events",
            "brightcove-videos", "diva-videos", "hero-videos", "jwplayer-videos", "forms"
        ]

        for content_type in content_types:
            respx.get(f"{mock_config.base_url}/v1/content/en-gb/{content_type}").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "items": [{"id": f"{content_type}-1", "type": content_type}],
                        "pagination": {"total": 1}
                    }
                )
            )

        async with FDAPIClient(mock_config) as client:
            for content_type in content_types:
                response = await client.get(f"/v1/content/en-gb/{content_type}")
                assert response["items"][0]["type"] == content_type
                assert response["pagination"]["total"] == 1


@pytest.mark.asyncio
@pytest.mark.slow
class TestRealConnectivityScenarios:
    """Tests that simulate real connectivity scenarios (marked as slow)."""

    @pytest.fixture
    def real_config(self):
        """Configuration for testing against a real or mock FDAPI instance."""
        return FDAPIConfig(
            base_url=os.environ.get("FDAPI_TEST_URL", "https://httpbin.org"),
            timeout=5,
            max_retries=1
        )

    @pytest.mark.asyncio
    async def test_real_http_connectivity(self, real_config):
        """Test real HTTP connectivity using httpbin.org as test endpoint."""
        async with FDAPIClient(real_config) as client:
            # Use httpbin.org's json endpoint for testing
            try:
                response = await client.get("/json")
                # httpbin.org returns a JSON object
                assert isinstance(response, dict)
            except Exception as e:
                # If httpbin.org is unavailable, skip the test
                pytest.skip(
                    f"Real connectivity test failed: {e}")    @ pytest.mark.asyncio

    async def test_invalid_domain_connection(self):
        """Test connection to invalid domain."""
        config = FDAPIConfig(
            base_url="https://this-domain-should-not-exist-12345.com",
            timeout=2,
            max_retries=1
        )

        async with FDAPIClient(config) as client:
            # health_check() method catches exceptions and returns False
            result = await client.health_check()
            assert result is False

            # Direct request should raise exception
            with pytest.raises(FDAPIConnectionError):
                await client.get("/v1/test")
