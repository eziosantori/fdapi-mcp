# Copilot Instructions for FDAPI MCP Server Development

## Project Overview

You are working on the **FDAPI MCP Server**, a Model Context Protocol server that provides AI tools to interact with the FDAPI endpoints. This project uses **Python 3.10+**, **uv** for dependency management, and **FastMCP 2.0** for the MCP server framework.

## Development Philosophy

### Incremental Development Approach

This project follows a **strict incremental development methodology**:

- Each endpoint type is implemented completely before moving to the next
- **100% test coverage** is required for each endpoint before proceeding
- Each phase must result in a fully functional MCP server for the implemented endpoints
- Never implement multiple endpoint types simultaneously

### Quality Standards

- **Type Safety First:** Use type hints for all functions and variables
- **Test-Driven Development:** Write tests before or alongside implementation
- **Documentation:** Every public function must have docstrings
- **Error Handling:** Comprehensive error handling with meaningful messages for LLMs

## Technology Stack Guidelines

### Python and uv

- **Use uv exclusively** for dependency management and virtual environment
- Run commands with `uv run <command>` in the project directory
- Add dependencies with `uv add <package>`
- Use `uv sync` to sync dependencies

### FastMCP 2.0 Framework

- **Primary Framework:** Use FastMCP 2.0 for all MCP server functionality
- **Tool Registration:** Register each FDAPI endpoint as an MCP tool
- **Parameter Validation:** Use FastMCP's parameter validation features
- **Response Formatting:** Format responses optimally for LLM consumption

### HTTP Client (httpx)

- **Async-First:** Use httpx AsyncClient for all API calls
- **Connection Management:** Reuse connections with proper client lifecycle
- **Error Handling:** Handle HTTP errors with specific exception types
- **Timeouts:** Configure appropriate timeouts for all requests

### Configuration (pydantic-settings)

- **Type-Safe Config:** Use pydantic-settings for all configuration
- **Environment Variables:** Support environment variable configuration
- **Validation:** Validate all configuration at startup
- **Future-Proof:** Include optional API key support for future authentication

## Code Organization Patterns

### Project Structure

```
src/fdapi_mcp/
├── __init__.py
├── server.py              # FastMCP server entry point
├── client.py              # FDAPI HTTP client
├── config.py              # Configuration management
├── exceptions.py          # Custom exceptions
├── models/                # Pydantic models by content type
│   ├── __init__.py
│   ├── base.py            # Base models and common types
│   ├── albums.py          # Album-specific models
│   └── ...                # Other content type models
└── tools/                 # MCP tools by content type
    ├── __init__.py
    ├── base.py            # Base tool functionality
    ├── albums.py          # Album MCP tools
    └── ...                # Other content type tools
```

### Naming Conventions

#### MCP Tools

- **Detail Tools:** `fdapi_get_{content_type}` (e.g., `fdapi_get_album`)
- **List Tools:** `fdapi_list_{content_type}s` (e.g., `fdapi_list_albums`)
- **Consistent Parameters:** Use `language`, `slug`, `page`, `limit` consistently

#### Python Code

- **Functions:** snake_case
- **Classes:** PascalCase
- **Constants:** UPPER_SNAKE_CASE
- **Private:** Leading underscore

#### Files and Modules

- **Models:** `{content_type}.py` (e.g., `albums.py`)
- **Tools:** `{content_type}.py` matching model files
- **Tests:** `test_{module}.py`

## Implementation Patterns

### Configuration Pattern

```python
from pydantic_settings import BaseSettings
from typing import Optional

class FDAPIConfig(BaseSettings):
    base_url: str = "https://api.example.com"
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

    class Config:
        env_prefix = "FDAPI_"
        env_file = ".env"
```

### HTTP Client Pattern

```python
import httpx
from typing import Optional, Dict, Any

class FDAPIClient:
    def __init__(self, config: FDAPIConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def get_content(
        self,
        content_type: str,
        language: str,
        slug: str
    ) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("Client not initialized")

        url = f"/v1/content/{language}/{content_type}/{slug}"
        response = await self._client.get(url)
        response.raise_for_status()
        return response.json()
```

### Pydantic Model Pattern

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

class BaseContent(BaseModel):
    title: str
    slug: str
    self_url: str = Field(alias="selfUrl")
    translation_id: UUID = Field(alias="_translationId")
    entity_id: UUID = Field(alias="_entityId")
    fields: Dict[str, Any]
    type: str

    class Config:
        allow_population_by_field_name = True

class Album(BaseContent):
    # Album-specific fields
    pass
```

### MCP Tool Pattern

```python
from fastmcp import MCP
from typing import Optional

class AlbumTools:
    def __init__(self, client: FDAPIClient):
        self.client = client

    async def get_album(
        self,
        slug: str,
        language: str = "en-gb"
    ) -> dict:
        """Get album details by slug.

        Args:
            slug: Album identifier
            language: Content language (default: en-gb)

        Returns:
            Album details as dictionary

        Raises:
            HTTPError: If album not found or API error
        """
        async with self.client as client:
            return await client.get_content("albums", language, slug)
