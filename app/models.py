from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Book(Base):
    # Physical table name in SQLite.
    __tablename__ = "books"

    # ORM model mirrors one book record in the database.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    genre: Mapped[str] = mapped_column(String(80), nullable=False)
    published_year: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
