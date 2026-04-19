from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import Book
from .schemas import BookCreate, BookUpdate


def create_book(db: Session, payload: BookCreate) -> Book:
    # Convert validated request payload into ORM model and persist it.
    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def list_books(db: Session, skip: int, limit: int) -> list[Book]:
    # Basic pagination for list endpoint.
    return db.query(Book).offset(skip).limit(limit).all()


def search_books(
    db: Session,
    skip: int,
    limit: int,
    book_id: int | None = None,
    title: str | None = None,
    author: str | None = None,
    genre: str | None = None,
    published_year: int | None = None,
) -> list[Book]:
    # Apply optional filters so users can query by multiple fields.
    query = db.query(Book)

    if book_id is not None:
        query = query.filter(Book.id == book_id)
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))
    if published_year is not None:
        query = query.filter(Book.published_year == published_year)

    return query.offset(skip).limit(limit).all()


def get_book_or_404(db: Session, book_id: int) -> Book:
    # Centralized lookup so all endpoints share the same 404 behavior.
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


def update_book(db: Session, book_id: int, payload: BookUpdate) -> Book:
    book = get_book_or_404(db, book_id)
    # Only update fields explicitly sent by the client.
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided")

    for field, value in updates.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    # Reuse lookup helper to return 404 for unknown IDs.
    book = get_book_or_404(db, book_id)
    db.delete(book)
    db.commit()
