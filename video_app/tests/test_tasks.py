from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import override_settings
from django.test import TestCase

from video_app.tests.factories import create_test_video
from video_app.tasks import process_video


class ProcessVideoTaskTest(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_dir.name)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        self.temp_dir.cleanup()

    @patch("video_app.utils.subprocess.run")
    def test_process_video_generates_thumbnail_and_hls_paths(self, mock_run):
        video = create_test_video()

        process_video(video.id)

        video.refresh_from_db()

        self.assertEqual(mock_run.call_count, 4)
        self.assertEqual(video.thumbnail.name, f"thumbnails/video_{video.id}.jpg")
        self.assertEqual(video.hls_master_playlist, f"hls/{video.id}/master.m3u8")

    @patch("video_app.utils.subprocess.run")
    def test_process_video_ignores_missing_video(self, mock_run):
        process_video(999999)

        mock_run.assert_not_called()