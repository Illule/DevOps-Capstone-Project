"""
SQLAlchemy ORM models for BookShelf.

Defines the `Book` and `Review` tables with their relationships.
These models are the source of truth for the database schema and
are used by Alembic to generate migrations.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReadingStatus(str, enum.Enum):
    """Reading status enum — used in both SQLAlchemy and Pydantic."""

    WANT_TO_READ = "want_to_read"
    READING = "reading"
    FINISHED = "finished"


class Book(Base):
    """A book in the user's personal collection."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(13), unique=True, nullable=True)
    status: Mapped[ReadingStatus] = mapped_column(
        Enum(
            ReadingStatus,
            name="reading_status",
            create_constraint=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=ReadingStatus.WANT_TO_READ,
    )
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship: one book has many reviews
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', status='{self.status.value}')>"


class Review(Base):
    """A review/rating for a specific book."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    reviewer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship: each review belongs to one book
    book: Mapped["Book"] = relationship("Book", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, book_id={self.book_id}, rating={self.rating})>"
