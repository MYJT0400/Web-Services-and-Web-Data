from sqlalchemy import Float, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bookID: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    authors: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    average_rating: Mapped[float] = mapped_column(Float, nullable=False)
    isbn: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    isbn13: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    language_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    num_pages: Mapped[int] = mapped_column(Integer, nullable=False)
    ratings_count: Mapped[int] = mapped_column(Integer, nullable=False)
    text_reviews_count: Mapped[int] = mapped_column(Integer, nullable=False)
    publication_date: Mapped[str] = mapped_column(String(20), nullable=False)
    publisher: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title_embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(80), nullable=True)
