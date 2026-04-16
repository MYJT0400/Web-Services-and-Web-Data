from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import Book
from .schemas import BookCreate, BookUpdate


def create_book(db: Session, payload: BookCreate) -> Book:
    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def list_books(db: Session, skip: int, limit: int) -> list[Book]:
    return db.query(Book).offset(skip).limit(limit).all()


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

    for field, value in updates.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book_or_404(db, book_id)
    db.delete(book)
    db.commit()
