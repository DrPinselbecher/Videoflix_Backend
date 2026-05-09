from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response

User = get_user_model()


def set_jwt_cookie(response: Response, key: str, value: str, max_age: int) -> None:
    """Set a JWT cookie with the configured security options."""
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=max_age,
    )


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str | None = None,
) -> None:
    """Set access and optional refresh token cookies on a response."""
    set_jwt_cookie(
        response,
        settings.JWT_ACCESS_COOKIE_NAME,
        access_token,
        settings.JWT_ACCESS_COOKIE_MAX_AGE,
    )

    if refresh_token is not None:
        set_jwt_cookie(
            response,
            settings.JWT_REFRESH_COOKIE_NAME,
            refresh_token,
            settings.JWT_REFRESH_COOKIE_MAX_AGE,
        )


def delete_auth_cookies(response: Response) -> None:
    """Delete authentication cookies from a response."""
    response.delete_cookie(settings.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(settings.JWT_REFRESH_COOKIE_NAME)


def get_refresh_token_from_request(request) -> str | None:
    """Return the refresh token from request cookies if present."""
    return request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)


def get_user_from_uidb64(uidb64: str):
    """Return a user instance from a base64 encoded user ID."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None