```

### Error Handling Pattern

```python
from typing import Dict, Any, Optional

class FDAPIError(Exception):
    """Base exception for FDAPI errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class ContentNotFoundError(FDAPIError):
    """Raised when content is not found."""
    pass

class ValidationError(FDAPIError):
    """Raised when request validation fails."""
    pass

# Usage in tools
try:
    content = await client.get_content(content_type, language, slug)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        raise ContentNotFoundError(
            f"{content_type.title()} with slug '{slug}' not found",
            error_code="CONTENT_NOT_FOUND",
            details={"content_type": content_type, "slug": slug, "language": language}
        )
    raise FDAPIError(f"API error: {e.response.status_code}")
```

## Testing Guidelines

### Test Structure

```
tests/
├── conftest.py               # pytest fixtures
├── unit/
│   ├── test_config.py        # Configuration tests
│   ├── test_client.py        # HTTP client tests
│   └── tools/
│       ├── test_albums.py    # Album tool tests
│       └── ...
├── integration/
│   ├── test_api.py          # API integration tests
│   └── test_mcp.py          # MCP integration tests
└── fixtures/
    ├── api_responses/       # Mock API responses
    └── test_data.py         # Test data generators
```

### Test Patterns

#### Unit Test Pattern

```python
import pytest
from unittest.mock import AsyncMock, patch
from fdapi_mcp.tools.albums import AlbumTools
from fdapi_mcp.exceptions import ContentNotFoundError

@pytest.fixture
def mock_client():
    client = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_get_album_success(mock_client):
    # Arrange
    mock_response = {"title": "Test Album", "slug": "test-album"}
    mock_client.get_content.return_value = mock_response

    tools = AlbumTools(mock_client)

    # Act
    result = await tools.get_album("test-album", "en-gb")

    # Assert
    assert result == mock_response
    mock_client.get_content.assert_called_once_with("albums", "en-gb", "test-album")

@pytest.mark.asyncio
async def test_get_album_not_found(mock_client):
    # Arrange
    mock_client.get_content.side_effect = ContentNotFoundError("Not found")
    tools = AlbumTools(mock_client)

    # Act & Assert
    with pytest.raises(ContentNotFoundError):
        await tools.get_album("nonexistent", "en-gb")
```

#### Integration Test Pattern

```python
import pytest
import httpx
from fdapi_mcp.client import FDAPIClient
from fdapi_mcp.config import FDAPIConfig

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_call():
    """Test against real API (requires network)."""
    config = FDAPIConfig(base_url="https://test-api.example.com")

    async with FDAPIClient(config) as client:
        # Test with known test data
        result = await client.get_content("albums", "en-gb", "test-album")
        assert "title" in result
        assert "slug" in result
```

### Coverage Requirements

- **Minimum Coverage:** 100% for each completed endpoint before moving to next
- **Coverage Tools:** Use `pytest-cov` for coverage reporting
- **Coverage Command:** `uv run pytest --cov=src/fdapi_mcp --cov-report=html`
- **Coverage Validation:** Fail builds if coverage drops below 100%

## API Integration Guidelines

### FDAPI Specifics

- **Base URL:** Configurable via `FDAPI_BASE_URL` environment variable
- **Authentication:** None currently, but support `FDAPI_API_KEY` for future
- **Languages:** Support en-gb (default), fr-fr, es-es, ar-sa, de-de, nd-nd
- **URL Pattern:** `/v1/content/{language}/{content_type}/{slug}`

### Content Types Priority Order

1. **Core Types:** Albums, Documents, Photos, Stories, Tags, Events, Forms, Teams
2. **Video Types:** Brightcove, Diva, Hero, JWPlayer videos
3. **Additional Types:** Accordions, Advertisements, Page Builder assets, etc.

### Parameter Validation

```python
from typing import Literal

Language = Literal["en-gb", "fr-fr", "es-es", "ar-sa", "de-de", "nd-nd"]

def validate_language(language: str) -> Language:
    """Validate language parameter."""
    valid_languages = ["en-gb", "fr-fr", "es-es", "ar-sa", "de-de", "nd-nd"]
    if language not in valid_languages:
        raise ValidationError(
            f"Invalid language '{language}'",
            error_code="INVALID_LANGUAGE",
            details={"valid_languages": valid_languages}
        )
    return language
```

## MCP Server Development

### FastMCP 2.0 Best Practices

- **Server Initialization:** Initialize once, register all tools
- **Tool Registration:** Use decorators for clean tool registration
- **Parameter Types:** Leverage FastMCP's type system for validation
- **Response Format:** Return structured data that LLMs can easily parse

### Tool Registration Pattern

```python
from fastmcp import MCP

app = MCP("fdapi-server")

@app.tool()
async def fdapi_get_album(
    slug: str,
    language: str = "en-gb"
) -> dict:
    """Get album details by slug.

    Args:
        slug: Album identifier
        language: Content language (default: en-gb)

    Returns:
        Album details including title, fields, and metadata
    """
    # Implementation
```

### Error Response Format for LLMs

```python
def format_error_for_llm(error: FDAPIError) -> dict:
    """Format errors in a way LLMs can understand and act upon."""
    return {
        "success": False,
        "error": {
            "type": error.__class__.__name__,
            "message": error.message,
            "code": error.error_code,
            "details": error.details,
            "suggestion": _get_error_suggestion(error)
        }
    }

def _get_error_suggestion(error: FDAPIError) -> str:
    """Provide helpful suggestions for LLMs."""
    if isinstance(error, ContentNotFoundError):
        return "Try checking the slug spelling or use the list endpoint to find available content."
    elif isinstance(error, ValidationError):
        return "Check the parameter values and ensure they match the required format."
    return "Please check the request parameters and try again."
```

## Development Workflow

### Phase Implementation Process

1. **Read Current Phase:** Check TASKS.MD for current phase requirements
2. **Create Models:** Start with Pydantic models for the content type
3. **Implement Client:** Add HTTP client methods for the endpoints
4. **Create Tools:** Implement MCP tools using FastMCP decorators
5. **Write Tests:** Achieve 100% coverage before proceeding
6. **Update Documentation:** Update README and tool documentation
7. **Mark Complete:** Update TASKS.MD with completion status

### Daily Development Checklist

- [ ] Check TASKS.MD for current phase and next tasks
- [ ] Run tests: `uv run pytest`
- [ ] Check coverage: `uv run pytest --cov=src`
- [ ] Lint code: `uv run flake8 src tests`
- [ ] Format code: `uv run black src tests`
- [ ] Type check: `uv run mypy src`
- [ ] Update documentation as needed

### Git Workflow

- **Commit Messages:** Use conventional commit format
- **Branch Names:** `feature/endpoint-{content-type}` (e.g., `feature/endpoint-albums`)
- **PR Requirements:** Tests passing, 100% coverage, documentation updated

## Common Patterns and Anti-Patterns

### ✅ DO

- Use async/await for all I/O operations
- Implement proper error handling with custom exceptions
- Write comprehensive tests before marking tasks complete
- Use type hints for all function parameters and returns
- Validate all inputs before making API calls
- Format responses for optimal LLM consumption
- Follow the incremental development approach strictly

### ❌ DON'T

- Implement multiple content types simultaneously
- Skip test coverage requirements
- Use blocking I/O operations
- Ignore error handling
- Hard-code configuration values
- Proceed to next phase without completing current phase
- Make breaking changes to MCP tool interfaces

## Debugging and Troubleshooting

### Common Issues

1. **Import Errors:** Ensure you're using `uv run` for all commands
2. **Async Issues:** Always use `async with` for HTTP clients
3. **Type Errors:** Run `mypy` regularly to catch type issues early
4. **Test Failures:** Use `pytest -v` for verbose test output

### Debugging Tools

- **Logging:** Use structured logging with appropriate levels
- **Print Debugging:** Use `print()` for quick debugging, remove before commit
- **Pytest Debugging:** Use `pytest --pdb` to drop into debugger on failures
- **Coverage Analysis:** Use `--cov-report=html` to see uncovered lines

### Performance Considerations

- **Connection Reuse:** Always use async context managers for HTTP clients
- **Timeout Configuration:** Set appropriate timeouts for all HTTP requests
- **Error Boundaries:** Fail fast on configuration errors
- **Memory Usage:** Be mindful of large API responses

## Documentation Standards

### Docstring Format

```python
async def get_content(
    self,
    content_type: str,
    language: str,
    slug: str
) -> Dict[str, Any]:
    """Retrieve content from FDAPI.

    Args:
        content_type: Type of content (albums, documents, etc.)
        language: Language code (en-gb, fr-fr, etc.)
        slug: Content identifier

    Returns:
        Content data as dictionary

    Raises:
        ContentNotFoundError: If content doesn't exist
        ValidationError: If parameters are invalid
        FDAPIError: For other API errors

    Example:
        >>> async with client:
        ...     album = await client.get_content("albums", "en-gb", "my-album")
        ...     print(album["title"])
    """
```

### README Updates

Always update the README when:

- Adding new MCP tools
- Changing configuration options
- Adding new dependencies
- Modifying setup instructions

## Security Considerations

### Configuration Security

- Never commit API keys or sensitive data
- Use environment variables for all configuration
- Validate all configuration at startup
- Log configuration (but mask sensitive values)

### Input Validation

- Validate all parameters before API calls
- Sanitize user inputs appropriately
- Use type checking for parameter validation
- Provide clear error messages for invalid inputs

Remember: This project prioritizes **quality over speed**. Take time to implement each endpoint correctly with full test coverage before moving to the next phase.
