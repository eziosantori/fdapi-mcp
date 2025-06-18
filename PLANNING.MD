# FDAPI MCP Server - Planning Document

## Vision

Create a comprehensive, production-ready MCP server that seamlessly bridges the gap between Large Language Models and the FDAPI service, enabling AI assistants to retrieve and interact with content through a standardized, well-tested interface.

## Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP Server    │    │   FDAPI Service │
│  (VS Code/      │◄──►│  (FastMCP 2.0)  │◄──►│   (REST API)    │
│   Claude)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

```
fdapi-mcp-server/
├── MCP Server Layer (FastMCP 2.0)
│   ├── Tool Registration & Routing
│   ├── Parameter Validation
│   └── Response Formatting
├── Business Logic Layer
│   ├── FDAPI Client
│   ├── Content Type Handlers
│   └── Error Management
├── Configuration Layer
│   ├── Environment Management
│   ├── Authentication Settings
│   └── API Base URL Configuration
└── Data Layer
│   ├── HTTP Client (httpx)
│   ├── Response Models (Pydantic)
│   └── Caching (future consideration)
```

## Technical Stack

### Core Technologies

| Component              | Technology        | Version | Rationale                                        |
| ---------------------- | ----------------- | ------- | ------------------------------------------------ |
| **Language**           | Python            | 3.10+   | Modern Python features, excellent MCP support    |
| **Dependency Manager** | uv                | Latest  | Fast, modern Python package management           |
| **MCP Framework**      | FastMCP           | 2.0     | Purpose-built for MCP servers, rapid development |
| **HTTP Client**        | httpx             | Latest  | Async support, modern HTTP client                |
| **Configuration**      | pydantic-settings | Latest  | Type-safe configuration management               |
| **Validation**         | pydantic          | Latest  | Data validation and serialization                |
| **Testing**            | pytest            | Latest  | Comprehensive testing framework                  |
| **Type Checking**      | mypy              | Latest  | Static type checking                             |
| **Code Formatting**    | black             | Latest  | Consistent code formatting                       |
| **Linting**            | flake8            | Latest  | Code quality enforcement                         |

### Development Tools

| Tool       | Purpose                         | Configuration  |
| ---------- | ------------------------------- | -------------- |
| **uv**     | Package management, virtual env | pyproject.toml |
| **pytest** | Testing framework               | pytest.ini     |
| **mypy**   | Type checking                   | mypy.ini       |
| **black**  | Code formatting                 | pyproject.toml |
| **flake8** | Linting                         | setup.cfg      |

## Project Structure Design

### Directory Layout

```
fdapi-mcp-server/
├── .vscode/
│   ├── copilot-instructions.md    # LLM development guidelines
│   ├── settings.json              # VS Code project settings
│   └── tasks.json                 # Build and run tasks
├── src/
│   └── fdapi_mcp/
│       ├── __init__.py
│       ├── server.py              # Main MCP server entry point
│       ├── client.py              # FDAPI HTTP client
│       ├── config.py              # Configuration management
│       ├── exceptions.py          # Custom exceptions
│       ├── models/                # Pydantic models
│       │   ├── __init__.py
│       │   ├── base.py            # Base models
│       │   ├── albums.py          # Album-specific models
│       │   ├── documents.py       # Document-specific models
│       │   └── ...                # Other content type models
│       └── tools/                 # MCP tools
│           ├── __init__.py
│           ├── base.py            # Base tool functionality
│           ├── albums.py          # Album tools
│           ├── documents.py       # Document tools
│           └── ...                # Other content type tools
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest configuration
│   ├── unit/                     # Unit tests
│   │   ├── test_client.py
│   │   ├── test_config.py
│   │   └── tools/
│   │       ├── test_albums.py
│   │       └── ...
│   ├── integration/              # Integration tests
│   │   ├── test_api_integration.py
│   │   └── test_mcp_integration.py
│   └── fixtures/                 # Test data
│       ├── api_responses/
│       └── test_data.py
├── docs/                         # Additional documentation
│   ├── api.md                    # API documentation
│   ├── configuration.md          # Configuration guide
│   └── deployment.md             # Deployment guide
├── scripts/                      # Utility scripts
│   ├── dev-server.py             # Development server
│   └── test-client.py            # Test MCP client
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── CHANGELOG.MD                  # Version history
├── CONTRIBUTING.MD               # Contribution guidelines
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Development containers
├── pyproject.toml               # Project configuration
├── README.MD                    # Main documentation
├── uv.lock                      # Dependency lock file
├── PR.MD                        # Project requirements
├── PLANNING.MD                  # This file
└── TASKS.MD                     # Task tracking
```

