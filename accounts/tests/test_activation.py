from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories import create_test_user, get_uidb64
from accounts.tokens import activation_token_generator


class ActivateViewTest(APITestCase):
    """Test account activation endpoint behavior."""

    def test_activate_user_with_valid_token(self):
        """Activate an inactive user with a valid activation token."""
        user = create_test_user(is_active=False)
        uidb64 = get_uidb64(user)
        token = activation_token_generator.make_token(user)

        response = self.client.get(
            reverse("account-activate", args=[uidb64, token])
        )
        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.is_active)
        self.assertEqual(response.data["message"], "Account successfully activated.")

    def test_activate_user_with_invalid_token_fails(self):
        """Reject account activation with an invalid token."""
        user = create_test_user(is_active=False)
        uidb64 = get_uidb64(user)

        response = self.client.get(
            reverse("account-activate", args=[uidb64, "invalid"])
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)