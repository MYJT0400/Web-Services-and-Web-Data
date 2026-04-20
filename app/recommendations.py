import math
import random
import re
import struct
import sys
from functools import lru_cache
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from .models import Book

MODEL_DIR = Path(__file__).resolve().parents[1] / ".models" / "bge-micro-v2"
EMBEDDING_MODEL_NAME = "SmartComponents/bge-micro-v2"

# Requested rerank weights.
MODEL_SIMILARITY_WEIGHT = 0.50
AUTHORS_MATCH_WEIGHT = 0.15
LANGUAGE_MATCH_WEIGHT = 0.10
PUBLISHER_MATCH_WEIGHT = 0.05
AVERAGE_RATING_WEIGHT = 0.10
RATINGS_COUNT_WEIGHT = 0.10

# Diversity penalties applied during final selection.
SAME_TITLE_PENALTY = 0.45
SAME_AUTHORS_PENALTY = 0.18
SAME_PUBLISHER_PENALTY = 0.08
SAME_LANGUAGE_PENALTY = 0.03

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
SERIES_NUMBER_PATTERN = re.compile(r"#\d+")
REASON_TEMPLATES = [
    (
        "Recommended because its title is semantically close to '{target_title}', "
        "with a model contribution of {model_score:.3f}. It also has {rating:.2f}/5 average rating "
        "from {ratings_count} ratings."
    ),
    (
        "This looks like a strong similar-book candidate: the title embedding is close to the selected book, "
        "and {metadata_note} helped its rerank score."
    ),
    (
        "The recommendation engine found title-level similarity with '{target_title}'. "
        "Its popularity signal is {popularity_score:.3f}, while duplicate/diversity penalties total {penalty:.3f}."
    ),
    (
        "Selected as a varied alternative because it balances semantic title similarity, rating quality, "
        "and reader activity without being over-rewarded only for matching metadata."
    ),
    (
        "This book stayed near the top after reranking: semantic similarity contributed {model_score:.3f}, "
        "and the final score after penalties is {final_score:.3f}."
    ),
]


def warm_embeddings(db: Session) -> int:
    books = db.query(Book).all()
    missing_books = [
        book
        for book in books
        if book.title_embedding is None or book.embedding_model != EMBEDDING_MODEL_NAME
    ]
    if not missing_books:
        return 0

    embeddings = _embed_titles([book.title for book in missing_books])
    for book, embedding in zip(missing_books, embeddings, strict=True):
        book.title_embedding = _pack_embedding(embedding)
        book.embedding_model = EMBEDDING_MODEL_NAME

    db.commit()
    return len(missing_books)


def recommend_books(db: Session, target: Book, limit: int = 5) -> list[dict[str, object]]:
    if target.title_embedding is None or target.embedding_model != EMBEDDING_MODEL_NAME:
        warm_embeddings(db)
        db.refresh(target)

    candidates = (
        db.query(Book)
        .filter(
            Book.id != target.id,
            Book.title_embedding.is_not(None),
            Book.embedding_model == EMBEDDING_MODEL_NAME,
        )
        .all()
    )
    if not candidates:
        return []

    target_embedding = _unpack_embedding(target.title_embedding)
    max_log_ratings = max(math.log10(book.ratings_count + 1) for book in [target, *candidates]) or 1.0

    scored_candidates = []
    for candidate in candidates:
        candidate_embedding = _unpack_embedding(candidate.title_embedding)
        similarity = float(_cosine_similarity(target_embedding, candidate_embedding))
        authors_match = _authors_overlap_score(target.authors, candidate.authors)
        language_match = 1.0 if target.language_code == candidate.language_code else 0.0
        publisher_match = 1.0 if _normalize_text(target.publisher) == _normalize_text(candidate.publisher) else 0.0
        average_rating_score = float(max(0.0, min(candidate.average_rating / 5.0, 1.0)))
        ratings_count_score = float(math.log10(candidate.ratings_count + 1) / max_log_ratings)

        weighted_scores = {
            "model_similarity": similarity * MODEL_SIMILARITY_WEIGHT,
            "authors_match": authors_match * AUTHORS_MATCH_WEIGHT,
            "language_match": language_match * LANGUAGE_MATCH_WEIGHT,
            "publisher_match": publisher_match * PUBLISHER_MATCH_WEIGHT,
            "average_rating_score": average_rating_score * AVERAGE_RATING_WEIGHT,
            "ratings_count_score": ratings_count_score * RATINGS_COUNT_WEIGHT,
        }
        base_score = sum(weighted_scores.values())
        scored_candidates.append(
            {
                "book": candidate,
                "base_score": base_score,
                "score_breakdown": {key: round(value, 6) for key, value in weighted_scores.items()},
            }
        )

    return _select_diverse_recommendations(target, scored_candidates, limit=limit)


