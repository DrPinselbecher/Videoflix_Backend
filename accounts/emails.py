from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import activation_token_generator


def build_frontend_url(path: str, uid: str, token: str) -> str:
    """Build a frontend URL containing uid and token query parameters."""
    query_params = urlencode({"uid": uid, "token": token})
    return f"{settings.FRONTEND_BASE_URL}/{path}?{query_params}"


def get_uidb64(user) -> str:
    """Return the base64 encoded primary key for a user."""
    return urlsafe_base64_encode(force_bytes(user.pk))


def get_logo_url() -> str:
    """Return the public logo URL used inside HTML e-mails."""
    return settings.EMAIL_LOGO_URL


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


def build_email_layout(title: str, intro: str, button_text: str, action_url: str, footer: str) -> str:
    """Build a reusable HTML e-mail layout."""
    logo_url = get_logo_url()

    return f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f5f5f5;">
        <span style="display: none; max-height: 0; overflow: hidden; color: transparent;">
            {intro}
        </span>

        <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
               style="background-color: #f5f5f5; padding: 32px 0;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
                           style="max-width: 560px; background-color: #ffffff; border-radius: 12px;
                                  padding: 32px; font-family: Arial, sans-serif; color: #222222;">
                        <tr>
                            <td align="center" style="padding-bottom: 28px;">
                                <img src="{logo_url}" alt="Videoflix" style="max-width: 240px;">
                            </td>
                        </tr>

                        <tr>
                            <td>
                                <h1 style="font-size: 24px; margin: 0 0 20px 0; color: #111111;">
                                    {title}
                                </h1>

                                <p style="font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                                    {intro}
                                </p>

                                <p style="text-align: center; margin: 32px 0;">
                                    <a href="{action_url}"
                                       style="background-color: #1f2bff; color: #ffffff;
                                              text-decoration: none; padding: 14px 28px;
                                              border-radius: 28px; font-weight: bold;
                                              display: inline-block;">
                                        {button_text}
                                    </a>
                                </p>

                                <p style="font-size: 14px; line-height: 1.6; color: #555555;">
                                    If the button does not work, copy and paste this link into your browser:
                                </p>

                                <p style="font-size: 14px; line-height: 1.6; word-break: break-all;">
                                    <a href="{action_url}" style="color: #1f2bff;">
                                        {action_url}
                                    </a>
                                </p>

                                <p style="font-size: 14px; line-height: 1.6; color: #555555;
                                          margin-top: 32px;">
                                    {footer}
                                </p>

                                <p style="font-size: 14px; line-height: 1.6; color: #555555;">
                                    Best regards,<br>
                                    Your Videoflix Team
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def build_activation_email_html(activation_url: str) -> str:
    """Build the HTML body for the account activation e-mail."""
    return build_email_layout(
        title="Activate your Videoflix account",
        intro=(
            "Thank you for registering with Videoflix. "
            "Please confirm your e-mail address to activate your account."
        ),
        button_text="Activate account",
        action_url=activation_url,
        footer="If you did not create a Videoflix account, you can safely ignore this e-mail.",
    )


def build_password_reset_email_html(reset_url: str) -> str:
    """Build the HTML body for the password reset e-mail."""
    return build_email_layout(
        title="Reset your Videoflix password",
        intro=(
            "We received a request to reset your Videoflix password. "
            "Use the button below to choose a new password."
        ),
        button_text="Reset password",
        action_url=reset_url,
        footer="If you did not request a password reset, you can safely ignore this e-mail.",
    )


def send_activation_email(user) -> str:
    """Send an account activation e-mail to the given user."""
    uid = get_uidb64(user)
    token = activation_token_generator.make_token(user)
    activation_url = build_frontend_url("pages/auth/activate.html", uid, token)

    text_body = (
        "Activate your Videoflix account\n\n"
        "Thank you for registering with Videoflix.\n"
        "Please confirm your e-mail address using the link below:\n\n"
        f"{activation_url}\n\n"
        "If you did not create a Videoflix account, you can safely ignore this e-mail.\n\n"
        "Best regards,\n"
        "Your Videoflix Team"
    )

    html_body = build_activation_email_html(activation_url)

    send_html_email(
        subject="Activate your Videoflix account",
        text_body=text_body,
        html_body=html_body,
        recipient=user.email,
    )

    return token


def send_password_reset_email(user) -> None:
    """Send a password reset e-mail to the given user."""
    uid = get_uidb64(user)
    token = default_token_generator.make_token(user)
    reset_url = build_frontend_url("pages/auth/confirm_password.html", uid, token)

    text_body = (
        "Reset your Videoflix password\n\n"
        "We received a request to reset your Videoflix password.\n"
        "Use the link below to choose a new password:\n\n"
        f"{reset_url}\n\n"
        "If you did not request a password reset, you can safely ignore this e-mail.\n\n"
        "Best regards,\n"
        "Your Videoflix Team"
    )

    html_body = build_password_reset_email_html(reset_url)

    send_html_email(
        subject="Reset your Videoflix password",
        text_body=text_body,
        html_body=html_body,
        recipient=user.email,
    )