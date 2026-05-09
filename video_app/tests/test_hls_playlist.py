from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories import create_test_user
from video_app.tests.factories import create_test_video


class HLSPlaylistViewTest(APITestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_dir.name)
        self.override.enable()
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.override.disable()
        self.temp_dir.cleanup()

    def create_playlist(self, video_id: int, resolution: str = "720p") -> None:
        hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video_id)
        hls_dir.mkdir(parents=True, exist_ok=True)
        (hls_dir / f"{resolution}.m3u8").write_text("#EXTM3U\n", encoding="utf-8")

    def test_playlist_is_returned_for_valid_resolution(self):
        video = create_test_video()
        self.create_playlist(video.id)

        response = self.client.get(reverse("hls-playlist", args=[video.id, "720p"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/vnd.apple.mpegurl")

    def test_playlist_invalid_resolution_returns_404(self):
        video = create_test_video()

        response = self.client.get(reverse("hls-playlist", args=[video.id, "144p"]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_playlist_missing_file_returns_404(self):
        video = create_test_video()

        response = self.client.get(reverse("hls-playlist", args=[video.id, "720p"]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)