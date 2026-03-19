"""
Auth Service — ALL business logic lives here.

Why a service layer?
- Views should only handle HTTP (request in, response out)
- If you need to reuse logic (e.g., register via admin panel too),
  you call the service, not duplicate view logic
- Much easier to unit test services in isolation
"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers as drf_serializers

User = get_user_model()


def register_user(validated_data: dict) -> dict:
    """
    Creates a new user and returns tokens immediately.
    User shouldn't need to login again right after registering.

    Args:
        validated_data: cleaned data from RegisterSerializer

    Returns:
        dict with user object and JWT tokens
    """
    # Remove confirm field — not a model field
    validated_data.pop('password_confirm')
    password = validated_data.pop('password')

    user = User.objects.create_user(
        password=password,
        **validated_data
    )

    tokens = _generate_tokens(user)

    return {
        'user': user,
        'tokens': tokens
    }


def login_user(email: str, password: str) -> dict:
    """
    Authenticates user credentials and returns JWT tokens.

    authenticate() checks:
    1. Does this email exist?
    2. Does the password match the hash?
    3. Is the user active?

    Returns:
        dict with user and tokens, or raises ValidationError
    """
    user = authenticate(username=email, password=password)

    if not user:
        raise drf_serializers.ValidationError({
            'detail': 'Invalid email or password.'
        })

    if not user.is_active:
        raise drf_serializers.ValidationError({
            'detail': 'Account is disabled. Contact support.'
        })

    tokens = _generate_tokens(user)

    return {
        'user': user,
        'tokens': tokens
    }


def change_password(user, old_password: str, new_password: str) -> None:
    """
    Verifies old password then sets new one.

    Args:
        user: authenticated User instance
        old_password: must match current password
        new_password: new password to set
    """
    if not user.check_password(old_password):
        raise drf_serializers.ValidationError({
            'old_password': 'Current password is incorrect.'
        })
    user.set_password(new_password)
    user.save(update_fields=['password', 'updated_at'])


def _generate_tokens(user) -> dict:
    """
    Private helper — generates JWT access + refresh token pair.
    Prefixed with _ to signal 'internal use only'.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }