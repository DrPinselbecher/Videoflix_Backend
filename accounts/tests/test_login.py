from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories import create_test_user


class LoginViewTest(APITestCase):
    """Test login endpoint behavior."""

    def test_login_sets_auth_cookies(self):
        """Set access and refresh cookies after successful login."""
        create_test_user()

        response = self.client.post(reverse("account-login"), {
            "email": "user@example.com",
            "password": "StrongPass123!",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.JWT_ACCESS_COOKIE_NAME, response.cookies)
        self.assertIn(settings.JWT_REFRESH_COOKIE_NAME, response.cookies)

    def test_login_rejects_invalid_credentials(self):
        """Reject login with an invalid password."""
        create_test_user()

        response = self.client.post(reverse("account-login"), {
            "email": "user@example.com",
            "password": "wrong-password",
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_rejects_inactive_user(self):
        """Reject login for inactive user accounts."""
        create_test_user(is_active=False)

        response = self.client.post(reverse("account-login"), {
            "email": "user@example.com",
            "password": "StrongPass123!",
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
