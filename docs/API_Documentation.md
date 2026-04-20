# API Documentation - Book Insights API

Version: 0.3.0
Base URL (local): http://127.0.0.1:8000

## 1. Overview

Book Insights API is a FastAPI web service backed by a SQLite database. It imports the Goodreads `books.csv` dataset, exposes CRUD endpoints for book records, supports multi-field search, and provides a hybrid similar-books recommendation endpoint.

Interactive Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 2. Authentication

Write operations require an API key in the `X-API-Key` header.

- Header name: `X-API-Key`
- Default local key: `coursework-demo-key`
- Override with environment variable: `API_KEY`

Protected endpoints:

- `POST /books`
- `PUT /books/{book_id}`
- `DELETE /books/{book_id}`

Public endpoints:

- `GET /`
- `GET /health`
- `GET /books`
- `GET /books/{book_id}`
- `GET /books/{book_id}/recommendations`

Authentication error response:

```json
{
  "detail": "Invalid or missing API key"
}
```

## 3. Data Models

### 3.1 Book

The public book response follows the Goodreads dataset fields.

```json
{
  "id": 1,
  "bookID": 1,
  "title": "Harry Potter and the Half-Blood Prince (Harry Potter  #6)",
  "authors": "J.K. Rowling/Mary GrandPré",
  "average_rating": 4.57,
  "isbn": "0439785960",
  "isbn13": "9780439785969",
  "language_code": "eng",
  "num_pages": 652,
  "ratings_count": 2095690,
  "text_reviews_count": 27591,
  "publication_date": "9/16/2006",
  "publisher": "Scholastic Inc."
}
```

Field constraints:

- `bookID`: optional when creating, integer >= 1. If omitted, the API assigns the next available `bookID`.
- `title`: required string, 1-255 characters.
- `authors`: required string, 1-255 characters. Multiple authors may be separated with `/`, matching the Goodreads CSV format.
- `average_rating`: required number from 0 to 5.
- `isbn`: required string, 1-20 characters.
- `isbn13`: required string, 1-20 characters.
- `language_code`: required string, 1-20 characters.
- `num_pages`: required integer >= 0.
- `ratings_count`: required integer >= 0.
- `text_reviews_count`: required integer >= 0.
- `publication_date`: required string, 1-20 characters.
- `publisher`: required string, 1-255 characters.

### 3.2 Similar Book Recommendation

Recommendation responses include all book fields plus a final score, score breakdown, and generated text reason.

```json
{
  "id": 2,
  "bookID": 2,
  "title": "Harry Potter and the Order of the Phoenix (Harry Potter  #5)",
  "authors": "J.K. Rowling/Mary GrandPré",
  "average_rating": 4.49,
  "isbn": "0439358078",
  "isbn13": "9780439358071",
  "language_code": "eng",
  "num_pages": 870,
  "ratings_count": 2153167,
  "text_reviews_count": 29221,
  "publication_date": "9/1/2004",
  "publisher": "Scholastic Inc.",
  "recommendation_score": 0.624531,
  "score_breakdown": {
    "model_similarity": 0.423,
    "authors_match": 0.15,
    "language_match": 0.1,
    "publisher_match": 0.05,
    "average_rating_score": 0.0898,
    "ratings_count_score": 0.0976,
    "duplicate_penalty": 0.0,
    "diversity_penalty": 0.03
  },
  "reason": "This book stayed near the top after reranking: semantic similarity contributed 0.423, and the final score after penalties is 0.625."
}
```

Recommendation scoring uses title embeddings plus reranking:

- Title embedding model similarity: 50%
- Authors match: 15%
- Language code match: 10%
- Publisher match: 5%
- Average rating: 10%
- Ratings count: 10%
- Duplicate title and repeated metadata penalties are applied to improve variety.

## 4. Endpoints

### 4.1 Home Page

- Method: `GET`
- Path: `/`
- Auth required: No
- Response format: HTML

Returns the browser-based control page for searching, selecting, creating, updating, deleting, checking service health, and loading similar books.

### 4.2 Health Check

- Method: `GET`
- Path: `/health`
- Auth required: No

Success response `200`:

```json
{
  "status": "ok"
}
```

### 4.3 Create Book

- Method: `POST`
- Path: `/books`
- Auth required: Yes, `X-API-Key`

Request body:

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

Success response `201`:

