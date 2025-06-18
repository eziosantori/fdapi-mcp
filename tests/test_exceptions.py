"""Test exceptions module."""

import pytest
from fdapi_mcp.exceptions import (
    FDAPIError,
    FDAPIConnectionError,
    FDAPIResponseError,
    FDAPIAuthenticationError,
    FDAPIValidationError,
    FDAPINotFoundError,
    FDAPIRateLimitError,
)


def test_fdapi_error():
    """Test base FDAPI error."""
    error = FDAPIError("Test error")
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.details is None


def test_fdapi_error_with_details():
    """Test FDAPI error with details."""
    error = FDAPIError("Test error", "Additional details")
    assert str(error) == "Test error - Additional details"
    assert error.message == "Test error"
    assert error.details == "Additional details"


def test_fdapi_connection_error():
    """Test FDAPI connection error."""
    error = FDAPIConnectionError("Connection failed")
    assert isinstance(error, FDAPIError)
    assert str(error) == "Connection failed"


def test_fdapi_response_error():
    """Test FDAPI response error."""
    error = FDAPIResponseError("HTTP error", status_code=404)
    assert isinstance(error, FDAPIError)
    assert str(error) == "HTTP 404: HTTP error"
    assert error.status_code == 404


def test_fdapi_response_error_with_details():
    """Test FDAPI response error with details."""
    error = FDAPIResponseError("HTTP error", status_code=500, details="Server overload")
    assert str(error) == "HTTP 500: HTTP error - Server overload"


def test_fdapi_not_found_error():
    """Test FDAPI not found error."""
    error = FDAPINotFoundError("Album", "test-slug")
    assert isinstance(error, FDAPIResponseError)
    assert str(error) == "HTTP 404: Album 'test-slug' not found"
    assert error.status_code == 404
    assert error.resource == "Album"
    assert error.identifier == "test-slug"


def test_fdapi_rate_limit_error():
    """Test FDAPI rate limit error."""
    error = FDAPIRateLimitError(retry_after=60)
    assert isinstance(error, FDAPIResponseError)
    assert "Rate limit exceeded (retry after 60s)" in str(error)
    assert error.status_code == 429
    assert error.retry_after == 60


def test_fdapi_authentication_error():
    """Test FDAPI authentication error."""
    error = FDAPIAuthenticationError("Invalid API key")
    assert isinstance(error, FDAPIError)
    assert str(error) == "Invalid API key"


def test_fdapi_validation_error():
    """Test FDAPI validation error."""
    error = FDAPIValidationError("Invalid data format")
    assert isinstance(error, FDAPIError)
    assert str(error) == "Invalid data format"
