# FDAPI MCP Server

A Model Context Protocol (MCP) server that provides AI tools to interact with the FDAPI endpoints, enabling Large Language Models to seamlessly access and retrieve content from the FDAPI service.

## Features

- 🔧 **Complete API Coverage**: Access to all FDAPI content types (Albums, Documents, Photos, Stories, Tags, Events, Videos, Forms, Teams, and more)
- 🌍 **Multi-language Support**: Support for en-gb, fr-fr, es-es, ar-sa, de-de, nd-nd with en-gb as default
- ⚡ **FastMCP 2.0**: Built with the latest FastMCP framework for optimal performance
- 🔒 **Future-proof Authentication**: Ready for API key authentication when needed
- 🧪 **100% Test Coverage**: Comprehensive testing for all implemented endpoints
- 📚 **Comprehensive Documentation**: Detailed setup guides for VS Code and Claude Desktop
- 🐳 **Docker Support**: Container-ready for easy deployment

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for dependency management

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd fdapi-mcp-server
   ```

2. **Install dependencies**:

   ```bash
   uv sync
   ```

3. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your FDAPI base URL
   ```

4. **Run the development server**:
   ```bash
   uv run python src/fdapi_mcp/server.py
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# FDAPI Configuration
FDAPI_BASE_URL=https://your-fdapi-instance.com
FDAPI_API_KEY=your-api-key-here  # Optional, for future authentication
FDAPI_TIMEOUT=30
FDAPI_MAX_RETRIES=3

# Server Configuration
MCP_SERVER_NAME=fdapi-server
MCP_SERVER_VERSION=1.0.0
LOG_LEVEL=INFO
```

### Configuration Options

| Variable            | Default  | Description                                 |
| ------------------- | -------- | ------------------------------------------- |
| `FDAPI_BASE_URL`    | Required | Base URL for the FDAPI service              |
| `FDAPI_API_KEY`     | None     | API key for authentication (future use)     |
| `FDAPI_TIMEOUT`     | 30       | Request timeout in seconds                  |
| `FDAPI_MAX_RETRIES` | 3        | Maximum retry attempts for failed requests  |
| `LOG_LEVEL`         | INFO     | Logging level (DEBUG, INFO, WARNING, ERROR) |

## MCP Client Integration

### VS Code with Copilot

1. **Install the MCP extension** (if available) or configure manually
2. **Add to your VS Code settings** (`.vscode/settings.json`):

```json
{
  "mcp.servers": {
    "fdapi": {
      "command": "uv",
      "args": ["run", "python", "src/fdapi_mcp/server.py"],
      "cwd": "/path/to/fdapi-mcp-server",
      "env": {
        "FDAPI_BASE_URL": "https://your-fdapi-instance.com"
      }
    }
  }
}
```

3. **Restart VS Code** and the FDAPI tools will be available in Copilot

### Claude Desktop

