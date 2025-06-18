"""Exception classes for FDAPI MCP Server."""

from typing import Optional


class FDAPIError(Exception):
    """Base exception for all FDAPI-related errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        """Return string representation."""
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class FDAPIConnectionError(FDAPIError):
    """Exception raised for connection-related errors."""
    pass


class FDAPIResponseError(FDAPIError):
    """Exception raised for HTTP response errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None):
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, details)
        self.status_code = status_code

    def __str__(self) -> str:
        """Return string representation."""
        if self.status_code:
            base = f"HTTP {self.status_code}: {self.message}"
        else:
            base = self.message

        if self.details:
            return f"{base} - {self.details}"
        return base


class FDAPIAuthenticationError(FDAPIError):
    """Exception raised for authentication-related errors."""
    pass


class FDAPIValidationError(FDAPIError):
    """Exception raised for data validation errors."""
    pass


class FDAPINotFoundError(FDAPIResponseError):
    """Exception raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str, details: Optional[str] = None):
        """Initialize the exception.

        Args:
            resource: Type of resource that wasn't found
            identifier: Resource identifier
            details: Additional error details
        """
        message = f"{resource} '{identifier}' not found"
        super().__init__(message, status_code=404, details=details)
        self.resource = resource
        self.identifier = identifier


class FDAPIRateLimitError(FDAPIResponseError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, retry_after: Optional[int] = None, details: Optional[str] = None):
        """Initialize the exception.

        Args:
            retry_after: Seconds to wait before retrying
            details: Additional error details
        """
        message = "Rate limit exceeded"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after
