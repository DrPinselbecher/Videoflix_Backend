from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories import create_test_user, get_uidb64


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetViewTest(APITestCase):
    def test_password_reset_sends_email_for_active_user(self):
        create_test_user()

        response = self.client.post(reverse("password-reset"), {
            "email": "user@example.com",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_does_not_expose_unknown_email(self):
        response = self.client.post(reverse("password-reset"), {
            "email": "unknown@example.com",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)


class PasswordConfirmViewTest(APITestCase):
    def test_password_confirm_updates_password(self):
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
        user = create_test_user()
        uidb64 = get_uidb64(user)

        response = self.client.post(reverse("password-confirm", args=[uidb64, "invalid"]), {
            "new_password": "NewStrongPass123!",
            "confirm_password": "NewStrongPass123!",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)