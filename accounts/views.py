from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

from .emails import send_activation_email, send_password_reset_email
from .serializers import (
    GENERIC_AUTH_ERROR,
    LoginSerializer,
    PasswordConfirmSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
)
from .services import (
    activate_user,
    blacklist_refresh_token,
    get_active_user_by_email,
    get_refreshed_tokens,
    get_tokens_for_user,
    is_valid_password_reset_token,
    update_user_password,
)
from .utils import (
    delete_auth_cookies,
    get_refresh_token_from_request,
    get_user_from_uidb64,
    set_auth_cookies,
)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        send_activation_email(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uidb64: str, token: str):
        user = get_user_from_uidb64(uidb64)

        if user is None or not activate_user(user, token):
            return Response(
                {"detail": GENERIC_AUTH_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Account successfully activated."})


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        access_token, refresh_token = get_tokens_for_user(user)

        response = Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.email,
                },
            }
        )

        set_auth_cookies(response, access_token, refresh_token)
        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = get_refresh_token_from_request(request)

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            blacklist_refresh_token(refresh_token)
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response({"detail": "Logout successful."})
        delete_auth_cookies(response)
        return response


class CookieTokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = get_refresh_token_from_request(request)

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            access_token, new_refresh_token = get_refreshed_tokens(refresh_token)
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response({"detail": "Token refreshed"})
        set_auth_cookies(response, access_token, new_refresh_token)
        return response


class PasswordResetView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_active_user_by_email(serializer.validated_data["email"])

        if user is not None:
            send_password_reset_email(user)

        return Response(
            {"detail": "Falls ein aktives Konto existiert, wurde eine E-Mail versendet."}
        )


class PasswordConfirmView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, uidb64: str, token: str):
        user = get_user_from_uidb64(uidb64)

        if not is_valid_password_reset_token(user, token):
            return Response(
                {"detail": GENERIC_AUTH_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_user_password(user, serializer.validated_data["new_password"])
        return Response({"detail": "Your password has been successfully reset."})