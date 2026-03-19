"""
Serializers handle:
1. Input validation (is the data correct?)
2. Transformation (convert raw data ↔ Python objects)

We never put business logic here — that goes in services.
Serializers only validate and transform.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration input validation.
    password is write_only — never returned in responses.
    password_confirm is extra validation — not a model field.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role'
        ]
        extra_kwargs = {
            'role': {'required': False}  # defaults to 'student'
        }

    def validate_email(self, value):
        """Check email is not already registered."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Email already registered.')
        return value.lower()

    def validate(self, attrs):
        """Cross-field validation — passwords must match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs


class LoginSerializer(serializers.Serializer):
    """
    Login only needs email + password.
    Not a ModelSerializer because we're not creating anything.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Returns safe user data in responses.
    Never exposes password or internal flags.
    """
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'bio', 'avatar',
            'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    """Handles authenticated password changes."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({
                'confirm_new_password': 'New passwords do not match.'
            })
        return attrs