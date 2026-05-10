from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from urllib.parse import parse_qs, urlparse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegisterViewTest(APITestCase):
    """Test user registration endpoint behavior."""

    def test_register_creates_inactive_user_and_sends_email(self):
        """Create an inactive user and send an activation e-mail."""
        url = reverse("account-register")
        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "StrongPass123!",
        }

        response = self.client.post(url, data, format="json")
        user = User.objects.get(email="test@example.com")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(user.is_active)
        self.assertEqual(user.username, "test@example.com")
        self.assertEqual(len(mail.outbox), 1)

    def test_register_email_contains_frontend_activation_link(self):
        """Embed frontend activation URL with uidb64 and token query params."""
        self.client.post(reverse("account-register"), {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "StrongPass123!",
        })

        email_body = mail.outbox[0].alternatives[0][0]
        start = email_body.find("http")
        end = email_body.find('"', start)
        activation_url = email_body[start:end]
        query = parse_qs(urlparse(activation_url).query)
        self.assertIn("activate.html", activation_url)
        self.assertIn("uidb64", query)
        self.assertIn("token", query)

    def test_register_sends_html_activation_email(self):
        """Send activation e-mail with HTML alternative content."""
        self.client.post(reverse("account-register"), {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "StrongPass123!",
        })

        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")

    def test_register_rejects_existing_email(self):
        """Reject registration when the e-mail address already exists."""
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(reverse("account-register"), {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "StrongPass123!",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
