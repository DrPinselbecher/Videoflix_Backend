from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


def create_test_user(email: str = "user@example.com", is_active: bool = True):
    """Create a test user with e-mail as username."""
    return User.objects.create_user(
        username=email,
        email=email,
        password="StrongPass123!",
        is_active=is_active,
    )


def get_uidb64(user) -> str:
    """Return the base64 encoded user ID."""
    return urlsafe_base64_encode(force_bytes(user.pk))