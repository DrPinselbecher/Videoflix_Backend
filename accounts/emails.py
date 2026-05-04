from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import activation_token_generator


def send_activation_email(request, user) -> str:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = activation_token_generator.make_token(user)

    path = reverse("account-activate", kwargs={"uidb64": uidb64, "token": token})
    activation_url = request.build_absolute_uri(path)

    send_mail(
        subject="Activate your Videoflix account",
        message=f"Activate your account:\n{activation_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return token


def send_password_reset_email(request, user) -> None:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    path = reverse("password-confirm", kwargs={"uidb64": uidb64, "token": token})
    reset_url = request.build_absolute_uri(path)

    send_mail(
        subject="Reset your Videoflix password",
        message=f"Reset your password:\n{reset_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )