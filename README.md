# Book Insights API

An API using **FastAPI + SQLite (SQL) + SQLAlchemy**.

## Project Scope (MVP)
- Theme: Book management API
- Core model: `Book`
- CRUD endpoints implemented
- SQL database integration
- JSON responses with standard HTTP status codes
- API key authentication for write operations

## Quick Start
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open docs:
   - Swagger UI: `http://127.0.0.1:8000/docs`
5. Use API key for protected endpoints:
   - Header: `X-API-Key: coursework-demo-key`
   - Or set your own key:
     ```bash
     # PowerShell
     $env:API_KEY="your-secret-key"
     ```

## Implemented Endpoints
- `GET /health`
- `POST /books`
- `GET /books`
- `GET /books/{book_id}`
- `PUT /books/{book_id}`
- `DELETE /books/{book_id}`

## API Documentation
- Markdown: `docs/API_Documentation.md`
- PDF: `docs/API_Documentation.pdf`

## One-Command Local Run
```bash
python -m uvicorn app.main:app --reload
```

## Run Tests
```bash
pytest -q tests -p no:cacheprovider
```

## Example Request (Create)
```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Software Engineering",
  "published_year": 2008,
  "summary": "A handbook of agile software craftsmanship."
}
```

## Notes
- Database file: `books.db` (created automatically on startup).
- Write endpoints (`POST/PUT/DELETE`) require `X-API-Key`.
- Full test cases are under `tests/test_api.py`.
