from django.db import models


class Video(models.Model):
    """Store uploaded video metadata and generated media paths."""

    class Category(models.TextChoices):
        ACTION = "action", "Action"
        ADVENTURE = "adventure", "Adventure"
        ANIMATION = "animation", "Animation"
        ANIME = "anime", "Anime"
        COMEDY = "comedy", "Comedy"
        CRIME = "crime", "Crime"
        DOCUMENTARY = "documentary", "Documentary"
        DRAMA = "drama", "Drama"
        FAMILY = "family", "Family"
        FANTASY = "fantasy", "Fantasy"
        HISTORY = "history", "History"
        HORROR = "horror", "Horror"
        KIDS = "kids", "Kids"
        MYSTERY = "mystery", "Mystery"
        NATURE = "nature", "Nature"
        REALITY = "reality", "Reality"
        ROMANCE = "romance", "Romance"
        SCI_FI = "sci-fi", "Sci-Fi"
        SPORTS = "sports", "Sports"
        THRILLER = "thriller", "Thriller"
        WAR = "war", "War"
        WESTERN = "western", "Western"

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
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.ACTION,
    )

    def __str__(self):
        """Return the video title as string representation."""
        return self.title