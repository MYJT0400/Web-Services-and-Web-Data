def render_home_page() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Book Insights API</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fb;
      --bg-accent: #dde7f4;
      --panel: #ffffff;
      --panel-strong: #eef3f9;
      --text: #142033;
      --muted: #42526b;
      --line: #b7c4d6;
      --focus: #0b57d0;
      --primary: #0057b8;
      --primary-hover: #003f87;
      --secondary: #dce7f5;
      --secondary-text: #17365d;
      --danger: #a3261a;
      --danger-hover: #7e1c13;
      --shadow: 0 18px 40px rgba(20, 32, 51, 0.10);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      background:
        radial-gradient(circle at top right, rgba(0, 87, 184, 0.08), transparent 24rem),
        linear-gradient(180deg, var(--bg-accent) 0%, var(--bg) 22%, #eef2f8 100%);
    }

    a {
      color: inherit;
    }

    .shell {
      width: min(1380px, calc(100% - 28px));
      margin: 0 auto;
      padding: 24px 0 36px;
    }

    .hero {
      display: grid;
      grid-template-columns: 1.25fr 0.75fr;
      gap: 18px;
      margin-bottom: 18px;
    }

    .card,
    .panel {
      border: 1px solid var(--line);
      border-radius: 24px;
      background: rgba(255, 255, 255, 0.96);
      box-shadow: var(--shadow);
    }

    .card {
      padding: 28px;
      background:
        linear-gradient(135deg, rgba(0, 87, 184, 0.08), transparent 60%),
        var(--panel);
    }

    .eyebrow {
      margin: 0 0 10px;
      color: var(--primary);
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      max-width: 820px;
      font-size: clamp(2rem, 5vw, 4.2rem);
      line-height: 0.98;
      letter-spacing: -0.045em;
    }

    h2 {
      margin: 0 0 12px;
      font-size: 1.3rem;
      line-height: 1.2;
    }

    p {
      color: var(--muted);
      line-height: 1.65;
    }

    .panel {
      padding: 18px;
    }

    .quick-links {
      display: grid;
      gap: 12px;
      align-content: start;
    }

    button,
    .link-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 44px;
      border: 1px solid transparent;
      border-radius: 999px;
      padding: 10px 16px;
      color: #ffffff;
      background: var(--primary);
      font: 700 0.95rem/1 "Segoe UI", Arial, sans-serif;
      text-decoration: none;
      cursor: pointer;
      transition: background 160ms ease, border-color 160ms ease, transform 160ms ease;
    }

    button:hover,
    .link-button:hover {
      background: var(--primary-hover);
      transform: translateY(-1px);
    }

    button.secondary {
      color: var(--secondary-text);
      background: var(--secondary);
      border-color: #aebfd9;
    }

    button.secondary:hover {
      background: #cad9ed;
    }

    button.danger {
      background: var(--danger);
    }

    button.danger:hover {
      background: var(--danger-hover);
    }

    button:focus-visible,
    .link-button:focus-visible,
    input:focus-visible,
    summary:focus-visible {
      outline: 3px solid rgba(11, 87, 208, 0.28);
      outline-offset: 2px;
    }

    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(340px, 0.65fr);
      column-gap: 32px;
      row-gap: 22px;
      align-items: start;
    }

    .left-column,
    .right-column {
      display: grid;
      gap: 18px;
      min-width: 0;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }

    .form-grid.three {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    label {
      display: grid;
      gap: 5px;
      color: var(--muted);
      font-size: 0.82rem;
      font-weight: 700;
    }

    input {
      width: 100%;
      border: 1px solid #8da2bf;
      border-radius: 12px;
      padding: 11px 12px;
      color: var(--text);
      background: #ffffff;
      font: 0.94rem/1.2 "Segoe UI", Arial, sans-serif;
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 12px;
    }

    .status {
      min-height: 22px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.45;
    }

    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--panel);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 900px;
      font-size: 0.88rem;
      line-height: 1.45;
    }

    th,
    td {
      padding: 10px 12px;
      border-bottom: 1px solid #d5deea;
      text-align: left;
      vertical-align: top;
    }

    th {
      position: sticky;
      top: 0;
      background: var(--panel-strong);
      color: #14375f;
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    tr:last-child td {
      border-bottom: 0;
    }

    .details {
      white-space: pre-wrap;
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px;
      background: #f8fbff;
      font: 0.86rem/1.5 Consolas, monospace;
      overflow: auto;
    }

    .reason-box {
      margin-top: 12px;
      padding: 12px 14px;
      border: 1px solid #aebfd9;
      border-radius: 14px;
      background: #f5f9ff;
      color: var(--text);
      font-size: 0.92rem;
      line-height: 1.6;
    }

    details {
      margin-top: 8px;
    }

    summary {
      cursor: pointer;
      color: var(--primary);
      font-weight: 700;
    }

    .stack-note {
      margin: 0 0 10px;
      font-size: 0.92rem;
      color: var(--muted);
    }

    @media (max-width: 1080px) {
      .layout,
      .hero,
      .form-grid,
      .form-grid.three {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="card">
        <p class="eyebrow">Book Insights Workspace</p>
        <h1>Search, inspect, and compare similar books from your local database.</h1>
        <p>
          The left side keeps your results and record details visible. The right side keeps search
          and similar-book actions within reach so you can browse without losing context.
        </p>
      </div>
      <nav class="panel quick-links" aria-label="Quick links">
        <a class="link-button" href="/docs">Open Swagger UI</a>
        <button class="secondary" type="button" onclick="checkHealth()">Check Service Health</button>
        <div id="health-status" class="status"></div>
      </nav>
    </section>

    <section class="layout">
      <section class="left-column">
        <div class="panel">
          <h2>Selected Record</h2>
          <p class="stack-note">
            Keep one book selected here while you search and compare similar books on the right.
          </p>
          <div class="form-grid">
            <label>Database ID <input id="record-id" type="number" min="1" placeholder="Use returned id" /></label>
            <label>API Key <input id="api-key" placeholder="Enter API key for POST/PUT/DELETE" /></label>
          </div>
          <div class="actions">
            <button type="button" onclick="getBook()">Load Details</button>
            <button class="danger" type="button" onclick="deleteBook()">Delete</button>
          </div>
          <div id="action-status" class="status"></div>
          <pre id="details" class="details">Select a result below or enter a database id, then click Load Details.</pre>
        </div>

        <div class="panel">
          <h2>Results</h2>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>bookID</th>
                  <th>Title</th>
                  <th>Authors</th>
                  <th>Rating</th>
                  <th>ISBN</th>
                  <th>Language</th>
                  <th>Publisher</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody id="results"></tbody>
            </table>
          </div>
        </div>

        <div class="panel">
          <h2>Create or Update Book</h2>
          <div class="form-grid three">
            <label>bookID <input id="bookID" type="number" min="1" placeholder="Optional for create" /></label>
            <label>Title <input id="title" /></label>
            <label>Authors <input id="authors" /></label>
            <label>Average Rating <input id="average_rating" type="number" min="0" max="5" step="0.01" /></label>
            <label>ISBN <input id="isbn" /></label>
            <label>ISBN13 <input id="isbn13" /></label>
            <label>Language Code <input id="language_code" placeholder="eng" /></label>
            <label>Pages <input id="num_pages" type="number" min="0" /></label>
            <label>Ratings Count <input id="ratings_count" type="number" min="0" /></label>
            <label>Text Reviews <input id="text_reviews_count" type="number" min="0" /></label>
            <label>Publication Date <input id="publication_date" placeholder="9/16/2006" /></label>
            <label>Publisher <input id="publisher" /></label>
          </div>
          <div class="actions">
            <button type="button" onclick="createBook()">Create</button>
            <button class="secondary" type="button" onclick="updateBook()">Update Selected ID</button>
            <button class="secondary" type="button" onclick="fillExample()">Fill Example</button>
            <button class="secondary" type="button" onclick="clearForm()">Clear Form</button>
          </div>
          <div id="form-status" class="status"></div>
        </div>
      </section>

      <aside class="right-column">
        <div class="panel">
          <h2>Search</h2>
          <div class="form-grid">
            <label>Title <input id="search-title" placeholder="Harry Potter" /></label>
            <label>Authors <input id="search-authors" placeholder="Rowling" /></label>
            <label>ISBN <input id="search-isbn" placeholder="0439785960" /></label>
            <label>ISBN13 <input id="search-isbn13" placeholder="9780439785969" /></label>
            <label>Language <input id="search-language" placeholder="eng" /></label>
            <label>Publisher <input id="search-publisher" placeholder="Scholastic" /></label>
            <label>Book ID <input id="search-book-id" type="number" min="1" placeholder="1" /></label>
            <label>Limit <input id="search-limit" type="number" min="1" max="100000" value="10" /></label>
          </div>
          <div class="actions">
            <button type="button" onclick="searchBooks()">Search</button>
            <button class="secondary" type="button" onclick="loadLatest()">Load First 10</button>
          </div>
          <div id="search-status" class="status"></div>
        </div>

        <div class="panel">
          <h2>Similar Books</h2>
          <p class="stack-note">
            Recommendations use title embeddings, rerank signals, and diversity penalties.
            Click a recommendation to read a generated explanation.
          </p>
          <div class="actions" style="margin-top: 0;">
            <button type="button" onclick="loadRecommendations()">Find Similar Books</button>
          </div>
          <div id="recommendation-status" class="status"></div>
          <div id="recommendation-cards"></div>
        </div>
      </aside>
    </section>
  </main>

  <script>
    const fields = [
      "bookID", "title", "authors", "average_rating", "isbn", "isbn13",
      "language_code", "num_pages", "ratings_count", "text_reviews_count",
      "publication_date", "publisher"
    ];

    function value(id) {
      return document.getElementById(id).value.trim();
    }

    function setStatus(id, message, isError = false) {
      const element = document.getElementById(id);
      element.textContent = message;
      element.style.color = isError ? "var(--danger)" : "var(--muted)";
    }

    function buildQuery() {
      const params = new URLSearchParams();
      const mappings = {
        "search-title": "title",
        "search-authors": "authors",
        "search-isbn": "isbn",
        "search-isbn13": "isbn13",
        "search-language": "language_code",
        "search-publisher": "publisher",
        "search-book-id": "book_id",
        "search-limit": "limit"
      };

      Object.entries(mappings).forEach(([inputId, queryName]) => {
        const item = value(inputId);
        if (item) params.set(queryName, item);
      });

      if (!params.has("limit")) params.set("limit", "10");
      return params.toString();
    }

    async function request(path, options = {}) {
      const response = await fetch(path, options);
      const text = await response.text();
      const data = text ? JSON.parse(text) : null;
      if (!response.ok) {
        const detail = data && data.detail ? JSON.stringify(data.detail) : response.statusText;
        throw new Error(`${response.status} ${detail}`);
      }
      return data;
    }

    async function checkHealth() {
      try {
        setStatus("health-status", "Checking service health...");
        const data = await request("/health");
        const message = data && data.status === "ok"
          ? "Service is healthy."
          : `Unexpected response: ${JSON.stringify(data)}`;
        setStatus("health-status", message, data?.status !== "ok");
      } catch (error) {
        setStatus("health-status", error.message, true);
      }
    }

    async function searchBooks() {
      try {
        setStatus("search-status", "Searching...");
        const data = await request(`/books?${buildQuery()}`);
        renderResults(data);
        setStatus("search-status", `Loaded ${data.length} book(s).`);
      } catch (error) {
        setStatus("search-status", error.message, true);
      }
    }

    function loadLatest() {
      document.getElementById("search-limit").value = 10;
      ["search-title", "search-authors", "search-isbn", "search-isbn13",
       "search-language", "search-publisher", "search-book-id"].forEach(id => {
        document.getElementById(id).value = "";
      });
      searchBooks();
    }

    function renderResults(books) {
      const body = document.getElementById("results");
      body.innerHTML = books.map(book => `
        <tr>
          <td>${escapeHtml(book.id)}</td>
          <td>${escapeHtml(book.bookID)}</td>
          <td>${escapeHtml(book.title)}</td>
          <td>${escapeHtml(book.authors)}</td>
          <td>${escapeHtml(book.average_rating)}</td>
          <td>${escapeHtml(book.isbn)}</td>
          <td>${escapeHtml(book.language_code)}</td>
          <td>${escapeHtml(book.publisher)}</td>
          <td><button class="secondary" type="button" onclick="selectBook(${book.id})">Select</button></td>
        </tr>
      `).join("");
    }

    async function selectBook(id) {
      document.getElementById("record-id").value = id;
      await getBook();
    }

    async function getBook() {
      try {
        const id = value("record-id");
        if (!id) throw new Error("Enter a database ID first.");
        const book = await request(`/books/${id}`);
        document.getElementById("details").textContent = JSON.stringify(book, null, 2);
        fillForm(book);
        setStatus("action-status", "Book loaded.");
      } catch (error) {
        setStatus("action-status", error.message, true);
      }
    }

    async function loadRecommendations() {
      try {
        const id = value("record-id");
        if (!id) throw new Error("Select a book first.");
        setStatus("recommendation-status", "Loading similar books...");
        const data = await request(`/books/${id}/recommendations?limit=5`);
        renderRecommendations(data);
        setStatus("recommendation-status", `Loaded ${data.length} similar book(s).`);
      } catch (error) {
        setStatus("recommendation-status", error.message, true);
      }
    }

    function collectPayload(includeEmpty = false) {
      const payload = {};
      fields.forEach(field => {
        const item = value(field);
        if (!includeEmpty && item === "") return;
        if (["bookID", "num_pages", "ratings_count", "text_reviews_count"].includes(field)) {
          payload[field] = Number(item);
        } else if (field === "average_rating") {
          payload[field] = Number(item);
        } else {
          payload[field] = item;
        }
      });
      return payload;
    }

    function authHeaders() {
      return {
        "Content-Type": "application/json",
        "X-API-Key": value("api-key")
      };
    }

    async function createBook() {
      try {
        setStatus("form-status", "Creating...");
        const book = await request("/books", {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify(collectPayload(false))
        });
        document.getElementById("record-id").value = book.id;
        document.getElementById("details").textContent = JSON.stringify(book, null, 2);
        setStatus("form-status", `Created database ID ${book.id}.`);
        await searchBooks();
      } catch (error) {
        setStatus("form-status", error.message, true);
      }
    }

    async function updateBook() {
      try {
        const id = value("record-id");
        if (!id) throw new Error("Enter or select a database ID first.");
        const book = await request(`/books/${id}`, {
          method: "PUT",
          headers: authHeaders(),
          body: JSON.stringify(collectPayload(false))
        });
        document.getElementById("details").textContent = JSON.stringify(book, null, 2);
        setStatus("form-status", `Updated database ID ${book.id}.`);
        await searchBooks();
      } catch (error) {
        setStatus("form-status", error.message, true);
      }
    }

    async function deleteBook() {
      try {
        const id = value("record-id");
        if (!id) throw new Error("Enter or select a database ID first.");
        await request(`/books/${id}`, {
          method: "DELETE",
          headers: authHeaders()
        });
        document.getElementById("details").textContent = "Deleted.";
        setStatus("action-status", `Deleted database ID ${id}.`);
        document.getElementById("recommendation-cards").innerHTML = "";
        await searchBooks();
      } catch (error) {
        setStatus("action-status", error.message, true);
      }
    }

    function fillForm(book) {
      fields.forEach(field => {
        document.getElementById(field).value = book[field] ?? "";
      });
    }

    function renderRecommendations(books) {
      const root = document.getElementById("recommendation-cards");
      root.innerHTML = books.map((book, index) => `
        <div class="reason-box">
          <strong>${index + 1}. ${escapeHtml(book.title)}</strong><br />
          <span>${escapeHtml(book.authors)}</span><br />
          <span>Total score: ${escapeHtml(book.recommendation_score)}</span>
          <details>
            <summary>Why this book?</summary>
            <p>${escapeHtml(book.reason)}</p>
            <p>
              Model ${escapeHtml(book.score_breakdown.model_similarity)} |
              Author ${escapeHtml(book.score_breakdown.authors_match)} |
              Language ${escapeHtml(book.score_breakdown.language_match)} |
              Publisher ${escapeHtml(book.score_breakdown.publisher_match)} |
              Rating ${escapeHtml(book.score_breakdown.average_rating_score)} |
              Popularity ${escapeHtml(book.score_breakdown.ratings_count_score)}
            </p>
            <p>
              Duplicate penalty ${escapeHtml(book.score_breakdown.duplicate_penalty)} |
              Diversity penalty ${escapeHtml(book.score_breakdown.diversity_penalty)}
            </p>
          </details>
        </div>
      `).join("");
    }

    function fillExample() {
      fillForm({
        bookID: "",
        title: "Clean Code",
        authors: "Robert C. Martin",
        average_rating: 4.4,
        isbn: "0132350882",
        isbn13: "9780132350884",
        language_code: "eng",
        num_pages: 464,
        ratings_count: 1000,
        text_reviews_count: 100,
        publication_date: "8/1/2008",
        publisher: "Prentice Hall"
      });
    }

    function clearForm() {
      fields.forEach(field => {
        document.getElementById(field).value = "";
      });
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    loadLatest();
    checkHealth();
  </script>
</body>
</html>
"""