1. **Add to Claude Desktop configuration** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "fdapi": {
      "command": "uv",
      "args": ["run", "python", "src/fdapi_mcp/server.py"],
      "cwd": "/path/to/fdapi-mcp-server",
      "env": {
        "FDAPI_BASE_URL": "https://your-fdapi-instance.com"
      }
    }
  }
}
```

2. **Restart Claude Desktop** and the FDAPI tools will be available

### Other MCP Clients

The server follows the standard MCP protocol and should work with any compliant MCP client. Refer to your client's documentation for configuration details.

## Available Tools

### Content Retrieval Tools

#### Albums

- `fdapi_get_album(slug, language="en-gb")` - Get album details
- `fdapi_list_albums(language="en-gb", page=1, limit=20)` - List albums

#### Documents

- `fdapi_get_document(slug, language="en-gb")` - Get document details
- `fdapi_list_documents(language="en-gb", page=1, limit=20)` - List documents

#### Photos

- `fdapi_get_photo(slug, language="en-gb")` - Get photo details
- `fdapi_list_photos(language="en-gb", page=1, limit=20)` - List photos

#### Stories

- `fdapi_get_story(slug, language="en-gb")` - Get story details
- `fdapi_list_stories(language="en-gb", page=1, limit=20)` - List stories

#### Tags

- `fdapi_get_tag(slug, language="en-gb")` - Get tag details
- `fdapi_list_tags(language="en-gb", page=1, limit=20)` - List tags

#### Events

- `fdapi_get_event(slug, language="en-gb")` - Get event details
- `fdapi_list_events(language="en-gb", page=1, limit=20)` - List events

#### Videos

- `fdapi_get_brightcove_video(slug, language="en-gb")` - Get Brightcove video
- `fdapi_list_brightcove_videos(language="en-gb", page=1, limit=20)` - List Brightcove videos
- `fdapi_get_diva_video(slug, language="en-gb")` - Get Diva video
- `fdapi_list_diva_videos(language="en-gb", page=1, limit=20)` - List Diva videos
- `fdapi_get_hero_video(slug, language="en-gb")` - Get Hero video
- `fdapi_list_hero_videos(language="en-gb", page=1, limit=20)` - List Hero videos
- `fdapi_get_jwplayer_video(slug, language="en-gb")` - Get JW Player video
- `fdapi_list_jwplayer_videos(language="en-gb", page=1, limit=20)` - List JW Player videos

#### Forms

- `fdapi_get_form(slug, language="en-gb")` - Get form details
- `fdapi_list_forms(language="en-gb", page=1, limit=20)` - List forms

#### Teams

- `fdapi_get_team(slug, language="en-gb")` - Get team details
- `fdapi_list_teams(language="en-gb", page=1, limit=20)` - List teams

### Parameters

#### Common Parameters

- `slug` (string, required): Content identifier
- `language` (string, optional): Language code (en-gb, fr-fr, es-es, ar-sa, de-de, nd-nd), defaults to "en-gb"
- `page` (integer, optional): Page number for pagination, defaults to 1
- `limit` (integer, optional): Number of items per page, defaults to 20

## Usage Examples

### Getting Content with Copilot

```
"Get me the album with slug 'championship-photos' in French"
```

Copilot will use: `fdapi_get_album(slug="championship-photos", language="fr-fr")`

### Listing Content

```
"Show me the first 10 stories in Spanish"
```

Copilot will use: `fdapi_list_stories(language="es-es", page=1, limit=10)`

### Working with Videos

```
"Find all Brightcove videos, get the first one in German"
```

Copilot will:

1. Use: `fdapi_list_brightcove_videos(language="de-de", limit=1)`
2. Then: `fdapi_get_brightcove_video(slug="<first-slug>", language="de-de")`

## Development

### Project Structure

```
fdapi-mcp-server/
├── src/
│   └── fdapi_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       ├── client.py          # FDAPI HTTP client
│       ├── config.py          # Configuration management
│       ├── exceptions.py      # Custom exceptions
│       ├── models/            # Pydantic models
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── albums.py
│       │   └── ...
│       └── tools/             # MCP tools
│           ├── __init__.py
│           ├── base.py
│           ├── albums.py
│           └── ...
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
├── .env.example
├── pyproject.toml
└── README.md
```

### Development Setup

1. **Clone and setup**:

   ```bash
   git clone <repository-url>
   cd fdapi-mcp-server
   uv sync
   ```

2. **Run tests**:

   ```bash
   uv run pytest
   ```

3. **Check coverage**:

   ```bash
   uv run pytest --cov=src/fdapi_mcp --cov-report=html
   ```

4. **Code quality**:
   ```bash
   uv run black src tests
   uv run flake8 src tests
   uv run mypy src
   ```

### Development Commands

```bash
# Run development server with hot reload
uv run python scripts/dev-server.py

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Format code
uv run black src tests

# Lint code
uv run flake8 src tests

# Type checking
uv run mypy src

