"""Initial schema — books and reviews tables.

Revision ID: 001_initial
Revises: None
Create Date: 2024-12-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the reading_status enum type
    reading_status_enum = sa.Enum(
        "want_to_read", "reading", "finished", name="reading_status"
    )

    # Create books table
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("isbn", sa.String(length=13), nullable=True),
        sa.Column("status", reading_status_enum, nullable=False, server_default="want_to_read"),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("isbn"),
    )

    # Create reviews table
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_name", sa.String(length=100), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    # Create index on book_id for faster review lookups
    op.create_index("ix_reviews_book_id", "reviews", ["book_id"])


def downgrade() -> None:
    op.drop_index("ix_reviews_book_id", table_name="reviews")
    op.drop_table("reviews")
    op.drop_table("books")

    # Drop the enum type
    sa.Enum(name="reading_status").drop(op.get_bind(), checkfirst=True)
