from django.db import models


class Video(models.Model):
    """Store uploaded video metadata and generated media paths."""

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=120)
    description = models.TextField()
    video_file = models.FileField(upload_to="videos/")
    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
        null=True,
        help_text="Optional. Wird automatisch aus dem Video erstellt.",
    )
    hls_master_playlist = models.CharField(
        max_length=500,
        blank=True,
        editable=False,
    )
    category = models.CharField(max_length=50)

    def __str__(self):
        """Return the video title as string representation."""
        return self.title