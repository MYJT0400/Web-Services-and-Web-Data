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

On first run, if `.models/fastembed-bge-small-en-v1.5` is missing, the app prints a terminal message and downloads the embedding model automatically. The `.models/` directory is ignored by git so the model does not need to be submitted.

For PythonAnywhere deployment, use the traditional WSGI entrypoint in [wsgi.py](/d:/desktop/web/cwk1/wsgi.py). That entrypoint disables automatic startup initialization so the website worker does not try to import CSV data or warm embeddings during every reload.

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

Penalty fields in `score_breakdown`:

- `duplicate_penalty`: penalty when the candidate has the same normalized title as the selected target book.
- `title_diversity_penalty`: penalty when the candidate repeats a normalized title that has already appeared earlier in the recommendation list.
- `authors_diversity_penalty`: progressive penalty for repeating authors that already appeared earlier in the recommendation list. Each repeated author occurrence deducts one quarter of the author score, capped at the full author weight.
- `language_diversity_penalty`: progressive penalty for repeating the same language code. Each repeated language occurrence deducts one quarter of the language score, capped at the full language weight.
- `publisher_diversity_penalty`: progressive penalty for repeating the same publisher. Each repeated publisher occurrence deducts one quarter of the publisher score, capped at the full publisher weight.
- `diversity_penalty`: total list-level diversity penalty, equal to the title, authors, language, and publisher diversity penalties added together.

The distinction is intentional: `duplicate_penalty` compares a candidate with the selected book, while diversity penalties compare a candidate with books that have already been selected for the current recommendation list.

Embedding details:

- Embedding library: `fastembed`
- Model name: `BAAI/bge-small-en-v1.5`
- Local model cache path: `.models/fastembed-bge-small-en-v1.5`
- Embeddings are computed from book titles using FastEmbed on ONNX Runtime, without PyTorch.
- If a complete FastEmbed snapshot is already present locally, the app registers a local FastEmbed model that points to `model_optimized.onnx` and loads that snapshot directly instead of downloading from Hugging Face.
- Title embeddings are stored in `books.db` on startup for faster recommendations.

## Data Import and Startup

- `books.csv` should be placed in the project root.
- `books.db` is stored in the project root and is created automatically if it does not exist.
- If the database is empty, `books.csv` is imported automatically.
- Missing embedding columns are added automatically for existing local databases.
- Missing title embeddings are precomputed and stored on startup.
- For traditional WSGI deployment, run `initialize_database()` once from a console before reloading the site:

  ```bash
  python -c "from app.seed import initialize_database; initialize_database(); print('ready')"
  ```

  The WSGI entrypoint then serves the existing database without repeating heavy initialization during worker import.

## PythonAnywhere WSGI Deployment

Install dependencies in your PythonAnywhere Bash console:

```bash
python -m pip install --user -r requirements.txt
```

Initialize the database once:

```bash
cd ~/Web-Services-and-Web-Data
python -c "from app.seed import initialize_database; initialize_database(); print('ready')"
```

Create or edit the WSGI file in PythonAnywhere so it points at your project `wsgi.py`:

```python
import sys
path = "/home/MX0000/Web-Services-and-Web-Data"
if path not in sys.path:
    sys.path.append(path)

from wsgi import application
```

In the PythonAnywhere Web tab:

- Choose a manual configuration with the same Python version that your installed packages use.
- Set the source code path to `/home/MX0000/Web-Services-and-Web-Data`.
- Set the WSGI configuration file to import `application` from the project `wsgi.py`.
- Reload the web app after saving changes.

After reloading, test:

```text
https://MX0000.pythonanywhere.com/health
https://MX0000.pythonanywhere.com/
https://MX0000.pythonanywhere.com/docs
```

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
