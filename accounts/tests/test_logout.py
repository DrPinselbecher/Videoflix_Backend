from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.tests.factories import create_test_user


class LogoutViewTest(APITestCase):
    """Test logout endpoint behavior."""

    def test_logout_blacklists_refresh_token_and_deletes_cookies(self):
        """Blacklist refresh token and clear auth cookies on logout."""
        user = create_test_user()
        refresh = RefreshToken.for_user(user)
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = str(refresh)

        response = self.client.post(reverse("account-logout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.JWT_ACCESS_COOKIE_NAME, response.cookies)
        self.assertIn(settings.JWT_REFRESH_COOKIE_NAME, response.cookies)

    def test_logout_without_refresh_token_fails(self):
        """Reject logout requests without a refresh token cookie."""
        response = self.client.post(reverse("account-logout"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)