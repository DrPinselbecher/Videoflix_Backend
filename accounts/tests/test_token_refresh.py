from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.tests.factories import create_test_user


class CookieTokenRefreshViewTest(APITestCase):
    def test_refresh_token_creates_new_access_cookie(self):
        user = create_test_user()
        refresh = RefreshToken.for_user(user)
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = str(refresh)

        response = self.client.post(reverse("token-refresh"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.JWT_ACCESS_COOKIE_NAME, response.cookies)

    def test_refresh_without_cookie_fails(self):
        response = self.client.post(reverse("token-refresh"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)