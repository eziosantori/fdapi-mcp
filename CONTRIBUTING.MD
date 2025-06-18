# Contributing to FDAPI MCP Server

Thank you for your interest in contributing to the FDAPI MCP Server! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Requirements](#documentation-requirements)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)

## Code of Conduct

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) installed
- Git configured with your name and email
- Basic understanding of FastMCP 2.0 and MCP protocol

### Development Environment Setup

1. **Fork and clone the repository**:

   ```bash
   git clone https://github.com/your-username/fdapi-mcp-server.git
   cd fdapi-mcp-server
   ```

2. **Set up the development environment**:

   ```bash
   uv sync
   ```

3. **Create environment file**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Verify setup**:
   ```bash
   uv run pytest
   uv run python src/fdapi_mcp/server.py --help
   ```

## Development Process

### Incremental Development Methodology

This project follows a **strict incremental development approach**:

1. **One Endpoint Type at a Time**: Never work on multiple content types simultaneously
2. **Complete Before Proceeding**: Each endpoint must have 100% test coverage before moving to the next
3. **Phase-Based Development**: Follow the phases outlined in [TASKS.MD](TASKS.MD)

### Workflow Steps

1. **Check Current Phase**: Review [TASKS.MD](TASKS.MD) for the current development phase
2. **Claim a Task**: Comment on the issue or task to claim it
3. **Create Feature Branch**: `git checkout -b feature/endpoint-{content-type}`
4. **Implement with Tests**: Write code and tests simultaneously
5. **Verify Coverage**: Ensure 100% test coverage before proceeding
6. **Update Documentation**: Update relevant documentation
7. **Submit Pull Request**: Follow the PR template

### Task Claiming Process

To avoid conflicts:

1. Check [TASKS.MD](TASKS.MD) for available tasks in the current phase
2. Comment on the task or create an issue to claim it
3. Maintainers will assign the task to you
4. Begin work only after assignment confirmation

## Project Structure

### Directory Layout

```
fdapi-mcp-server/
├── .vscode/                    # VS Code configuration
│   └── copilot-instructions.md # Development guidelines
├── src/
│   └── fdapi_mcp/
│       ├── __init__.py
│       ├── server.py           # Main MCP server
│       ├── client.py           # FDAPI HTTP client
│       ├── config.py           # Configuration management
│       ├── exceptions.py       # Custom exceptions
│       ├── models/             # Pydantic models
│       │   ├── __init__.py
│       │   ├── base.py         # Base models
│       │   └── {content}.py    # Content-specific models
│       └── tools/              # MCP tools
│           ├── __init__.py
│           ├── base.py         # Base tool functionality
│           └── {content}.py    # Content-specific tools
├── tests/
│   ├── conftest.py            # pytest configuration
│   ├── unit/                  # Unit tests
│   │   ├── test_client.py
│   │   ├── test_config.py
│   │   └── tools/
│   │       └── test_{content}.py
│   ├── integration/           # Integration tests
│   │   ├── test_api.py
│   │   └── test_mcp.py
│   └── fixtures/              # Test data
│       ├── api_responses/
│       └── test_data.py
├── docs/                      # Additional documentation
├── scripts/                   # Utility scripts
├── pyproject.toml            # Project configuration
├── .env.example              # Environment template
└── README.md                 # Main documentation
```

### File Naming Conventions

- **Models**: `{content_type}.py` (e.g., `albums.py`)
- **Tools**: `{content_type}.py` (matching model files)
- **Tests**: `test_{module}.py`
- **Branches**: `feature/endpoint-{content-type}`

## Coding Standards

### Python Code Style

#### Formatting and Linting

- **Formatter**: black with default settings
- **Linter**: flake8 with project-specific configuration
- **Type Checker**: mypy with strict settings
- **Import Sorting**: isort (configured in pyproject.toml)

#### Code Quality Commands

```bash
# Format code
uv run black src tests

# Lint code
uv run flake8 src tests

# Type checking
uv run mypy src

# Sort imports
uv run isort src tests

# Run all quality checks
uv run python scripts/check-quality.py
```

#### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: Leading underscore (`_private`)
- **MCP Tools**: `fdapi_{action}_{content_type}` (e.g., `fdapi_get_album`)

### Type Hints

All functions must include type hints:

```python
from typing import Dict, Any, Optional, List
from uuid import UUID

async def get_content(
    self,
    content_type: str,
    language: str,
    slug: str
) -> Dict[str, Any]:
    """Get content from FDAPI."""
    pass

class ContentModel(BaseModel):
    title: str
    slug: str
    entity_id: UUID
    fields: Dict[str, Any]
```

### Documentation Standards

#### Docstrings

Use Google-style docstrings:

```python
async def fetch_albums(
    self,
    language: str = "en-gb",
    page: int = 1,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Fetch albums from FDAPI.

    Args:
        language: Language code (en-gb, fr-fr, etc.)
        page: Page number for pagination
        limit: Number of items per page

    Returns:
        List of album dictionaries

    Raises:
        ValidationError: If parameters are invalid
        FDAPIError: If API request fails

    Example:
        >>> client = FDAPIClient(config)
        >>> albums = await client.fetch_albums("en-gb", 1, 10)
        >>> print(len(albums))
        10
    """
```

#### Comments

- Use comments sparingly for complex logic
- Prefer descriptive function and variable names
- Comment the "why", not the "what"

## Testing Guidelines

### Test Coverage Requirements

