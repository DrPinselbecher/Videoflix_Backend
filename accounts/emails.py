from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
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


def get_logo_url() -> str:
    """Return the frontend logo URL used inside HTML e-mails."""
    return f"{settings.FRONTEND_BASE_URL}/assets/icons/logo_icon.svg"


def send_html_email(subject: str, text_body: str, html_body: str, recipient: str) -> None:
    """Send an e-mail with plain text and HTML alternative."""
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)


def build_activation_email_html(user, activation_url: str) -> str:
    """Build the HTML body for the account activation e-mail."""
    return f"""
    <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="text-align: center; margin-bottom: 28px;">
            <img src="{get_logo_url()}" alt="Videoflix" style="max-width: 280px;">
        </div>

        <p>Dear {user.email},</p>

        <p>
            Thank you for registering with <span style="color: #1f2bff;">Videoflix</span>.
            To complete your registration and verify your e-mail address,
            please click the link below:
        </p>

        <p style="margin: 32px 0;">
            <a href="{activation_url}"
               style="background: #1f2bff; color: #ffffff; text-decoration: none;
                      padding: 14px 28px; border-radius: 28px; font-weight: bold;
                      display: inline-block;">
                Activate account
            </a>
        </p>

        <p>If you did not create an account with us, please disregard this e-mail.</p>

        <p>Best regards,</p>
        <p>Your Videoflix Team.</p>
    </div>
    """


def build_password_reset_email_html(reset_url: str) -> str:
    """Build the HTML body for the password reset e-mail."""
    return f"""
    <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <p>Hello,</p>

        <p>
            We recently received a request to reset your password. If you made this request,
            please click on the following link to reset your password:
        </p>

        <p style="margin: 32px 0;">
            <a href="{reset_url}"
               style="background: #1f2bff; color: #ffffff; text-decoration: none;
                      padding: 14px 28px; border-radius: 28px; font-weight: bold;
                      display: inline-block;">
                Reset password
            </a>
        </p>

        <p>Please note that for security reasons, this link is only valid for 24 hours.</p>

        <p>If you did not request a password reset, please ignore this e-mail.</p>

        <p>Best regards,</p>
        <p>Your Videoflix team!</p>

        <div style="margin-top: 32px;">
            <img src="{get_logo_url()}" alt="Videoflix" style="max-width: 280px;">
        </div>
    </div>
    """


def send_activation_email(user) -> str:
    """Send an account activation e-mail to the given user."""
    uidb64 = get_uidb64(user)
    token = activation_token_generator.make_token(user)
    activation_url = build_frontend_url("pages/auth/activate.html", uidb64, token)
    text_body = f"Activate your account:\n{activation_url}"
    html_body = build_activation_email_html(user, activation_url)

    send_html_email(
        "Confirm your email",
        text_body,
        html_body,
        user.email,
    )

    return token


def send_password_reset_email(user) -> None:
    """Send a password reset e-mail to the given user."""
    uidb64 = get_uidb64(user)
    token = default_token_generator.make_token(user)
    reset_url = build_frontend_url("pages/auth/confirm_password.html", uidb64, token)
    text_body = f"Reset your password:\n{reset_url}"
    html_body = build_password_reset_email_html(reset_url)

    send_html_email(
        "Reset your Password",
        text_body,
        html_body,
        user.email,
    )