### Module Design Patterns

#### Configuration Pattern

```python
# config.py
from pydantic_settings import BaseSettings

class FDAPIConfig(BaseSettings):
    base_url: str = "https://api.example.com"
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

    class Config:
        env_prefix = "FDAPI_"
```

#### Client Pattern

```python
# client.py
class FDAPIClient:
    def __init__(self, config: FDAPIConfig):
        self.config = config
        self.client = httpx.AsyncClient()

    async def get_content(self, content_type: str, language: str, slug: str):
        # Implementation
```

#### Tool Pattern

```python
# tools/base.py
class BaseFDAPITool:
    def __init__(self, client: FDAPIClient):
        self.client = client

    async def execute(self, **kwargs):
        # Base implementation
```

## Content Type Analysis

### FDAPI Content Types (from OpenAPI spec)

Based on the API analysis, the following content types are available:

#### Core Content Types (Priority Order)

1. **Albums** - `/v1/content/{language}/albums/{slug}`
2. **Documents** - `/v1/content/{language}/documents/{slug}`
3. **Photos** - `/v1/content/{language}/photos/{slug}`
4. **Stories** - `/v1/content/{language}/stories/{slug}`
5. **Tags** - `/v1/content/{language}/tags/{slug}`
6. **Events** - `/v1/content/{language}/events/{slug}`
7. **Forms** - `/v1/content/{language}/forms/{slug}`
8. **Teams** - `/v1/content/{language}/teams/{slug}`

#### Video Content Types

- **Brightcove Videos** - `/v1/content/{language}/brightcovevideos/{slug}`
- **Diva Videos** - `/v1/content/{language}/divavideos/{slug}`
- **Hero Videos** - `/v1/content/{language}/hero-videos/{slug}`
- **JW Player Videos** - `/v1/content/{language}/jwplayervideos/{slug}`

#### Additional Content Types

- **Accordions** - `/v1/content/{language}/accordions/{slug}`
- **Advertisements** - `/v1/content/{language}/advertisements/{slug}`
- **Page Builder GAD Assets** - `/v1/content/{language}/page-builder-gad-assets/{slug}`
- **Page Builder Text Editors** - `/v1/content/{language}/page-builder-text-editors/{slug}`
- **Partners** - `/v1/content/{language}/partners/{slug}`
- **Promos** - `/v1/content/{language}/promos/{slug}`
- **Shop Products** - `/v1/content/{language}/shop-products/{slug}`
- **Visual Cards** - `/v1/content/{language}/visualcards/{slug}`
- **Visual Stories** - `/v1/content/{language}/visualstories/{slug}`

### Language Support

- **Primary:** en-gb (default)
- **Secondary:** fr-fr, es-es, ar-sa, de-de, nd-nd

## MCP Tools Design

### Tool Naming Convention

#### Detail Tools (Individual Items)

- `fdapi_get_album` - Get album by slug
- `fdapi_get_document` - Get document by slug
- `fdapi_get_photo` - Get photo by slug
- etc.

#### Collection Tools (Lists)

- `fdapi_list_albums` - List albums with pagination
- `fdapi_list_documents` - List documents with pagination
- `fdapi_list_photos` - List photos with pagination
- etc.

### Tool Parameter Design

#### Common Parameters

```json
{
  "language": {
    "type": "string",
    "enum": ["en-gb", "fr-fr", "es-es", "ar-sa", "de-de", "nd-nd"],
    "default": "en-gb",
    "description": "Content language"
  }
}
```

#### Detail Tool Parameters

```json
{
  "slug": {
    "type": "string",
    "required": true,
    "description": "Content identifier"
  }
}
```

#### Collection Tool Parameters

```json
{
  "page": {
    "type": "integer",
    "default": 1,
    "description": "Page number for pagination"
  },
  "limit": {
    "type": "integer",
    "default": 20,
    "description": "Number of items per page"
  }
}
```

## Error Handling Strategy

### Error Categories

1. **Configuration Errors**

   - Invalid base URL
   - Missing required configuration
   - Authentication failures

2. **Validation Errors**

   - Invalid language codes
   - Invalid slugs
   - Invalid parameters

3. **API Errors**

   - HTTP 404 (Not Found)
   - HTTP 500 (Server Error)
   - Network timeouts
   - Rate limiting

4. **MCP Errors**
   - Tool not found
   - Invalid tool parameters
   - Response formatting errors

### Error Response Format

