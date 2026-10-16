"""
Dashboard statistics endpoint.

Provides aggregate reading metrics for the frontend dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, ReadingStatus, Review
from app.schemas import StatsResponse

router = APIRouter(tags=["Statistics"])


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Get reading dashboard statistics.

    Returns counts of books by status, total reviews,
    and the average review rating across all books.
    """
    total_books = db.query(func.count(Book.id)).scalar() or 0

    # Count books by status
    status_counts = (
        db.query(Book.status, func.count(Book.id))
        .group_by(Book.status)
        .all()
    )
    status_map = {status: count for status, count in status_counts}

    total_reviews = db.query(func.count(Review.id)).scalar() or 0

    # Average rating — returns None if no reviews exist
    avg_rating_raw = db.query(func.avg(Review.rating)).scalar()
    average_rating = round(float(avg_rating_raw), 2) if avg_rating_raw else None

    return StatsResponse(
        total_books=total_books,
        want_to_read=status_map.get(ReadingStatus.WANT_TO_READ, 0),
        reading=status_map.get(ReadingStatus.READING, 0),
        finished=status_map.get(ReadingStatus.FINISHED, 0),
        total_reviews=total_reviews,
        average_rating=average_rating,
    )
