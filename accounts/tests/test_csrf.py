from django.middleware.csrf import CSRF_COOKIE_NAME
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CsrfTokenViewTest(APITestCase):
    """Test explicit CSRF cookie endpoint."""

    def test_csrf_endpoint_sets_cookie(self):
        """Return success and set the CSRF cookie."""
        response = self.client.get(reverse("csrf-cookie"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(CSRF_COOKIE_NAME, response.cookies)