- **100% Coverage**: Required for each endpoint before proceeding to next
- **Test Categories**: Unit tests, integration tests, and fixtures
- **Coverage Tools**: pytest-cov for coverage reporting

### Test Structure

#### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from fdapi_mcp.tools.albums import AlbumTools
from fdapi_mcp.exceptions import ContentNotFoundError

@pytest.fixture
def mock_client():
    return AsyncMock()

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
```

#### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_integration():
    """Test against real API (requires FDAPI_BASE_URL)."""
    config = FDAPIConfig()

    async with FDAPIClient(config) as client:
        # Test with known test data
        result = await client.get_content("albums", "en-gb", "test-album")
        assert "title" in result
        assert "slug" in result
```

### Test Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/fdapi_mcp --cov-report=html

# Run specific test category
uv run pytest tests/unit/
uv run pytest tests/integration/ -m integration

# Run specific test file
uv run pytest tests/unit/test_client.py

# Run with verbose output
uv run pytest -v

# Run tests and open coverage report
uv run pytest --cov=src --cov-report=html && open htmlcov/index.html
```

### Test Data and Fixtures

- **Mock Responses**: Store in `tests/fixtures/api_responses/`
- **Test Data**: Generate realistic test data in `tests/fixtures/test_data.py`
- **Shared Fixtures**: Define in `tests/conftest.py`

## Documentation Requirements

### Required Documentation Updates

When making changes, update the following as applicable:

1. **README.md**: For new tools, configuration options, or setup changes
2. **TASKS.MD**: Mark completed tasks and update progress
3. **API Documentation**: For new endpoints or parameter changes
4. **Configuration Guide**: For new environment variables or settings
5. **Examples**: Add usage examples for new functionality

### Documentation Style

- Use clear, concise language
- Include code examples for complex concepts
- Link to relevant external documentation
- Keep examples up-to-date with current API

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure all relevant documentation is updated
2. **Test Coverage**: Verify 100% test coverage for new code
3. **Quality Checks**: Run all code quality tools
4. **Commit Messages**: Use conventional commit format
5. **PR Description**: Fill out the pull request template completely

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer(s)]
```

#### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Examples

```
feat(albums): implement album MCP tools

- Add fdapi_get_album tool
- Add fdapi_list_albums tool
- Include comprehensive unit tests
- Update documentation with examples

Closes #123
```

```
fix(client): handle timeout errors gracefully

- Add timeout error handling in HTTP client
- Improve error messages for network issues
- Add integration tests for timeout scenarios
```

### Pull Request Template

When creating a PR, include:

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Checklist

- [ ] Tests pass (`uv run pytest`)
- [ ] Code coverage maintained at 100%
- [ ] Code formatted (`uv run black src tests`)
- [ ] Linting passes (`uv run flake8 src tests`)
- [ ] Type checking passes (`uv run mypy src`)
- [ ] Documentation updated
- [ ] TASKS.MD updated (if applicable)

## Testing

Describe testing performed

## Related Issues

Closes #(issue number)
```

## Review Process

### Review Criteria

Pull requests are reviewed for:

1. **Code Quality**: Follows project standards and conventions
2. **Test Coverage**: Maintains 100% coverage requirement
3. **Documentation**: All changes are documented appropriately
4. **Functionality**: Code works as intended and handles edge cases
5. **Performance**: No significant performance regressions
6. **Security**: No security vulnerabilities introduced

### Review Timeline

- **Initial Review**: Within 2 business days
- **Follow-up Reviews**: Within 1 business day
- **Approval Requirements**: At least one maintainer approval
- **Merge Requirements**: All checks passing and conflicts resolved

### Feedback Process

1. **Address Feedback**: Make requested changes promptly
2. **Discussion**: Use PR comments for clarification
3. **Re-review**: Request re-review after addressing feedback
4. **Merge**: Maintainers will merge approved PRs

## Development Guidelines

### Performance Considerations

- Use async/await for all I/O operations
- Implement proper connection pooling
- Handle timeouts appropriately
- Consider memory usage with large responses

### Security Best Practices

- Validate all inputs
- Never commit secrets or API keys
- Use environment variables for configuration
- Sanitize error messages for external consumption

### Error Handling

- Use custom exception classes
- Provide meaningful error messages for LLMs
- Include suggestion text in error responses
- Log errors appropriately for debugging

### Configuration Management

- Use pydantic-settings for type-safe configuration
- Support environment variable overrides
- Validate configuration at startup
- Document all configuration options

## Getting Help

### Resources

- **Project Documentation**: [README.md](README.md)
- **Task Tracking**: [TASKS.MD](TASKS.MD)
- **Architecture**: [PLANNING.MD](PLANNING.MD)
- **Development Guidelines**: [.vscode/copilot-instructions.md](.vscode/copilot-instructions.md)

### Communication Channels

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions
- **Pull Requests**: Use PR comments for code-specific discussions

### Common Questions

**Q: Can I work on multiple content types at once?**
A: No, the project follows strict incremental development. Complete one endpoint type with 100% test coverage before moving to the next.

**Q: What if I find a bug in already implemented code?**
A: Create an issue and submit a fix PR. Bug fixes can be worked on in parallel with new endpoint development.

**Q: How do I know which task to work on next?**
A: Check [TASKS.MD](TASKS.MD) for the current phase and available tasks. Claim a task by commenting on it.

**Q: Can I suggest architectural changes?**
A: Yes, but create an issue first to discuss the change before implementing. Major architectural changes require broader discussion.

Thank you for contributing to the FDAPI MCP Server! Your contributions help make this project better for everyone.
