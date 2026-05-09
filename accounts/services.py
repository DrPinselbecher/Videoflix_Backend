from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .tokens import activation_token_generator

User = get_user_model()


def get_tokens_for_user(user) -> tuple[str, str]:
    """Create access and refresh tokens for the given user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def blacklist_refresh_token(refresh_token: str) -> None:
    """Blacklist the given refresh token."""
    token = RefreshToken(refresh_token)
    token.blacklist()


def get_refreshed_tokens(refresh_token: str) -> tuple[str, str | None]:
    """Validate a refresh token and return the refreshed token values."""
    serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data["access"], serializer.validated_data.get("refresh")


def activate_user(user, token: str) -> bool:
    """Activate a user account if the activation token is valid."""
    if not activation_token_generator.check_token(user, token):
        return False

    user.is_active = True
    user.save(update_fields=["is_active"])
    return True


def get_active_user_by_email(email: str):
    """Return an active user by e-mail address if one exists."""
    return User.objects.filter(email=email.lower(), is_active=True).first()


def is_valid_password_reset_token(user, token: str) -> bool:
    """Check whether the password reset token is valid for the user."""
    return user is not None and default_token_generator.check_token(user, token)


def update_user_password(user, password: str) -> None:
    """Set and persist a new password for the given user."""
    user.set_password(password)
    user.save(update_fields=["password"])