```python
{
    "error": {
        "type": "ValidationError",
        "message": "Invalid language code 'xx-xx'",
        "code": "INVALID_LANGUAGE",
        "details": {
            "valid_languages": ["en-gb", "fr-fr", "es-es", "ar-sa", "de-de", "nd-nd"]
        }
    }
}
```

## Performance Considerations

### Response Optimization

- **Async Operations:** Use httpx async client for non-blocking requests
- **Connection Pooling:** Reuse HTTP connections
- **Request Timeouts:** Configurable timeouts to prevent hanging
- **Response Streaming:** Handle large responses efficiently

### Caching Strategy (Future)

- **In-Memory Cache:** For frequently accessed content
- **TTL Configuration:** Configurable cache expiration
- **Cache Invalidation:** Smart cache invalidation strategies

## Security Considerations

### API Security

- **Authentication:** Future-proof API key support
- **Input Validation:** Strict parameter validation
- **Rate Limiting:** Respect API rate limits
- **Error Information:** Limit sensitive information in error messages

### Configuration Security

- **Environment Variables:** Sensitive data in environment variables
- **Secret Management:** Secure handling of API keys
- **Configuration Validation:** Validate all configuration at startup

## Testing Strategy

### Test Categories

#### Unit Tests (per component)

- **Configuration:** Test all configuration scenarios
- **Client:** Test HTTP client functionality with mocks
- **Tools:** Test each MCP tool individually
- **Models:** Test data validation and serialization

#### Integration Tests (per endpoint)

- **API Integration:** Test actual API calls (with test data)
- **MCP Integration:** Test full MCP workflow
- **Error Scenarios:** Test error handling end-to-end

#### Coverage Requirements

- **Per Endpoint:** 100% coverage before moving to next endpoint
- **Overall:** Maintain 100% coverage throughout development
- **Critical Paths:** Extra attention to error handling and edge cases

### Test Data Strategy

- **Mock Responses:** Realistic API response fixtures
- **Test Environment:** Separate test configuration
- **Data Isolation:** Each test should be independent

## Development Workflow

### Incremental Development Process

#### Phase Setup

1. Create endpoint-specific models
2. Implement HTTP client methods
3. Create MCP tools
4. Write comprehensive tests
5. Validate 100% coverage
6. Update documentation

#### Quality Gates

- **Code Review:** All changes reviewed
- **Test Coverage:** 100% coverage requirement
- **Type Checking:** mypy passes without errors
- **Linting:** flake8 passes without warnings
- **Formatting:** black applied consistently

### Git Workflow

- **Branch Strategy:** Feature branches for each endpoint
- **Commit Messages:** Conventional commit format
- **PR Requirements:** Tests, documentation, coverage reports

## Deployment Strategy

### Development Deployment

- **Local Development:** uv-based virtual environment
- **Hot Reload:** Development server with auto-reload
- **Debug Mode:** Detailed logging and error messages

### Production Deployment (Future)

- **Docker Container:** Multi-stage build for optimization
- **Environment Configuration:** Production-ready configuration
- **Health Checks:** Endpoint health monitoring
- **Logging:** Structured logging for monitoring

## Monitoring and Observability

### Logging Strategy

- **Structured Logging:** JSON-formatted logs
- **Log Levels:** DEBUG, INFO, WARNING, ERROR
- **Request Tracking:** Track API requests and responses
- **Performance Metrics:** Response times and error rates

### Health Monitoring

- **Health Endpoint:** MCP server health check
- **API Connectivity:** FDAPI service health
- **Configuration Validation:** Runtime configuration checks

## Future Enhancements

### Potential Features

1. **Response Caching:** Improve performance with intelligent caching
2. **Webhook Support:** Real-time content updates
3. **Bulk Operations:** Batch content retrieval
4. **Advanced Filtering:** Enhanced query capabilities
5. **Content Indexing:** Search across all content types
6. **Metrics Dashboard:** Usage and performance monitoring

### Scalability Considerations

- **Horizontal Scaling:** Multiple server instances
- **Load Balancing:** Distribute requests across instances
- **Database Integration:** Optional local content caching
- **CDN Integration:** Content delivery optimization

## Risk Mitigation

### Technical Risks

- **API Changes:** Version pinning and change detection
- **Framework Updates:** Conservative update strategy
- **Performance Issues:** Load testing and optimization
- **Security Vulnerabilities:** Regular dependency updates

### Business Risks

- **Service Availability:** Graceful degradation strategies
- **API Limits:** Rate limiting and quota management
- **Data Consistency:** Validation and error recovery
- **User Experience:** Clear error messages and documentation
