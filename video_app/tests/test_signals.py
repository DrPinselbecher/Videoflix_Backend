from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test import TestCase

from video_app.models import Video
from video_app.tests.factories import create_test_video


class VideoSignalTest(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_dir.name)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        self.temp_dir.cleanup()

    @patch("video_app.signals.process_video.delay")
    def test_video_post_save_enqueues_processing_job(self, mock_delay):
        video_file = SimpleUploadedFile(
            "signal_video.mp4",
            b"fake video content",
            content_type="video/mp4",
        )

        with self.captureOnCommitCallbacks(execute=True):
            video = Video.objects.create(
                title="Signal Video",
                description="Signal description",
                video_file=video_file,
                category="Action",
            )

        mock_delay.assert_called_once_with(video.id)

    def test_video_post_delete_removes_related_files(self):
        video = create_test_video(thumbnail=True)
        hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video.id)
        hls_dir.mkdir(parents=True, exist_ok=True)
        hls_file = hls_dir / "720p.m3u8"
        hls_file.write_text("#EXTM3U\n", encoding="utf-8")

        video_path = Path(video.video_file.path)
        thumbnail_path = Path(video.thumbnail.path)

        self.assertTrue(video_path.exists())
        self.assertTrue(thumbnail_path.exists())
        self.assertTrue(hls_file.exists())

        with self.captureOnCommitCallbacks(execute=True):
            video.delete()

        self.assertFalse(video_path.exists())
        self.assertFalse(thumbnail_path.exists())
        self.assertFalse(hls_dir.exists())