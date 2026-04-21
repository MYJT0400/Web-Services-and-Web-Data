from django.core.management.base import BaseCommand

from app.seed import initialize_database


class Command(BaseCommand):
    help = "Create/upgrade the books table, import books.csv, and warm embeddings."

    def handle(self, *args, **options):
        initialize_database()
        self.stdout.write(self.style.SUCCESS("ready"))