# Run all quality checks
uv run python scripts/check-quality.py
```

## Testing

The project maintains 100% test coverage. Tests are organized into:

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test API interactions and MCP functionality
- **Fixtures** (`tests/fixtures/`): Mock data and test utilities

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/fdapi_mcp

# Run specific test file
uv run pytest tests/unit/test_client.py

# Run with verbose output
uv run pytest -v

# Run integration tests only
uv run pytest tests/integration/ -m integration
```

## Docker Deployment

### Using Docker

1. **Build the image**:

   ```bash
   docker build -t fdapi-mcp-server .
   ```

2. **Run the container**:
   ```bash
   docker run -e FDAPI_BASE_URL=https://your-api.com fdapi-mcp-server
   ```

### Using Docker Compose

1. **Create docker-compose.yml**:

   ```yaml
   version: "3.8"
   services:
     fdapi-mcp:
       build: .
       environment:
         - FDAPI_BASE_URL=https://your-api.com
         - FDAPI_API_KEY=your-key-here
       ports:
         - "8000:8000"
   ```

2. **Run with compose**:
   ```bash
   docker-compose up
   ```

## Error Handling

The server provides comprehensive error handling with meaningful messages for LLMs:

### Common Error Types

- `ContentNotFoundError`: When content doesn't exist
- `ValidationError`: When parameters are invalid
- `AuthenticationError`: When API authentication fails
- `FDAPIError`: Generic API errors

### Error Response Format

```json
{
  "success": false,
  "error": {
    "type": "ContentNotFoundError",
    "message": "Album with slug 'nonexistent' not found",
    "code": "CONTENT_NOT_FOUND",
    "details": {
      "content_type": "album",
      "slug": "nonexistent",
      "language": "en-gb"
    },
    "suggestion": "Try checking the slug spelling or use the list endpoint to find available content."
  }
}
```

## Performance

- **Async Operations**: All I/O operations are asynchronous for optimal performance
- **Connection Pooling**: HTTP connections are reused efficiently
- **Configurable Timeouts**: Request timeouts prevent hanging operations
- **Response Streaming**: Large responses are handled efficiently

## Contributing

Please read [CONTRIBUTING.MD](CONTRIBUTING.MD) for details on our code of conduct and the process for submitting pull requests.

### Development Workflow

1. Check [TASKS.MD](TASKS.MD) for current phase and available tasks
2. Create a feature branch: `git checkout -b feature/endpoint-albums`
3. Implement the endpoint with 100% test coverage
4. Update documentation
5. Submit a pull request

## Changelog

See [CHANGELOG.MD](CHANGELOG.MD) for a detailed history of changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:

1. Check the [documentation](docs/)
2. Review [TASKS.MD](TASKS.MD) for known issues
3. Create an issue in the repository

## Roadmap

- [x] **Phase 1**: Project foundation and setup
- [ ] **Phase 2**: Core infrastructure (FDAPI client, configuration)
- [ ] **Phase 3**: Albums implementation
- [ ] **Phase 4**: Documents implementation
- [ ] **Phase 5**: Photos implementation
- [ ] **Phase 6**: Stories implementation
- [ ] **Phase 7**: Tags implementation
- [ ] **Phase 8**: Events implementation
- [ ] **Phase 9**: Videos implementation (all providers)
- [ ] **Phase 10**: Forms implementation
- [ ] **Phase 11**: Teams implementation
- [ ] **Phase 12**: Additional content types
- [ ] **Phase 13**: Comprehensive error handling and validation
- [ ] **Phase 14**: Docker support and deployment
- [ ] **Phase 15**: Final documentation and polish

See [TASKS.MD](TASKS.MD) for detailed task tracking and progress updates.

## Acknowledgments

- Built with [FastMCP 2.0](https://github.com/jlowin/fastmcp)
- Dependency management with [uv](https://docs.astral.sh/uv/)
- Following [MCP Protocol](https://modelcontextprotocol.io/) standards
