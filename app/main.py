from fastapi import Depends, FastAPI, Query, status
from sqlalchemy.orm import Session

from .auth import require_api_key
from .crud import (
    create_book as crud_create_book,
    delete_book as crud_delete_book,
    get_book_or_404,
    list_books as crud_list_books,
    update_book as crud_update_book,
)
from .database import Base, engine, get_db
from .schemas import BookCreate, BookOut, BookUpdate

app = FastAPI(
    title="Book Insights API",
    description="A CRUD API for managing books.",
    version="0.1.0",
)

# Create tables on app import so local runs and tests are consistent.
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    # Lightweight endpoint to verify service is alive.
    return {"status": "ok"}


@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book_endpoint(
    book: BookCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
) -> BookOut:
    # Route handles HTTP concerns; DB logic lives in crud.py.
    return crud_create_book(db, book)


@app.get("/books", response_model=list[BookOut])
def list_books_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[BookOut]:
    # Public read endpoint with pagination parameters.
    return crud_list_books(db, skip, limit)


@app.get("/books/{book_id}", response_model=BookOut)
def get_book_endpoint(book_id: int, db: Session = Depends(get_db)) -> BookOut:
    return get_book_or_404(db, book_id)


@app.put("/books/{book_id}", response_model=BookOut)
def update_book_endpoint(
    book_id: int,
    payload: BookUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
) -> BookOut:
    # Protected write endpoint.
    return crud_update_book(db, book_id, payload)


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_endpoint(
    book_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
) -> None:
    # Protected write endpoint.
    crud_delete_book(db, book_id)
    return None
