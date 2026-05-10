from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    """Configure the video app and register model signals."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "video_app"

    def ready(self):
        """Import signal handlers when the app is ready."""
        import video_app.signals  # noqa: F401