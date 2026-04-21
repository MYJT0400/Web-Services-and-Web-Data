from django.db import models


class Book(models.Model):
    bookID = models.PositiveIntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    authors = models.CharField(max_length=255, db_index=True)
    average_rating = models.FloatField()
    isbn = models.CharField(max_length=20, db_index=True)
    isbn13 = models.CharField(max_length=20, db_index=True)
    language_code = models.CharField(max_length=20, db_index=True)
    num_pages = models.IntegerField()
    ratings_count = models.IntegerField()
    text_reviews_count = models.IntegerField()
    publication_date = models.CharField(max_length=20)
    publisher = models.CharField(max_length=255, db_index=True)
    title_embedding = models.BinaryField(null=True, blank=True)
    embedding_model = models.CharField(max_length=80, null=True, blank=True)

    class Meta:
        db_table = "books"
        managed = False
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.title} ({self.bookID})"
