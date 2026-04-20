import csv
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from .database import Base, engine
from .models import Book
from .recommendations import warm_embeddings

CSV_PATH = Path(__file__).resolve().parents[1] / "books.csv"
REQUIRED_COLUMNS = {
    "id",
    "bookID",
    "title",
    "authors",
    "average_rating",
    "isbn",
    "isbn13",
    "language_code",
    "num_pages",
    "ratings_count",
    "text_reviews_count",
    "publication_date",
    "publisher",
}
EMBEDDING_COLUMNS = {
    "title_embedding": "ALTER TABLE books ADD COLUMN title_embedding BLOB",
    "embedding_model": "ALTER TABLE books ADD COLUMN embedding_model VARCHAR(80)",
}


def initialize_database() -> None:
    """Create/upgrade the books table, seed CSV data, and precompute embeddings."""
    _drop_incompatible_legacy_books_table()
    Base.metadata.create_all(bind=engine)
    _add_missing_embedding_columns()

    with Session(engine) as db:
        if db.query(Book).count() == 0 and CSV_PATH.exists():
            import_books_from_csv(db, CSV_PATH)
        warm_embeddings(db)


def import_books_from_csv(db: Session, csv_path: Path = CSV_PATH) -> int:
    imported = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file)
        header = [column.strip() for column in next(reader)]

        for row in reader:
            normalized = _normalize_row(header, row)
            book = Book(**normalized)
            db.add(book)
            imported += 1

    db.commit()
    return imported


def _drop_incompatible_legacy_books_table() -> None:
    inspector = inspect(engine)
    if "books" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("books")}
    if not REQUIRED_COLUMNS.issubset(existing_columns):
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE books"))


def _add_missing_embedding_columns() -> None:
    inspector = inspect(engine)
    if "books" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("books")}
    with engine.begin() as connection:
        for column_name, ddl in EMBEDDING_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))


def _normalize_row(header: list[str], row: list[str]) -> dict[str, object]:
    if len(row) > len(header):
        row = _repair_extra_author_commas(row)

    data = dict(zip(header, row, strict=True))
    return {
        "bookID": int(data["bookID"]),
        "title": data["title"].strip(),
        "authors": data["authors"].strip(),
        "average_rating": float(data["average_rating"]),
        "isbn": data["isbn"].strip(),
        "isbn13": str(data["isbn13"]).strip(),
        "language_code": data["language_code"].strip(),
        "num_pages": int(data["num_pages"]),
        "ratings_count": int(data["ratings_count"]),
        "text_reviews_count": int(data["text_reviews_count"]),
        "publication_date": data["publication_date"].strip(),
        "publisher": data["publisher"].strip(),
    }


def _repair_extra_author_commas(row: list[str]) -> list[str]:
    """Some Kaggle rows contain unescaped commas inside the authors field."""
    expected_tail_count = 9
    title_and_author_values = row[: len(row) - expected_tail_count]
    tail_values = row[len(row) - expected_tail_count :]
    repaired_authors = ",".join(title_and_author_values[2:])
    return [title_and_author_values[0], title_and_author_values[1], repaired_authors, *tail_values]
