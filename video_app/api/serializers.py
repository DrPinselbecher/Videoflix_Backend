from rest_framework import serializers

from video_app.models import Video


class VideoListSerializer(serializers.ModelSerializer):
    """Serialize video data for the protected video list endpoint."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        ]

    def get_thumbnail_url(self, obj: Video) -> str | None:
        """Return an absolute thumbnail URL if a thumbnail exists."""
        if not obj.thumbnail:
            return None

        request = self.context.get("request")
        thumbnail_url = obj.thumbnail.url

        if request is None:
            return thumbnail_url

        return request.build_absolute_uri(thumbnail_url)