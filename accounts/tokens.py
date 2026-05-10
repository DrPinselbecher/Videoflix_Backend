from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    """Generate account activation tokens that become invalid after activation."""

    def _make_hash_value(self, user, timestamp):
        """Build the token hash value from user state and timestamp."""
        return f"{user.pk}{timestamp}{user.is_active}{user.password}"


activation_token_generator = ActivationTokenGenerator()