from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegisterViewTest(APITestCase):
    def test_register_creates_inactive_user_and_sends_email(self):
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

    def test_register_rejects_existing_email(self):
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