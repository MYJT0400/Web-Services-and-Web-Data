from django.apps import AppConfig as DjangoAppConfig


class BookInsightsAppConfig(DjangoAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self) -> None:
        from . import schema  # noqa: F401