```json
{
  "id": 11128,
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

Common errors:

- `401`: invalid or missing API key.
- `409`: `bookID already exists`.
- `422`: validation error, for example `average_rating` greater than 5.

### 4.4 List and Search Books

- Method: `GET`
- Path: `/books`
- Auth required: No

Query parameters:

- `skip`: integer, optional, default `0`, minimum `0`.
- `limit`: integer, optional, default `20`, minimum `1`, maximum `100000`.
- `book_id`: integer, optional, minimum `1`. Matches either internal `id` or Goodreads `bookID`.
- `title`: string, optional, partial match.
- `authors`: string, optional, partial match.
- `isbn`: string, optional, partial match.
- `isbn13`: string, optional, partial match.
- `language_code`: string, optional, partial match.
- `publisher`: string, optional, partial match.

Example request:

```text
GET /books?title=Harry%20Potter&authors=Rowling&limit=5
```

Success response `200`:

```json
[
  {
    "id": 1,
    "bookID": 1,
    "title": "Harry Potter and the Half-Blood Prince (Harry Potter  #6)",
    "authors": "J.K. Rowling/Mary GrandPré",
    "average_rating": 4.57,
    "isbn": "0439785960",
    "isbn13": "9780439785969",
    "language_code": "eng",
    "num_pages": 652,
    "ratings_count": 2095690,
    "text_reviews_count": 27591,
    "publication_date": "9/16/2006",
    "publisher": "Scholastic Inc."
  }
]
```

Common errors:

- `422`: invalid query parameter, for example `limit=0`.

### 4.5 Get Book by Database ID

- Method: `GET`
- Path: `/books/{book_id}`
- Auth required: No

Path parameters:

- `book_id`: internal database `id`, not necessarily the Goodreads `bookID`.

Success response `200`:

```json
{
  "id": 1,
  "bookID": 1,
  "title": "Harry Potter and the Half-Blood Prince (Harry Potter  #6)",
  "authors": "J.K. Rowling/Mary GrandPré",
  "average_rating": 4.57,
  "isbn": "0439785960",
  "isbn13": "9780439785969",
  "language_code": "eng",
  "num_pages": 652,
  "ratings_count": 2095690,
  "text_reviews_count": 27591,
  "publication_date": "9/16/2006",
  "publisher": "Scholastic Inc."
}
```

Error response `404`:

```json
{
  "detail": "Book not found"
}
```

### 4.6 Get Similar Books

- Method: `GET`
- Path: `/books/{book_id}/recommendations`
- Auth required: No

Path parameters:

- `book_id`: internal database `id` for the selected book.

Query parameters:

- `limit`: integer, optional, default `5`, minimum `1`, maximum `20`.

Example request:

```text
GET /books/1/recommendations?limit=3
```

Success response `200`:

```json
[
  {
    "id": 2,
    "bookID": 2,
    "title": "Harry Potter and the Order of the Phoenix (Harry Potter  #5)",
    "authors": "J.K. Rowling/Mary GrandPré",
    "average_rating": 4.49,
    "isbn": "0439358078",
    "isbn13": "9780439358071",
    "language_code": "eng",
    "num_pages": 870,
    "ratings_count": 2153167,
    "text_reviews_count": 29221,
    "publication_date": "9/1/2004",
    "publisher": "Scholastic Inc.",
    "recommendation_score": 0.624531,
    "score_breakdown": {
      "model_similarity": 0.423,
      "authors_match": 0.15,
      "language_match": 0.1,
      "publisher_match": 0.05,
      "average_rating_score": 0.0898,
      "ratings_count_score": 0.0976,
      "duplicate_penalty": 0.0,
      "diversity_penalty": 0.03
    },
    "reason": "Recommended because its title is semantically close to the selected book and the metadata supports the rerank score."
  }
]
```

Common errors:

- `404`: selected book does not exist.
- `422`: invalid `limit`.

### 4.7 Update Book

- Method: `PUT`
- Path: `/books/{book_id}`
- Auth required: Yes, `X-API-Key`

Path parameters:

- `book_id`: internal database `id`.

Request body:

All book fields are optional for update. At least one field must be supplied.

```json
{
  "publisher": "Pearson",
  "average_rating": 4.5
}
```

Success response `200`:

```json
{
  "id": 11128,
  "bookID": 100001,
  "title": "Clean Code",
  "authors": "Robert C. Martin",
  "average_rating": 4.5,
  "isbn": "0132350882",
  "isbn13": "9780132350884",
  "language_code": "eng",
  "num_pages": 464,
  "ratings_count": 1000,
  "text_reviews_count": 100,
  "publication_date": "8/1/2008",
  "publisher": "Pearson"
}
```

Common errors:

- `400`: no fields provided.
- `401`: invalid or missing API key.
- `404`: book not found.
- `409`: updated `bookID` already exists.
- `422`: validation error.

### 4.8 Delete Book

- Method: `DELETE`
- Path: `/books/{book_id}`
- Auth required: Yes, `X-API-Key`

Path parameters:

- `book_id`: internal database `id`.

Success response:

- `204 No Content`

Common errors:

- `401`: invalid or missing API key.
- `404`: book not found.

## 5. Local Run Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Start server:

```bash
python -m uvicorn app.main:app --reload
```

Open the browser UI:

```text
http://127.0.0.1:8000/
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Run tests:

```bash
pytest -q tests -p no:cacheprovider
```

## 6. cURL Examples

Create:

```bash
curl -X POST "http://127.0.0.1:8000/books" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: coursework-demo-key" \
  -d "{\"bookID\":100001,\"title\":\"Clean Code\",\"authors\":\"Robert C. Martin\",\"average_rating\":4.4,\"isbn\":\"0132350882\",\"isbn13\":\"9780132350884\",\"language_code\":\"eng\",\"num_pages\":464,\"ratings_count\":1000,\"text_reviews_count\":100,\"publication_date\":\"8/1/2008\",\"publisher\":\"Prentice Hall\"}"
```

Search:

```bash
curl "http://127.0.0.1:8000/books?title=Harry%20Potter&authors=Rowling&limit=5"
```

Get similar books:

```bash
curl "http://127.0.0.1:8000/books/1/recommendations?limit=3"
```

Delete:

```bash
curl -X DELETE "http://127.0.0.1:8000/books/11128" \
  -H "X-API-Key: coursework-demo-key"
```
