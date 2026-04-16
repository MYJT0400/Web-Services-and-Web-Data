# API Documentation - Book Insights API

Version: 0.2.0
Base URL (local): http://127.0.0.1:8000

## 1. Authentication

This API uses API key authentication for write operations.

- Header name: X-API-Key
- Default local key: coursework-demo-key
- Set your own key with environment variable API_KEY

Protected endpoints:
- POST /books
- PUT /books/{book_id}
- DELETE /books/{book_id}

Public endpoints:
- GET /health
- GET /books
- GET /books/{book_id}

### Authentication Error Example
Request without or with wrong X-API-Key on a protected endpoint:

Response (401):
```json
{
  "detail": "Invalid or missing API key"
}
```

## 2. Data Model

Book object:

```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Software Engineering",
  "published_year": 2008,
  "summary": "A handbook."
}
```

Field constraints:
- title: 1-200 chars
- author: 1-120 chars
- genre: 1-80 chars
- published_year: 0-2100
- summary: 0-2000 chars

## 3. Endpoints

### 3.1 Health Check
- Method: GET
- Path: /health
- Auth required: No
- Query params: None

Success response (200):
```json
{
  "status": "ok"
}
```

### 3.2 Create Book
- Method: POST
- Path: /books
- Auth required: Yes (X-API-Key)

Request body:
```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Software Engineering",
  "published_year": 2008,
  "summary": "A handbook."
}
```

Success response (201):
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Software Engineering",
  "published_year": 2008,
  "summary": "A handbook."
}
```

Common errors:
- 401: Invalid or missing API key
- 422: Validation error (e.g., published_year > 2100)

### 3.3 List Books
- Method: GET
- Path: /books
- Auth required: No

Query parameters:
- skip (int, optional, default=0, min=0)
- limit (int, optional, default=20, min=1, max=100)

Success response (200):
```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "genre": "Software Engineering",
    "published_year": 2008,
    "summary": "A handbook."
  }
]
```

Common errors:
- 422: Invalid query parameters

### 3.4 Get Book by ID
- Method: GET
- Path: /books/{book_id}
- Auth required: No

Path parameters:
- book_id (int)

Success response (200):
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Software Engineering",
  "published_year": 2008,
  "summary": "A handbook."
}
```

Error response (404):
```json
{
  "detail": "Book not found"
}
```

### 3.5 Update Book
- Method: PUT
- Path: /books/{book_id}
- Auth required: Yes (X-API-Key)

Request body (partial update fields allowed):
```json
{
  "genre": "Programming"
}
```

Success response (200):
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Programming",
  "published_year": 2008,
  "summary": "A handbook."
}
```

Common errors:
- 400: No fields provided
- 401: Invalid or missing API key
- 404: Book not found
- 422: Validation error

### 3.6 Delete Book
- Method: DELETE
- Path: /books/{book_id}
- Auth required: Yes (X-API-Key)

Success response (204): no content

Common errors:
- 401: Invalid or missing API key
- 404: Book not found

## 4. Run and Demo Commands

Start server:
```bash
uvicorn app.main:app --reload
```

Open interactive docs:
- http://127.0.0.1:8000/docs

## 5. cURL Demo

Create:
```bash
curl -X POST "http://127.0.0.1:8000/books" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: coursework-demo-key" \
  -d '{"title":"Clean Code","author":"Robert C. Martin","genre":"Software Engineering","published_year":2008,"summary":"A handbook."}'
```

List:
```bash
curl "http://127.0.0.1:8000/books?skip=0&limit=10"
```
