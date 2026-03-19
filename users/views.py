from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)
from common.services.auth_service import register_user, login_user, change_password


@swagger_auto_schema(
    method="post",
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response("Registration successful", UserProfileSerializer),
        400: "Validation error",
    },
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": True, "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    result = register_user(serializer.validated_data)
    return Response(
        {
            "error": False,
            "message": "Registration successful.",
            "data": {
                "user": UserProfileSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
        },
        status=status.HTTP_201_CREATED,
    )


@swagger_auto_schema(
    method="post",
    request_body=LoginSerializer,
    responses={200: "Login successful with tokens", 400: "Invalid credentials"},
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login with email and password.

    Returns JWT access token (expires in 60 min)
    and refresh token (expires in 7 days).
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": True, "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    result = login_user(
        email=serializer.validated_data["email"],
        password=serializer.validated_data["password"],
    )
    return Response(
        {
            "error": False,
            "message": "Login successful.",
            "data": {
                "user": UserProfileSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
        },
        status=status.HTTP_200_OK,
    )


@swagger_auto_schema(
    method="get", responses={200: UserProfileSerializer}, tags=["Authentication"]
)
@swagger_auto_schema(
    method="patch",
    request_body=UserProfileSerializer,
    responses={200: UserProfileSerializer},
    tags=["Authentication"],
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    GET  → Returns current user profile.
    PATCH → Updates first_name, last_name, bio fields.
    Requires Bearer token authentication.
    """
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user)
        return Response({"error": False, "data": serializer.data})

    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
            {"error": True, "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.save()
    return Response(
        {"error": False, "message": "Profile updated.", "data": serializer.data}
    )


@swagger_auto_schema(
    method="post",
    request_body=ChangePasswordSerializer,
    responses={200: "Password changed", 400: "Validation error"},
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):

    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": True, "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    change_password(
        user=request.user,
        old_password=serializer.validated_data["old_password"],
        new_password=serializer.validated_data["new_password"],
    )
    return Response({"error": False, "message": "Password changed successfully."})
