from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories import create_test_user
from video_app.tests.factories import create_test_video


class HLSSegmentViewTest(APITestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_dir.name)
        self.override.enable()
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.override.disable()
        self.temp_dir.cleanup()

    def create_segment(self, video_id: int, segment: str = "720p_00000.ts") -> None:
        hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video_id)
        hls_dir.mkdir(parents=True, exist_ok=True)
        (hls_dir / segment).write_bytes(b"fake segment content")

    def test_segment_is_returned_for_valid_request(self):
        video = create_test_video()
        self.create_segment(video.id)

        response = self.client.get(
            reverse("hls-segment", args=[video.id, "720p", "720p_00000.ts"])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "video/MP2T")

    def test_segment_invalid_resolution_returns_404(self):
        video = create_test_video()

        response = self.client.get(
            reverse("hls-segment", args=[video.id, "144p", "144p_00000.ts"])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_segment_wrong_prefix_returns_404(self):
        video = create_test_video()
        self.create_segment(video.id, "480p_00000.ts")

        response = self.client.get(
            reverse("hls-segment", args=[video.id, "720p", "480p_00000.ts"])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_segment_missing_file_returns_404(self):
        video = create_test_video()

        response = self.client.get(
            reverse("hls-segment", args=[video.id, "720p", "720p_00000.ts"])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)