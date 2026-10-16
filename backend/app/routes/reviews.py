"""
Review endpoints.

Reviews are a sub-resource of books. Creating a review requires
a valid book_id. Deleting is done by review ID directly.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Review
from app.schemas import ReviewCreate, ReviewResponse

router = APIRouter(tags=["Reviews"])


@router.get("/books/{book_id}/reviews", response_model=list[ReviewResponse])
def list_reviews(book_id: int, db: Session = Depends(get_db)):
    """
    List all reviews for a specific book.

    Returns 404 if the book does not exist.
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    return db.query(Review).filter(Review.book_id == book_id).order_by(Review.created_at.desc()).all()


@router.post("/books/{book_id}/reviews", response_model=ReviewResponse, status_code=201)
def create_review(book_id: int, review_data: ReviewCreate, db: Session = Depends(get_db)):
    """
    Add a review to a book.

    Rating must be between 1 and 5 (enforced by Pydantic schema).
    Returns 404 if the book does not exist.
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    review = Review(book_id=book_id, **review_data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/reviews/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """
    Delete a review by its ID.

    Returns 204 on success. Returns 404 if the review does not exist.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail=f"Review with id {review_id} not found")

    db.delete(review)
    db.commit()
    return None
