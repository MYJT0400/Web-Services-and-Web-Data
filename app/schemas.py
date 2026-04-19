from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    # Shared validation rules for request/response data.
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    genre: str = Field(min_length=1, max_length=80)
    published_year: int = Field(ge=0, le=2100)
    summary: str = Field(default="", max_length=2000)


class BookCreate(BookBase):
    # Create payload uses all required fields from BookBase.
    pass


class BookUpdate(BaseModel):
    # All fields are optional so clients can send partial updates.
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=120)
    genre: str | None = Field(default=None, min_length=1, max_length=80)
    published_year: int | None = Field(default=None, ge=0, le=2100)
    summary: str | None = Field(default=None, max_length=2000)


class BookOut(BookBase):
    # Response model includes generated database ID.
    id: int

    # Allow returning SQLAlchemy objects directly from route handlers.
    model_config = ConfigDict(from_attributes=True)
