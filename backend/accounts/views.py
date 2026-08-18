from rest_framework import generics, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdmin
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)


# ==========================================================
# REGISTER
# ==========================================================

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# ==========================================================
# LOGIN
# ==========================================================

class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response({

            "access": str(refresh.access_token),

            "refresh": str(refresh),

            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "profile_image": (
                    request.build_absolute_uri(
                        user.profile_image.url
                    )
                    if user.profile_image
                    else None
                ),
            }

        })


# ==========================================================
# PROFILE
# ==========================================================

class ProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):

        user = self.get_object()

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message":
                "Profile updated successfully.",
            "user":
                serializer.data,
        })


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = request.user

        if not user.check_password(
            serializer.validated_data[
                "old_password"
            ]
        ):
            return Response(
                {
                    "old_password":
                        [
                            "Old password is incorrect."
                        ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(
            serializer.validated_data[
                "new_password"
            ]
        )

        user.save()

        return Response(
            {
                "message":
                    "Password changed successfully."
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# LOGOUT
# ==========================================================

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get(
            "refresh"
        )

        if not refresh_token:
            return Response(
                {
                    "detail":
                        "Refresh token is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            token = RefreshToken(
                refresh_token
            )

            token.blacklist()

            return Response(
                {
                    "message":
                        "Logout successful."
                },
                status=status.HTTP_205_RESET_CONTENT,
            )

        except Exception:

            return Response(
                {
                    "detail":
                        "Invalid or expired refresh token."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

class AdminDashboardView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get(self, request):

        return Response({

            "message":
                "Welcome Admin",

            "admin": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            }

        })