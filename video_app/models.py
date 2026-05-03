from django.db import models


class Video(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=120)
    description = models.TextField()
    video_file = models.FileField(upload_to="videos/")
    thumbnail = models.ImageField(upload_to="thumbnails/")
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.title