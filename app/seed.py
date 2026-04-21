import csv
from pathlib import Path

from django.db import connection

from .database import PROJECT_ROOT
from .models import Book
from .recommendations import warm_embeddings

CSV_PATH = PROJECT_ROOT / "books.csv"
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
    _drop_incompatible_legacy_books_table()
    _create_books_table_if_missing()
    _add_missing_embedding_columns()

    if Book.objects.count() == 0 and CSV_PATH.exists():
        import_books_from_csv(CSV_PATH)
    warm_embeddings()


def import_books_from_csv(csv_path: Path = CSV_PATH) -> int:
    imported = 0
    pending = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file)
        header = [column.strip() for column in next(reader)]

        for row in reader:
            normalized = _normalize_row(header, row)
            pending.append(Book(**normalized))
            imported += 1

            if len(pending) >= 500:
                Book.objects.bulk_create(pending, batch_size=500)
                pending.clear()

    if pending:
        Book.objects.bulk_create(pending, batch_size=500)
    return imported


def _drop_incompatible_legacy_books_table() -> None:
    table_names = connection.introspection.table_names()
    if "books" not in table_names:
        return

    with connection.cursor() as cursor:
        table_description = connection.introspection.get_table_description(cursor, "books")
    existing_columns = {column.name for column in table_description}
    if not REQUIRED_COLUMNS.issubset(existing_columns):
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE books")


def _create_books_table_if_missing() -> None:
    if "books" in connection.introspection.table_names():
        return

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Book)


def _add_missing_embedding_columns() -> None:
    if "books" not in connection.introspection.table_names():
        return

    with connection.cursor() as cursor:
        table_description = connection.introspection.get_table_description(cursor, "books")
        existing_columns = {column.name for column in table_description}
        for column_name, ddl in EMBEDDING_COLUMNS.items():
            if column_name not in existing_columns:
                cursor.execute(ddl)


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
    expected_tail_count = 9
    title_and_author_values = row[: len(row) - expected_tail_count]
    tail_values = row[len(row) - expected_tail_count :]
    repaired_authors = ",".join(title_and_author_values[2:])
    return [title_and_author_values[0], title_and_author_values[1], repaired_authors, *tail_values]
