"""Test models module."""

import pytest
from datetime import datetime
from fdapi_mcp.models import (
    AlbumEntity,
    DocumentEntity,
    ArticleEntity,
    LiveEntity,
    ListResponse,
    ErrorResponse,
)


def test_album_entity():
    """Test Album entity model."""
    album = AlbumEntity(
        id="album-123",
        title="Test Album",
        slug="test-album",
        language="en-gb"
    )

    assert album.id == "album-123"
    assert album.title == "Test Album"
    assert album.slug == "test-album"
    assert album.language == "en-gb"
    assert album.description is None
    assert album.created_at is None
    assert album.updated_at is None
    assert album.metadata is None


def test_album_entity_with_optional_fields():
    """Test Album entity with optional fields."""
    created_at = datetime.now()
    updated_at = datetime.now()

    album = AlbumEntity(
        id="album-123",
        title="Test Album",
        slug="test-album",
        description="A test album",
        language="en-gb",
        created_at=created_at,
        updated_at=updated_at,
        metadata={"category": "sports"}
    )

    assert album.description == "A test album"
    assert album.created_at == created_at
    assert album.updated_at == updated_at
    assert album.metadata == {"category": "sports"}


def test_document_entity():
    """Test Document entity model."""
    document = DocumentEntity(
        id="doc-456",
        title="Test Document",
        slug="test-document",
        language="fr-fr"
    )

    assert document.id == "doc-456"
    assert document.title == "Test Document"
    assert document.slug == "test-document"
    assert document.language == "fr-fr"
    assert document.content is None
    assert document.summary is None


def test_article_entity():
    """Test Article entity model."""
    article = ArticleEntity(
        id="article-789",
        title="Test Article",
        slug="test-article",
        language="es-es",
        author="John Doe",
        tags=["sports", "football"]
    )

    assert article.id == "article-789"
    assert article.title == "Test Article"
    assert article.slug == "test-article"
    assert article.language == "es-es"
    assert article.author == "John Doe"
    assert article.tags == ["sports", "football"]


def test_live_entity():
    """Test Live entity model."""
    start_time = datetime.now()
    end_time = datetime.now()

    live = LiveEntity(
        id="live-101",
        title="Live Event",
        slug="live-event",
        language="de-de",
        status="active",
        start_time=start_time,
        end_time=end_time
    )

    assert live.id == "live-101"
    assert live.title == "Live Event"
    assert live.slug == "live-event"
    assert live.language == "de-de"
    assert live.status == "active"
    assert live.start_time == start_time
    assert live.end_time == end_time


def test_list_response():
    """Test List response model."""
    albums = [
        AlbumEntity(id="1", title="Album 1", slug="album-1", language="en-gb"),
        AlbumEntity(id="2", title="Album 2", slug="album-2", language="en-gb"),
    ]

    response = ListResponse(
        items=albums,
        total=2,
        page=1,
        per_page=20,
        has_next=False,
        has_prev=False
    )

    assert len(response.items) == 2
    assert response.total == 2
    assert response.page == 1
    assert response.per_page == 20
    assert response.has_next is False
    assert response.has_prev is False


def test_error_response():
    """Test Error response model."""
    error = ErrorResponse(
        error="ValidationError",
        message="Invalid input data",
        code="VAL_001",
        details={"field": "slug", "reason": "already_exists"}
    )

    assert error.error == "ValidationError"
    assert error.message == "Invalid input data"
    assert error.code == "VAL_001"
    assert error.details == {"field": "slug", "reason": "already_exists"}


def test_model_validation():
    """Test model validation."""
    # Test that required fields are enforced
    with pytest.raises(ValueError):
        AlbumEntity()  # Missing required fields

    # Test that extra fields are forbidden
    with pytest.raises(ValueError):
        AlbumEntity(
            id="album-123",
            title="Test Album",
            slug="test-album",
            language="en-gb",
            extra_field="not_allowed"  # This should be rejected
        )
