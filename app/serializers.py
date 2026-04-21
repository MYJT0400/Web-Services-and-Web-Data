from rest_framework import serializers

from .models import Book


class BookWriteSerializer(serializers.ModelSerializer):
    bookID = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    title = serializers.CharField(min_length=1, max_length=255)
    authors = serializers.CharField(min_length=1, max_length=255)
    average_rating = serializers.FloatField()
    isbn = serializers.CharField(min_length=1, max_length=20)
    isbn13 = serializers.CharField(min_length=1, max_length=20)
    language_code = serializers.CharField(min_length=1, max_length=20)
    num_pages = serializers.IntegerField(min_value=0)
    ratings_count = serializers.IntegerField(min_value=0)
    text_reviews_count = serializers.IntegerField(min_value=0)
    publication_date = serializers.CharField(min_length=1, max_length=20)
    publisher = serializers.CharField(min_length=1, max_length=255)

    class Meta:
        model = Book
        fields = [
            "bookID",
            "title",
            "authors",
            "average_rating",
            "isbn",
            "isbn13",
            "language_code",
            "num_pages",
            "ratings_count",
            "text_reviews_count",
            "publication_date",
            "publisher",
        ]

    def validate_average_rating(self, value: float) -> float:
        if not 0 <= value <= 5:
            raise serializers.ValidationError("Ensure this value is between 0 and 5.")
        return value


class BookSerializer(BookWriteSerializer):
    id = serializers.IntegerField(read_only=True)
    bookID = serializers.IntegerField(read_only=True)

    class Meta(BookWriteSerializer.Meta):
        fields = ["id", *BookWriteSerializer.Meta.fields]


class RecommendationBreakdownSerializer(serializers.Serializer):
    model_similarity = serializers.FloatField()
    authors_match = serializers.FloatField()
    language_match = serializers.FloatField()
    publisher_match = serializers.FloatField()
    average_rating_score = serializers.FloatField()
    ratings_count_score = serializers.FloatField()
    duplicate_penalty = serializers.FloatField()
    title_diversity_penalty = serializers.FloatField()
    authors_diversity_penalty = serializers.FloatField()
    language_diversity_penalty = serializers.FloatField()
    publisher_diversity_penalty = serializers.FloatField()
    diversity_penalty = serializers.FloatField()


class BookRecommendationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    bookID = serializers.IntegerField()
    title = serializers.CharField()
    authors = serializers.CharField()
    average_rating = serializers.FloatField()
    isbn = serializers.CharField()
    isbn13 = serializers.CharField()
    language_code = serializers.CharField()
    num_pages = serializers.IntegerField()
    ratings_count = serializers.IntegerField()
    text_reviews_count = serializers.IntegerField()
    publication_date = serializers.CharField()
    publisher = serializers.CharField()
    recommendation_score = serializers.FloatField()
    score_breakdown = RecommendationBreakdownSerializer()
    reason = serializers.CharField()
