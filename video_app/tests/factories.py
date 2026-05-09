from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from video_app.models import Video


def create_test_video(
    title: str = "Test Video",
    category: str = "Action",
    thumbnail: bool = False,
) -> Video:
    """Create a test video without starting the RQ processing job."""
    video_file = SimpleUploadedFile(
        "test_video.mp4",
        b"fake video content",
        content_type="video/mp4",
    )

    thumbnail_file = None

    if thumbnail:
        thumbnail_file = SimpleUploadedFile(
            "test_thumbnail.jpg",
            b"fake image content",
            content_type="image/jpeg",
        )

    with patch("video_app.signals.process_video.delay"):
        return Video.objects.create(
            title=title,
            description="Test description",
            video_file=video_file,
            thumbnail=thumbnail_file,
            category=category,
        )