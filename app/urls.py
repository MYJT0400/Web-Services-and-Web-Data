from django.urls import path

from .views import BookDetailView, BookListCreateView, BookRecommendationsView, health_check, home_page

urlpatterns = [
    path("", home_page, name="home"),
    path("health", health_check, name="health"),
    path("books", BookListCreateView.as_view(), name="books"),
    path("books/<int:book_id>", BookDetailView.as_view(), name="book-detail"),
    path(
        "books/<int:book_id>/recommendations",
        BookRecommendationsView.as_view(),
        name="book-recommendations",
    ),
]