def _select_diverse_recommendations(
    target: Book, scored_candidates: list[dict[str, object]], limit: int
) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    remaining = scored_candidates.copy()

    while remaining and len(selected) < limit:
        best_item = None
        best_score = float("-inf")

        for item in remaining:
            candidate = item["book"]
            duplicate_penalty = _duplicate_penalty(target, candidate)
            diversity_penalty = sum(
                _pair_penalty(candidate, existing["book"]) for existing in selected
            )
            final_score = item["base_score"] - duplicate_penalty - diversity_penalty

            if final_score > best_score:
                best_score = final_score
                best_item = {
                    **item,
                    "recommendation_score": round(final_score, 6),
                    "duplicate_penalty": round(duplicate_penalty, 6),
                    "diversity_penalty": round(diversity_penalty, 6),
                }

        if best_item is None:
            break

        selected.append(best_item)
        remaining = [item for item in remaining if item["book"].id != best_item["book"].id]

    return selected


def build_recommendation_reason(target: Book, item: dict[str, object]) -> str:
    candidate = item["book"]
    breakdown = item["score_breakdown"]
    metadata_matches = []
    if breakdown["authors_match"] > 0:
        metadata_matches.append("author overlap")
    if breakdown["language_match"] > 0:
        metadata_matches.append("same language")
    if breakdown["publisher_match"] > 0:
        metadata_matches.append("same publisher")
    metadata_note = ", ".join(metadata_matches) if metadata_matches else "rating and popularity"
    penalty = item["duplicate_penalty"] + item["diversity_penalty"]

    template = random.choice(REASON_TEMPLATES)
    return template.format(
        target_title=target.title,
        candidate_title=candidate.title,
        model_score=breakdown["model_similarity"],
        popularity_score=breakdown["ratings_count_score"],
        final_score=item["recommendation_score"],
        metadata_note=metadata_note,
        rating=candidate.average_rating,
        ratings_count=candidate.ratings_count,
        penalty=penalty,
    )


def _duplicate_penalty(target: Book, candidate: Book) -> float:
    penalty = 0.0
    if _normalized_title(target.title) == _normalized_title(candidate.title):
        penalty += SAME_TITLE_PENALTY
    return penalty


def _pair_penalty(candidate: Book, selected_book: Book) -> float:
    penalty = 0.0
    if _normalized_title(candidate.title) == _normalized_title(selected_book.title):
        penalty += SAME_TITLE_PENALTY
    if _normalized_authors(candidate.authors) == _normalized_authors(selected_book.authors):
        penalty += SAME_AUTHORS_PENALTY
    if _normalize_text(candidate.publisher) == _normalize_text(selected_book.publisher):
        penalty += SAME_PUBLISHER_PENALTY
    if candidate.language_code == selected_book.language_code:
        penalty += SAME_LANGUAGE_PENALTY
    return penalty


def _authors_overlap_score(target_authors: str, candidate_authors: str) -> float:
    target_set = _split_authors(target_authors)
    candidate_set = _split_authors(candidate_authors)
    if not target_set or not candidate_set:
        return 0.0
    overlap = target_set & candidate_set
    union = target_set | candidate_set
    return len(overlap) / len(union)


def _split_authors(value: str) -> set[str]:
    return {_normalize_text(part) for part in value.split("/") if part.strip()}


def _normalized_authors(value: str) -> str:
    return "|".join(sorted(_split_authors(value)))


def _normalized_title(value: str) -> str:
    normalized = _normalize_text(value)
    normalized = SERIES_NUMBER_PATTERN.sub(" ", normalized)
    tokens = TOKEN_PATTERN.findall(normalized)
    return " ".join(tokens)


def _normalize_text(value: str) -> str:
    return value.lower().strip()


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(l * r for l, r in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _pack_embedding(values: list[float]) -> bytes:
    return struct.pack(f"<{len(values)}f", *values)


def _unpack_embedding(blob: bytes) -> list[float]:
    if not blob:
        return []
    length = len(blob) // 4
    return list(struct.unpack(f"<{length}f", blob))


def _embed_titles(titles: list[str]) -> list[list[float]]:
    prefixed_titles = [f"Represent this book title for similarity search: {title}" for title in titles]
    embeddings = _get_embedding_model().encode(
        prefixed_titles,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return [embedding.astype("float32").tolist() for embedding in embeddings]


@lru_cache(maxsize=1)
def _get_embedding_model() -> SentenceTransformer:
    _ensure_local_model()
    return SentenceTransformer(str(MODEL_DIR), local_files_only=True)


def _ensure_local_model() -> None:
    required_files = {"config.json", "modules.json", "tokenizer.json"}
    has_required_files = MODEL_DIR.exists() and required_files.issubset(
        {path.name for path in MODEL_DIR.iterdir() if path.is_file()}
    )
    if has_required_files:
        return

    MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
    print(
        f"[Book Insights API] Embedding model not found at {MODEL_DIR}.",
        file=sys.stderr,
        flush=True,
    )
    print(
        f"[Book Insights API] Downloading required model: {EMBEDDING_MODEL_NAME}",
        file=sys.stderr,
        flush=True,
    )
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    model.save(str(MODEL_DIR))
    print(
        f"[Book Insights API] Model downloaded and saved to {MODEL_DIR}.",
        file=sys.stderr,
        flush=True,
    )
