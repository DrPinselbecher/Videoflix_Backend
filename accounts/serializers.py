from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()

GENERIC_AUTH_ERROR = "Bitte überprüfe deine Eingaben und versuche es erneut."


def validate_password_or_raise_generic(password: str) -> None:
    try:
        validate_password(password)
    except DjangoValidationError:
        raise serializers.ValidationError(GENERIC_AUTH_ERROR)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value: str) -> str:
        return value.lower()

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(GENERIC_AUTH_ERROR)

        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(GENERIC_AUTH_ERROR)

        validate_password_or_raise_generic(attrs["password"])
        return attrs

    def create(self, validated_data):
        email = validated_data["email"]

        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            is_active=False,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].lower()
        password = attrs["password"]

        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password) or not user.is_active:
            raise serializers.ValidationError(GENERIC_AUTH_ERROR)

        attrs["user"] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(GENERIC_AUTH_ERROR)

        validate_password_or_raise_generic(attrs["new_password"])
        return attrs