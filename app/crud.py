from django.db.models import Max, Q
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .models import Book


class ConflictError(APIException):
    status_code = 409
    default_detail = "Conflict"
    default_code = "conflict"


def next_book_id() -> int:
    return (Book.objects.aggregate(max_id=Max("bookID"))["max_id"] or 0) + 1


def list_books(skip: int, limit: int):
    return Book.objects.all()[skip : skip + limit]


def search_books(
    skip: int,
    limit: int,
    book_id: int | None = None,
    title: str | None = None,
    authors: str | None = None,
    isbn: str | None = None,
    isbn13: str | None = None,
    language_code: str | None = None,
    publisher: str | None = None,
):
    query = Q()
    if book_id is not None:
        query &= Q(bookID=book_id)
    if title:
        query &= Q(title__icontains=title)
    if authors:
        query &= Q(authors__icontains=authors)
    if isbn:
        query &= Q(isbn__icontains=isbn)
    if isbn13:
        query &= Q(isbn13__icontains=isbn13)
    if language_code:
        query &= Q(language_code__icontains=language_code)
    if publisher:
        query &= Q(publisher__icontains=publisher)
    return Book.objects.filter(query)[skip : skip + limit]


def get_book_or_404(book_id: int) -> Book:
    try:
        return Book.objects.get(id=book_id)
    except Book.DoesNotExist as exc:
        raise NotFound(detail="Book not found") from exc


def create_book(validated_data: dict) -> Book:
    if validated_data.get("bookID") is None:
        validated_data["bookID"] = next_book_id()

    if Book.objects.filter(bookID=validated_data["bookID"]).exists():
        raise ConflictError(detail="bookID already exists")

    return Book.objects.create(**validated_data)


def update_book(book_id: int, validated_data: dict) -> Book:
    if not validated_data:
        raise ValidationError(detail="No fields provided")

    book = get_book_or_404(book_id)
    new_book_id = validated_data.get("bookID")
    if new_book_id is not None and new_book_id != book.bookID:
        if Book.objects.filter(bookID=new_book_id).exclude(id=book.id).exists():
            raise ConflictError(detail="bookID already exists")

    for field, value in validated_data.items():
        setattr(book, field, value)

    book.save()
    return book


def delete_book(book_id: int) -> None:
    book = get_book_or_404(book_id)
    book.delete()
