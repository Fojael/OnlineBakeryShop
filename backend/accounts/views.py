from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import User
from .serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChangePasswordSerializer
from .permissions import IsAdmin


from accounts.permissions import IsAdmin


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
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
    "role": user.role,
    "profile_image": (
        user.profile_image.url
        if user.profile_image
        else None
    ),
    }

        })
class ProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            refresh_token = request.data["refresh"]

            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )

        except Exception:

            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )
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
            serializer.validated_data["old_password"]
        ):
            return Response(
                {"error":"Old password incorrect"},
                status=400
            )

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save()

        return Response(
            {"message":"Password changed successfully"}
        )
class AdminDashboardView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            "message": "Welcome Admin"
        })
