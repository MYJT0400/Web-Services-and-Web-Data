from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import ApiKeyWritePermission
from .crud import create_book, delete_book, get_book_or_404, list_books, search_books, update_book
from .recommendations import recommend_books, serialize_recommendation
from .serializers import BookRecommendationSerializer, BookSerializer, BookWriteSerializer
from .ui import render_home_page


def _parse_int_param(value: str | None, name: str, *, minimum: int | None = None, maximum: int | None = None) -> int | None:
    if value is None:
        return None

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(detail={name: "A valid integer is required."}) from exc

    if minimum is not None and parsed < minimum:
        raise ValidationError(detail={name: f"Ensure this value is greater than or equal to {minimum}."})
    if maximum is not None and parsed > maximum:
        raise ValidationError(detail={name: f"Ensure this value is less than or equal to {maximum}."})
    return parsed


@require_GET
def home_page(request):
    return HttpResponse(render_home_page())


@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"})


class BookListCreateView(APIView):
    permission_classes = [ApiKeyWritePermission]

    @extend_schema(
        responses=BookSerializer(many=True),
        parameters=[
            OpenApiParameter("skip", int, default=0),
            OpenApiParameter("limit", int, default=20),
            OpenApiParameter("book_id", int),
            OpenApiParameter("title", str),
            OpenApiParameter("authors", str),
            OpenApiParameter("isbn", str),
            OpenApiParameter("isbn13", str),
            OpenApiParameter("language_code", str),
            OpenApiParameter("publisher", str),
        ],
    )
    def get(self, request):
        skip = _parse_int_param(request.query_params.get("skip", "0"), "skip", minimum=0) or 0
        limit = _parse_int_param(request.query_params.get("limit", "20"), "limit", minimum=1, maximum=100000) or 20
        book_id = _parse_int_param(request.query_params.get("book_id"), "book_id", minimum=1)
        title = request.query_params.get("title")
        authors = request.query_params.get("authors")
        isbn = request.query_params.get("isbn")
        isbn13 = request.query_params.get("isbn13")
        language_code = request.query_params.get("language_code")
        publisher = request.query_params.get("publisher")

        filters = [book_id, title, authors, isbn, isbn13, language_code, publisher]
        if any(value is not None for value in filters):
            books = search_books(
                skip=skip,
                limit=limit,
                book_id=book_id,
                title=title,
                authors=authors,
                isbn=isbn,
                isbn13=isbn13,
                language_code=language_code,
                publisher=publisher,
            )
        else:
            books = list_books(skip, limit)

        return Response(BookSerializer(books, many=True).data)

    @extend_schema(request=BookWriteSerializer, responses={201: BookSerializer})
    def post(self, request):
        serializer = BookWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = create_book(serializer.validated_data)
        return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)


class BookDetailView(APIView):
    permission_classes = [ApiKeyWritePermission]

    @extend_schema(responses=BookSerializer)
    def get(self, request, book_id: int):
        return Response(BookSerializer(get_book_or_404(book_id)).data)

    @extend_schema(request=BookWriteSerializer, responses=BookSerializer)
    def put(self, request, book_id: int):
        serializer = BookWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        book = update_book(book_id, serializer.validated_data)
        return Response(BookSerializer(book).data)

    @extend_schema(responses={204: None})
    def delete(self, request, book_id: int):
        delete_book(book_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookRecommendationsView(APIView):
    permission_classes = [ApiKeyWritePermission]

    @extend_schema(responses=BookRecommendationSerializer(many=True))
    def get(self, request, book_id: int):
        limit = _parse_int_param(request.query_params.get("limit", "5"), "limit", minimum=1, maximum=20) or 5
        target_book = get_book_or_404(book_id)
        data = [
            serialize_recommendation(target_book, item)
            for item in recommend_books(target_book, limit=limit)
        ]
        return Response(BookRecommendationSerializer(data, many=True).data)
