from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from urllib.parse import parse_qs, urlparse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories import create_test_user, get_uidb64


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetViewTest(APITestCase):
    """Test password reset request endpoint behavior."""

    def test_password_reset_sends_email_for_active_user(self):
        """Send a reset e-mail for an active user account."""
        create_test_user()

        response = self.client.post(reverse("password-reset"), {
            "email": "user@example.com",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        reset_link = mail.outbox[0].alternatives[0][0]
        self.assertIn("password_confirm.html", reset_link)

    def test_password_reset_email_contains_uidb64_and_token(self):
        """Include uidb64 and token query params in reset link."""
        user = create_test_user()

        self.client.post(reverse("password-reset"), {"email": user.email})

        email_body = mail.outbox[0].alternatives[0][0]
        start = email_body.find("http")
        end = email_body.find('"', start)
        reset_url = email_body[start:end]
        query = parse_qs(urlparse(reset_url).query)
        self.assertIn("uidb64", query)
        self.assertIn("token", query)
        self.assertTrue(query["uidb64"][0])
        self.assertTrue(query["token"][0])

    def test_password_reset_email_contains_html_alternative(self):
        """Render password reset e-mail as HTML plus plain text."""
        create_test_user()

        self.client.post(reverse("password-reset"), {"email": "user@example.com"})

        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")

    def test_password_reset_does_not_expose_unknown_email(self):
        """Return success without sending e-mail for unknown accounts."""
        response = self.client.post(reverse("password-reset"), {
            "email": "unknown@example.com",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)


class PasswordConfirmViewTest(APITestCase):
    """Test password confirmation endpoint behavior."""

    def test_password_confirm_updates_password(self):
        """Update the user password with a valid reset token."""
        user = create_test_user()
        uidb64 = get_uidb64(user)
        token = default_token_generator.make_token(user)

        response = self.client.post(reverse("password-confirm", args=[uidb64, token]), {
            "new_password": "NewStrongPass123!",
            "confirm_password": "NewStrongPass123!",
        })

        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password("NewStrongPass123!"))

    def test_password_confirm_with_invalid_token_fails(self):
        """Reject password confirmation with an invalid reset token."""
        user = create_test_user()
        uidb64 = get_uidb64(user)

        response = self.client.post(reverse("password-confirm", args=[uidb64, "invalid"]), {
            "new_password": "NewStrongPass123!",
            "confirm_password": "NewStrongPass123!",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
