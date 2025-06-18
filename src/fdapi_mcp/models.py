"""Pydantic models for FDAPI data structures."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict


class BaseEntity(BaseModel):
    """Base model for all FDAPI entities."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class AlbumEntity(BaseEntity):
    """Model for Album entity from FDAPI."""

    id: str = Field(..., description="Album unique identifier")
    title: str = Field(..., description="Album title")
    slug: str = Field(..., description="Album URL slug")
    description: Optional[str] = Field(None, description="Album description")
    language: str = Field(..., description="Album language code")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DocumentEntity(BaseEntity):
    """Model for Document entity from FDAPI."""

    id: str = Field(..., description="Document unique identifier")
    title: str = Field(..., description="Document title")
    slug: str = Field(..., description="Document URL slug")
    content: Optional[str] = Field(None, description="Document content")
    summary: Optional[str] = Field(None, description="Document summary")
    language: str = Field(..., description="Document language code")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ArticleEntity(BaseEntity):
    """Model for Article entity from FDAPI."""

    id: str = Field(..., description="Article unique identifier")
    title: str = Field(..., description="Article title")
    slug: str = Field(..., description="Article URL slug")
    content: Optional[str] = Field(None, description="Article content")
    summary: Optional[str] = Field(None, description="Article summary")
    author: Optional[str] = Field(None, description="Article author")
    language: str = Field(..., description="Article language code")
    tags: Optional[List[str]] = Field(None, description="Article tags")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LiveEntity(BaseEntity):
    """Model for Live entity from FDAPI."""

    id: str = Field(..., description="Live entity unique identifier")
    title: str = Field(..., description="Live entity title")
    slug: str = Field(..., description="Live entity URL slug")
    description: Optional[str] = Field(None, description="Live entity description")
    status: Optional[str] = Field(None, description="Live status")
    language: str = Field(..., description="Live entity language code")
    start_time: Optional[datetime] = Field(None, description="Live start time")
    end_time: Optional[datetime] = Field(None, description="Live end time")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ListResponse(BaseEntity):
    """Model for paginated list responses from FDAPI."""

    items: List[Union[AlbumEntity, DocumentEntity, ArticleEntity, LiveEntity]] = Field(
        ..., description="List of entities"
    )
    total: Optional[int] = Field(None, description="Total number of items")
    page: Optional[int] = Field(None, description="Current page number")
    per_page: Optional[int] = Field(None, description="Items per page")
    has_next: Optional[bool] = Field(None, description="Whether there are more pages")
    has_prev: Optional[bool] = Field(
        None, description="Whether there are previous pages")


class ErrorResponse(BaseEntity):
    """Model for error responses from FDAPI."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details")


# Type aliases for convenience
EntityType = Union[AlbumEntity, DocumentEntity, ArticleEntity, LiveEntity]
AnyEntity = Union[EntityType, ListResponse, ErrorResponse]
