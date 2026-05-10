from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers

User = get_user_model()

GENERIC_AUTH_ERROR = "Bitte überprüfe deine Eingaben und versuche es erneut."


def validate_password_or_raise_generic(password: str) -> None:
    """Validate a password and raise a generic API error if invalid."""
    try:
        validate_password(password)
    except DjangoValidationError as error:
        raise serializers.ValidationError(GENERIC_AUTH_ERROR) from error


class RegisterSerializer(serializers.Serializer):
    """Validate registration data and create inactive user accounts."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value: str) -> str:
        """Normalize the submitted e-mail address."""
        return value.lower()

    def validate(self, attrs):
        """Validate unique e-mail, matching passwords and password strength."""
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(GENERIC_AUTH_ERROR)

        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(GENERIC_AUTH_ERROR)

        validate_password_or_raise_generic(attrs["password"])
        return attrs

    def create(self, validated_data):
        """Create an inactive user account with e-mail as username."""
        email = validated_data["email"]

        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            is_active=False,
        )


class LoginSerializer(serializers.Serializer):
    """Validate login credentials and return the authenticated user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate e-mail, password and active account status."""
        email = attrs["email"].lower()
        password = attrs["password"]

        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password) or not user.is_active:
            raise AuthenticationFailed(GENERIC_AUTH_ERROR)

        attrs["user"] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Validate password reset request data."""

    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate password confirmation data for password reset."""

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate matching passwords and password strength."""
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(GENERIC_AUTH_ERROR)

        validate_password_or_raise_generic(attrs["new_password"])
        return attrs
