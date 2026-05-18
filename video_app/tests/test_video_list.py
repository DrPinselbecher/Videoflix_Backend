from tempfile import TemporaryDirectory

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories import create_test_user
from video_app.tests.factories import create_processed_test_video


class VideoListViewTest(APITestCase):
    """Test protected video list endpoint behavior."""

    def setUp(self):
        """Create temporary media storage."""
        self.temp_dir = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_dir.name)
        self.override.enable()

    def tearDown(self):
        """Clean up temporary media storage."""
        self.override.disable()
        self.temp_dir.cleanup()

    def test_video_list_requires_authentication(self):
        """Reject unauthenticated video list requests."""
        response = self.client.get(reverse("video-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_video_list_returns_videos_for_authenticated_user(self):
        """Return available videos for an authenticated user."""
        user = create_test_user()

        create_processed_test_video(
            title="First Video",
            hls_master_playlist="hls/1/master.m3u8",
        )
        create_processed_test_video(
            title="Second Video",
            hls_master_playlist="hls/2/master.m3u8",
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("video-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_video_list_returns_thumbnail_url(self):
        """Return a thumbnail URL if a video has a thumbnail."""
        user = create_test_user()

        create_processed_test_video(
            thumbnail=True,
            hls_master_playlist="hls/1/master.m3u8",
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("video-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIsNotNone(response.data[0]["thumbnail_url"])