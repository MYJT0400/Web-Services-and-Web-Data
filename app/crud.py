from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Book
from .schemas import BookCreate, BookUpdate


def _next_book_id(db: Session) -> int:
    return (db.query(func.max(Book.bookID)).scalar() or 0) + 1


def create_book(db: Session, payload: BookCreate) -> Book:
    data = payload.model_dump()
    if data["bookID"] is None:
        data["bookID"] = _next_book_id(db)

    existing = db.query(Book).filter(Book.bookID == data["bookID"]).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="bookID already exists")

    book = Book(**data)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def list_books(db: Session, skip: int, limit: int) -> list[Book]:
    return db.query(Book).offset(skip).limit(limit).all()


def search_books(
    db: Session,
    skip: int,
    limit: int,
    book_id: int | None = None,
    title: str | None = None,
    authors: str | None = None,
    isbn: str | None = None,
    isbn13: str | None = None,
    language_code: str | None = None,
    publisher: str | None = None,
) -> list[Book]:
    query = db.query(Book)

    if book_id is not None:
        query = query.filter(Book.bookID == book_id)
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if authors:
        query = query.filter(Book.authors.ilike(f"%{authors}%"))
    if isbn:
        query = query.filter(Book.isbn.ilike(f"%{isbn}%"))
    if isbn13:
        query = query.filter(Book.isbn13.ilike(f"%{isbn13}%"))
    if language_code:
        query = query.filter(Book.language_code.ilike(f"%{language_code}%"))
    if publisher:
        query = query.filter(Book.publisher.ilike(f"%{publisher}%"))

    return query.offset(skip).limit(limit).all()


def get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


def update_book(db: Session, book_id: int, payload: BookUpdate) -> Book:
    book = get_book_or_404(db, book_id)
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided")

    new_book_id = updates.get("bookID")
    if new_book_id is not None and new_book_id != book.bookID:
        existing = db.query(Book).filter(Book.bookID == new_book_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="bookID already exists")

    for field, value in updates.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book_or_404(db, book_id)
    db.delete(book)
    db.commit()
