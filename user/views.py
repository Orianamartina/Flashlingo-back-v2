from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from game.utils import setup_game_sessions

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    LogoutRequestSerializer,
    RegisterSerializer,
)


class RegisterView(APIView):
    permission_classes = []

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="User registered successfully"),
            400: OpenApiResponse(description="Bad Request"),
        },
        tags=["Authentication"],
        summary="Register a new user",
        description="Creates a new user with a username, password, and email.",
    )
    @transaction.atomic
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        missing_fields = []
        if not username:
            missing_fields.append("username")
        if not password:
            missing_fields.append("password")
        if not email:
            missing_fields.append("email")

        if missing_fields:
            error_message = f"Missing fields: {', '.join(missing_fields)}"
            return JsonResponse(
                {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        setup_game_sessions(user)
        return JsonResponse(
            {"message": "User registered successfully"}, status=status.HTTP_201_CREATED
        )


class LoginView(TokenObtainPairView):
    @extend_schema(
        request=LoginRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="Login successful", response=LoginResponseSerializer
            ),
            400: OpenApiResponse(description="Invalid credentials"),
        },
        tags=["Authentication"],
        summary="Login a user",
        description="Authenticate a user and return JWT tokens.",
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            response = super().post(request, *args, **kwargs)
            response.data["user"] = {"id": user.id}
            return response
        return JsonResponse(
            {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutRequestSerializer,
        responses={
            200: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Bad Request"),
        },
        tags=["Authentication"],
        summary="Logout a user",
        description="Blacklist the provided refresh token to log out the user.",
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return JsonResponse(
                {"message": "Logout successful"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except InvalidToken:
            return Response(
                {
                    "detail": "Refresh token is expired.",
                    "code": "refresh_token_expired",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
