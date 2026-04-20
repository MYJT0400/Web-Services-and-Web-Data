# Book Insights API

Book Insights API is a **FastAPI + SQLite + SQLAlchemy** project for managing and exploring a Goodreads books dataset. It provides CRUD endpoints, searchable book records, a browser-based control page, Swagger documentation, API-key protected write operations, and a hybrid similar-books recommendation system.

## Project Scope

- Dataset: Goodreads `books.csv` from Kaggle.
- Core model: `Book`, aligned with the Goodreads CSV fields.
- Database: SQLite (`books.db`) with SQLAlchemy ORM.
- API style: RESTful JSON API.
- UI: local browser page at `/` for quick search, record actions, health check, and similar-books exploration.
- Documentation: Swagger UI at `/docs`, plus Markdown/PDF API documentation under `docs/`.
- Authentication: `X-API-Key` required for create, update, and delete.
- Recommendations: title embedding similarity plus metadata reranking and diversity penalties.

## Quick Start

1. Create and activate a virtual environment.

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. Open the browser UI:

   ```text
   http://127.0.0.1:8000/
   ```

5. Open Swagger UI:

   ```text
   http://127.0.0.1:8000/docs
   ```

On first run, if `.models/bge-micro-v2` is missing, the app prints a terminal message and downloads the embedding model automatically. The `.models/` directory is ignored by git so the model does not need to be submitted.

## API Key

Protected endpoints require this header:

```text
X-API-Key: coursework-demo-key
```

To set your own key in PowerShell:

```powershell
$env:API_KEY="your-secret-key"
```

## Implemented Endpoints

- `GET /` - browser control page.
- `GET /health` - service health check.
- `GET /books` - list books or search with query filters.
- `GET /books/{book_id}` - get one book by internal database ID.
- `GET /books/{book_id}/recommendations` - get similar books with score breakdown and generated reason text.
- `POST /books` - create a book, protected by API key.
- `PUT /books/{book_id}` - update a book, protected by API key.
- `DELETE /books/{book_id}` - delete a book, protected by API key.

## Book Fields

The API stores and returns these Goodreads-aligned fields:

- `id`: internal database ID.
- `bookID`: original Goodreads book ID, or auto-assigned for new records.
- `title`
- `authors`
- `average_rating`
- `isbn`
- `isbn13`
- `language_code`
- `num_pages`
- `ratings_count`
- `text_reviews_count`
- `publication_date`
- `publisher`

Create example:

```json
{
  "bookID": 100001,
  "title": "Clean Code",
  "authors": "Robert C. Martin",
  "average_rating": 4.4,
  "isbn": "0132350882",
  "isbn13": "9780132350884",
  "language_code": "eng",
  "num_pages": 464,
  "ratings_count": 1000,
  "text_reviews_count": 100,
  "publication_date": "8/1/2008",
  "publisher": "Prentice Hall"
}
```

## Search

`GET /books` supports these optional filters:

- `skip`
- `limit`
- `book_id`
- `title`
- `authors`
- `isbn`
- `isbn13`
- `language_code`
- `publisher`

Example:

```text
http://127.0.0.1:8000/books?title=Harry%20Potter&authors=Rowling&limit=5
```

## Similar-Books Recommendation

`GET /books/{book_id}/recommendations?limit=5` returns similar books with:

- `recommendation_score`
- `score_breakdown`
- `reason`

The recommendation algorithm uses:

- Title embedding similarity: 50%
- Authors match: 15%
- Language code match: 10%
- Publisher match: 5%
- Average rating: 10%
- Ratings count: 10%

It also applies penalties for duplicate titles and repeated metadata, so different editions of the same title or repeated author/publisher clusters do not dominate every result.

Embedding details:

- Model name: `SmartComponents/bge-micro-v2`
- Local model path: `.models/bge-micro-v2`
- Embeddings are computed from book titles.
- Title embeddings are stored in `books.db` on startup for faster recommendations.

## Data Import and Startup

- `books.csv` should be placed in the project root.
- `books.db` is created automatically if it does not exist.
- If the database is empty, `books.csv` is imported automatically.
- Missing embedding columns are added automatically for existing local databases.
- Missing title embeddings are precomputed and stored on startup.

## API Documentation

- Markdown: `docs/API_Documentation.md`
- PDF: `docs/API_Documentation.pdf`
- Swagger UI: `http://127.0.0.1:8000/docs`

If you update the API, regenerate or update the PDF documentation so it matches `docs/API_Documentation.md`.

## Run Tests

```bash
pytest -q tests -p no:cacheprovider
```

If Windows blocks pytest from creating files in the system temp directory, run tests with a project-local temp directory:

```powershell
$env:TMP="D:\desktop\web\cwk1\.pytest_tmp"
$env:TEMP="D:\desktop\web\cwk1\.pytest_tmp"
pytest -q tests -p no:cacheprovider
```

## Project Structure

```text
app/
  auth.py              API key authentication
  crud.py              database CRUD and search operations
  database.py          SQLAlchemy engine/session setup
  main.py              FastAPI app setup and route wiring
  models.py            SQLAlchemy Book model
  recommendations.py   embedding model loading, scoring, reranking, reasons
  schemas.py           Pydantic request/response schemas
  seed.py              database initialization, CSV import, embedding warmup
  ui.py                browser home page HTML/CSS/JavaScript
docs/
  API_Documentation.md
  API_Documentation.pdf
tests/
  test_api.py
books.csv
books.db
requirements.txt
```

## Notes for Coursework

- FastAPI is used because it provides a modern API-first framework, automatic OpenAPI/Swagger documentation, type-driven validation through Pydantic, and straightforward local demonstration.
- SQLite is used because it satisfies the SQL database requirement while keeping setup simple for local execution and marking.
- GenAI-assisted development should be declared in the technical report, including its use for planning, debugging, dataset import, documentation, and recommendation-system design.
