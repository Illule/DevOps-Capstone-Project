"""
Pydantic schemas for request validation and response serialization.

These schemas define the exact shape of data the API accepts and returns.
FastAPI uses them for:
  - Automatic request body validation (422 on invalid input)
  - Response serialization (only declared fields are returned)
  - OpenAPI/Swagger documentation generation
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import ReadingStatus


# ---------------------------------------------------------------------------
# Review Schemas
# ---------------------------------------------------------------------------


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""

    reviewer_name: str = Field(
        ..., min_length=1, max_length=100, examples=["Alice"]
    )
    rating: int = Field(..., ge=1, le=5, examples=[4])
    comment: str | None = Field(None, max_length=2000, examples=["Great read!"])


class ReviewResponse(BaseModel):
    """Schema for returning a review in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    reviewer_name: str
    rating: int
    comment: str | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Book Schemas
# ---------------------------------------------------------------------------


class BookCreate(BaseModel):
    """Schema for creating a new book."""

    title: str = Field(
        ..., min_length=1, max_length=255, examples=["The Pragmatic Programmer"]
    )
    author: str = Field(
        ..., min_length=1, max_length=255, examples=["David Thomas, Andrew Hunt"]
    )
    isbn: str | None = Field(
        None, max_length=13, examples=["9780135957059"]
    )
    status: ReadingStatus = Field(
        ReadingStatus.WANT_TO_READ, examples=["want_to_read"]
    )
    page_count: int | None = Field(None, ge=1, examples=[352])
    description: str | None = Field(
        None, max_length=5000, examples=["A classic book on software craftsmanship."]
    )


class BookUpdate(BaseModel):
    """
    Schema for updating a book.

    All fields are optional — only provided fields are updated.
    """

    title: str | None = Field(None, min_length=1, max_length=255)
    author: str | None = Field(None, min_length=1, max_length=255)
    isbn: str | None = Field(None, max_length=13)
    status: ReadingStatus | None = None
    page_count: int | None = Field(None, ge=1)
    description: str | None = Field(None, max_length=5000)


class BookResponse(BaseModel):
    """Schema for returning a book in API responses (without reviews)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    isbn: str | None
    status: ReadingStatus
    page_count: int | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class BookDetailResponse(BookResponse):
    """Schema for returning a single book with its reviews."""

    reviews: list[ReviewResponse] = []


# ---------------------------------------------------------------------------
# Statistics Schema
# ---------------------------------------------------------------------------


class StatsResponse(BaseModel):
    """Schema for the dashboard statistics endpoint."""

    total_books: int
    want_to_read: int
    reading: int
    finished: int
    total_reviews: int
    average_rating: float | None
