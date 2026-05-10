from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import activation_token_generator


def build_frontend_url(path: str, uidb64: str, token: str) -> str:
    """Build a frontend URL containing uidb64 and token query parameters."""
    query_params = urlencode({"uidb64": uidb64, "token": token})
    return f"{settings.FRONTEND_BASE_URL}/{path}?{query_params}"


def get_uidb64(user) -> str:
    """Return the base64 encoded primary key for a user."""
    return urlsafe_base64_encode(force_bytes(user.pk))


def send_activation_email(user) -> str:
    """Send an account activation e-mail to the given user."""
    uidb64 = get_uidb64(user)
    token = activation_token_generator.make_token(user)
    activation_url = build_frontend_url("pages/auth/activate.html", uidb64, token)

    _send_html_email(
        subject="Activate your Videoflix account",
        template_name="accounts/emails/activation_email.html",
        action_url=activation_url,
        recipient=user.email,
    )

    return token


def send_password_reset_email(user) -> None:
    """Send a password reset e-mail to the given user."""
    uidb64 = get_uidb64(user)
    token = default_token_generator.make_token(user)
    reset_url = build_frontend_url("pages/auth/password_confirm.html", uidb64, token)

    _send_html_email(
        subject="Reset your Videoflix password",
        template_name="accounts/emails/password_reset_email.html",
        action_url=reset_url,
        recipient=user.email,
    )


def _send_html_email(subject: str, template_name: str, action_url: str, recipient: str):
    """Send an HTML e-mail with plain text fallback."""
    html_body = render_to_string(template_name, {"action_url": action_url})
    text_body = strip_tags(html_body)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
