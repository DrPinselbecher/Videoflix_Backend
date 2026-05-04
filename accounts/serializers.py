from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value: str) -> str:
        email = value.lower()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists.")

        return email

    def validate(self, attrs):
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError({"confirmed_password": "Passwords do not match."})

        validate_password(attrs["password"])

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

        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Account is not activated.")

        attrs["user"] = user

        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        validate_password(attrs["new_password"])

        return attrs