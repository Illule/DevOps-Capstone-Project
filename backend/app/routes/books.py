"""
Book CRUD endpoints.

Implements the full lifecycle for books: create, list (with filters),
get by ID (with reviews), update, and delete.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Book, ReadingStatus
from app.schemas import (
    BookCreate,
    BookDetailResponse,
    BookResponse,
    BookUpdate,
)

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookResponse])
def list_books(
    status: ReadingStatus | None = Query(None, description="Filter by reading status"),
    search: str | None = Query(None, description="Search by title or author"),
    db: Session = Depends(get_db),
):
    """
    List all books with optional filtering.

    - `status`: filter by reading status (want_to_read, reading, finished)
    - `search`: case-insensitive search in title and author fields
    """
    query = db.query(Book)

    if status:
        query = query.filter(Book.status == status)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            Book.title.ilike(search_pattern) | Book.author.ilike(search_pattern)
        )

    return query.order_by(Book.updated_at.desc()).all()


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """
    Get a single book by ID, including all its reviews.

    Returns 404 if the book does not exist.
    """
    book = (
        db.query(Book)
        .options(joinedload(Book.reviews))
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    return book


@router.post("", response_model=BookResponse, status_code=201)
def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    """
    Add a new book to the collection.

    Returns 201 with the created book. Returns 422 if validation fails
    (e.g., missing title, invalid status).
    """
    # Check for duplicate ISBN if provided
    if book_data.isbn:
        existing = db.query(Book).filter(Book.isbn == book_data.isbn).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"A book with ISBN {book_data.isbn} already exists",
            )

    book = Book(**book_data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_data: BookUpdate, db: Session = Depends(get_db)):
    """
    Update an existing book's details.

    Only the provided fields are updated (partial update).
    Returns 404 if the book does not exist.
    """
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    # Only update fields that were explicitly provided
    update_data = book_data.model_dump(exclude_unset=True)

    # Check for duplicate ISBN if being changed
    if "isbn" in update_data and update_data["isbn"]:
        existing = (
            db.query(Book)
            .filter(Book.isbn == update_data["isbn"], Book.id != book_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"A book with ISBN {update_data['isbn']} already exists",
            )

    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Delete a book and all its associated reviews (cascade).

    Returns 204 on success. Returns 404 if the book does not exist.
    """
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    db.delete(book)
    db.commit()
    return None
