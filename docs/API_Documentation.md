# API Documentation - Book Insights API

Version: 1.0.0
Base URL (local): http://127.0.0.1:8000

## 1. Overview

Book Insights API is a Django REST Framework web service backed by SQLite. It imports the Goodreads `books.csv` dataset, exposes CRUD endpoints for book records, supports multi-field search, and provides a hybrid similar-books recommendation endpoint.

The SQLite database file is fixed to the project root as `books.db`, so local runs and deployment use the same database location instead of relying on the current working directory.

Interactive Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The OpenAPI schema is available at:

```text
http://127.0.0.1:8000/schema/
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
- `GET /docs`
- `GET /schema/`

Authentication error response:

```json
{
  "detail": "Invalid or missing API key"
}
```

Swagger UI authentication:

1. Open `/docs`.
2. Click `Authorize`.
3. Enter the API key in `ApiKeyAuth`.
4. Click `Authorize`.
5. Run `POST`, `PUT`, or `DELETE` requests from Swagger UI.

Default local API key:

```text
coursework-demo-key
```

## 3. Data Models

### 3.1 Book

The public book response follows the Goodreads dataset fields.

```json
{
  "id": 1,
  "bookID": 1,
  "title": "Harry Potter and the Half-Blood Prince (Harry Potter  #6)",
  "authors": "J.K. Rowling/Mary GrandPre",
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
- `authors`: required string, 1-255 characters.
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
  "authors": "J.K. Rowling/Mary GrandPre",
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
    "title_diversity_penalty": 0.0,
    "authors_diversity_penalty": 0.0375,
    "language_diversity_penalty": 0.025,
    "publisher_diversity_penalty": 0.0125,
    "diversity_penalty": 0.075
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
- A duplicate title compared with the target book receives a strong fixed penalty.
- For later recommendation positions, each previously selected book with overlapping authors deducts one quarter of the author score, capped at the full 15% author weight.
- The same quarter-step rule is also applied to repeated language code and repeated publisher, each capped at its own maximum rerank weight.
- Title embeddings are generated locally with `fastembed` using the `BAAI/bge-small-en-v1.5` ONNX model, so PyTorch is not required.

Penalty field meanings:

- `duplicate_penalty`: compares the candidate book with the selected target book.
- `title_diversity_penalty`: compares the candidate book with books already selected earlier in the recommendation list.
- `authors_diversity_penalty`: list-level author-repeat penalty.
- `language_diversity_penalty`: list-level language-repeat penalty.
- `publisher_diversity_penalty`: list-level publisher-repeat penalty.
- `diversity_penalty`: total list-level diversity penalty.

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

Success response `201`: created book JSON.

Common errors:

- `401`: invalid or missing API key.
- `409`: `bookID already exists`.
- `400`: validation error.

### 4.4 List and Search Books

- Method: `GET`
- Path: `/books`
- Auth required: No

Query parameters:

- `skip`: integer, optional, default `0`, minimum `0`.
- `limit`: integer, optional, default `20`, minimum `1`, maximum `100000`.
- `book_id`: integer, optional, minimum `1`. Matches the Goodreads `bookID` field only.
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

Common errors:

- `400`: invalid query parameter, for example `limit=0`.

### 4.5 Get Book by Database ID

- Method: `GET`
- Path: `/books/{book_id}`
- Auth required: No

Path parameters:

- `book_id`: internal database `id`, not necessarily the Goodreads `bookID`.

Common errors:

- `404`: book not found.

### 4.6 Get Similar Books

- Method: `GET`
- Path: `/books/{book_id}/recommendations`
- Auth required: No

Path parameters:

- `book_id`: internal database `id` for the selected book.

Query parameters:

- `limit`: integer, optional, default `5`, minimum `1`, maximum `20`.

Common errors:

- `404`: selected book does not exist.
- `400`: invalid `limit`.

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

Common errors:

- `400`: no fields provided or validation error.
- `401`: invalid or missing API key.
- `404`: book not found.
- `409`: updated `bookID` already exists.

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

Initialize database and embeddings:

```bash
python manage.py initbooks
```

Start server:

```bash
python manage.py runserver
```

Open the browser UI:

```text
http://127.0.0.1:8000/
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
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
