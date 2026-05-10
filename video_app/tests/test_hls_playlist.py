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
    """Test protected HLS playlist endpoint behavior."""

    def setUp(self):
        """Create temporary media storage and authenticate the test user."""
        self.temp_dir = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_dir.name)
        self.override.enable()
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """Clean up temporary media storage."""
        self.override.disable()
        self.temp_dir.cleanup()

    def create_playlist(self, video_id: int, resolution: str = "720p") -> None:
        """Create a temporary HLS playlist file."""
        hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video_id)
        hls_dir.mkdir(parents=True, exist_ok=True)
        (hls_dir / f"{resolution}.m3u8").write_text("#EXTM3U\n", encoding="utf-8")

    def test_playlist_is_returned_for_valid_resolution(self):
        """Return playlist file for a valid resolution."""
        video = create_test_video()
        self.create_playlist(video.id)

        response = self.client.get(reverse("hls-playlist", args=[video.id, "720p"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/vnd.apple.mpegurl")

    def test_playlist_invalid_resolution_returns_404(self):
        """Return 404 for unsupported HLS resolution."""
        video = create_test_video()

        response = self.client.get(reverse("hls-playlist", args=[video.id, "144p"]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_playlist_missing_file_returns_404(self):
        """Return 404 when the playlist file does not exist."""
        video = create_test_video()

        response = self.client.get(reverse("hls-playlist", args=[video.id, "720p"]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)