from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    authors: str = Field(min_length=1, max_length=255)
    average_rating: float = Field(ge=0, le=5)
    isbn: str = Field(min_length=1, max_length=20)
    isbn13: str = Field(min_length=1, max_length=20)
    language_code: str = Field(min_length=1, max_length=20)
    num_pages: int = Field(ge=0)
    ratings_count: int = Field(ge=0)
    text_reviews_count: int = Field(ge=0)
    publication_date: str = Field(min_length=1, max_length=20)
    publisher: str = Field(min_length=1, max_length=255)


class BookCreate(BookBase):
    bookID: int | None = Field(default=None, ge=1)


class BookUpdate(BaseModel):
    bookID: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    authors: str | None = Field(default=None, min_length=1, max_length=255)
    average_rating: float | None = Field(default=None, ge=0, le=5)
    isbn: str | None = Field(default=None, min_length=1, max_length=20)
    isbn13: str | None = Field(default=None, min_length=1, max_length=20)
    language_code: str | None = Field(default=None, min_length=1, max_length=20)
    num_pages: int | None = Field(default=None, ge=0)
    ratings_count: int | None = Field(default=None, ge=0)
    text_reviews_count: int | None = Field(default=None, ge=0)
    publication_date: str | None = Field(default=None, min_length=1, max_length=20)
    publisher: str | None = Field(default=None, min_length=1, max_length=255)


class BookOut(BookBase):
    id: int
    bookID: int

    model_config = ConfigDict(from_attributes=True)


class RecommendationBreakdown(BaseModel):
    model_similarity: float
    authors_match: float
    language_match: float
    publisher_match: float
    average_rating_score: float
    ratings_count_score: float
    duplicate_penalty: float
    diversity_penalty: float

    model_config = ConfigDict(protected_namespaces=())


class BookRecommendationOut(BookOut):
    recommendation_score: float
    score_breakdown: RecommendationBreakdown
    reason: str
