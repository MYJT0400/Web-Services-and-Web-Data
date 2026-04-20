from fastapi import Depends, FastAPI, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from .auth import require_api_key
from .crud import (
    create_book as crud_create_book,
    delete_book as crud_delete_book,
    get_book_or_404,
    list_books as crud_list_books,
    search_books as crud_search_books,
    update_book as crud_update_book,
)
from .database import get_db
from .recommendations import build_recommendation_reason, recommend_books
from .schemas import BookCreate, BookOut, BookRecommendationOut, BookUpdate
from .seed import initialize_database
from .ui import render_home_page

app = FastAPI(
    title="Book Insights API",
    description="A CRUD API for managing books.",
    version="0.1.0",
)

# Create the table and import books.csv for local runs.
initialize_database()


@app.get("/", response_class=HTMLResponse)
def home_page() -> str:
    return render_home_page()


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
    limit: int = Query(default=20, ge=1, le=100000),
    book_id: int | None = Query(default=None, ge=1),
    title: str | None = Query(default=None, min_length=1, max_length=255),
    authors: str | None = Query(default=None, min_length=1, max_length=255),
    isbn: str | None = Query(default=None, min_length=1, max_length=20),
    isbn13: str | None = Query(default=None, min_length=1, max_length=20),
    language_code: str | None = Query(default=None, min_length=1, max_length=20),
    publisher: str | None = Query(default=None, min_length=1, max_length=255),
    db: Session = Depends(get_db),
) -> list[BookOut]:
    # Public read endpoint with pagination + optional multi-field filtering.
    filters = [book_id, title, authors, isbn, isbn13, language_code, publisher]
    if any(value is not None for value in filters):
        return crud_search_books(
            db,
            skip,
            limit,
            book_id,
            title,
            authors,
            isbn,
            isbn13,
            language_code,
            publisher,
        )
    return crud_list_books(db, skip, limit)


@app.get("/books/{book_id}", response_model=BookOut)
def get_book_endpoint(book_id: int, db: Session = Depends(get_db)) -> BookOut:
    return get_book_or_404(db, book_id)


@app.get("/books/{book_id}/recommendations", response_model=list[BookRecommendationOut])
def get_book_recommendations_endpoint(
    book_id: int,
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list[BookRecommendationOut]:
    target_book = get_book_or_404(db, book_id)
    recommendations = recommend_books(db, target_book, limit=limit)
    return [
        BookRecommendationOut(
            **item["book"].__dict__,
            recommendation_score=item["recommendation_score"],
            score_breakdown={
                **item["score_breakdown"],
                "duplicate_penalty": item["duplicate_penalty"],
                **item["diversity_penalties"],
                "diversity_penalty": item["diversity_penalty"],
            },
            reason=build_recommendation_reason(target_book, item),
        )
        for item in recommendations
    ]


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
