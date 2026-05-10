"""URL routes for authentication and account management endpoints."""

from django.urls import path

from .views import (
    ActivateView,
    CookieTokenRefreshView,
    CsrfTokenView,
    LoginView,
    LogoutView,
    PasswordConfirmView,
    PasswordResetView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="account-register"),
    path("activate/<uidb64>/<token>/", ActivateView.as_view(), name="account-activate"),
    path("login/", LoginView.as_view(), name="account-login"),
    path("logout/", LogoutView.as_view(), name="account-logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("csrf/", CsrfTokenView.as_view(), name="csrf-cookie"),
    path("password_reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password_confirm/<uidb64>/<token>/",
        PasswordConfirmView.as_view(),
        name="password-confirm",
    ),
]
