from decimal import Decimal

from django.db import models
from django.db.models import Count, Q, Sum

from rest_framework import generics, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from orders.models import Order
from products.models import Product
from suppliers.models import Supplier

from .models import User
from .permissions import IsAdmin
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    AdminCustomerSerializer,
    ChangePasswordSerializer,
    AdminCustomerOrderSerializer,
)


# ==========================================================
# REGISTER
# ==========================================================

class RegisterView(
    generics.CreateAPIView
):

    queryset = User.objects.all()

    serializer_class = RegisterSerializer

    permission_classes = [
        AllowAny
    ]


# ==========================================================
# LOGIN
# ==========================================================

class LoginView(
    APIView
):

    permission_classes = [
        AllowAny
    ]

    def post(
        self,
        request,
    ):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            "user"
        ]

        if user.role == User.ROLE_SUPPLIER:
            try:
                supplier = user.supplier
            except Supplier.DoesNotExist:
                return Response(
                    {
                        "detail": "Supplier profile not found."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if not supplier.can_login:
                return Response(
                    {
                        "detail": "Your supplier account has not been approved yet."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # ==================================================
        # CREATE JWT TOKENS
        # ==================================================

        refresh = RefreshToken.for_user(
            user
        )

        access = refresh.access_token

        # ==================================================
        # PROFILE IMAGE
        # ==================================================

        profile_image = None

        if user.profile_image:

            profile_image = (
                request.build_absolute_uri(
                    user.profile_image.url
                )
            )

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response(

            {
                "access": str(access),

                "refresh": str(refresh),

                "user": {

                    "id": user.id,

                    "username": user.username,

                    "email": user.email,

                    "phone": user.phone,

                    "role": user.role,

                    "profile_image":
                        profile_image,

                },
            },

            status=status.HTTP_200_OK,
        )


# ==========================================================
# PROFILE
# ==========================================================

class ProfileView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = UserSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_object(
        self
    ):

        return self.request.user

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):

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

        return Response(
            {
                "message":
                    "Profile updated successfully.",

                "user":
                    serializer.data,
            }
        )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

class ChangePasswordView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
    ):

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = request.user

        # ==================================================
        # CHECK OLD PASSWORD
        # ==================================================

        if not user.check_password(
            serializer.validated_data[
                "old_password"
            ]
        ):

            return Response(

                {
                    "old_password": [
                        "Old password is incorrect."
                    ]
                },

                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # SET NEW PASSWORD
        # ==================================================

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

class LogoutView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
    ):

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

class AdminDashboardView(
    APIView
):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get(
        self,
        request,
    ):

        total_sales = (
            Order.objects.aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        total_sales = Decimal(str(total_sales)).quantize(
            Decimal("0.01")
        )

        low_stock_products = (
            Product.objects.filter(
                stock_quantity__lte=models.F("inventory__minimum_stock")
            ).count()
        )

        return Response(
            {
                "message": "Welcome Admin",
                "admin": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                },
                "stats": {
                    "customers": User.objects.filter(
                        role=User.ROLE_CUSTOMER,
                        is_active=True,
                    ).count(),
                    "suppliers": Supplier.objects.count(),
                    "delivery_riders": User.objects.filter(
                        role=User.ROLE_DELIVERY_RIDER,
                    ).count(),
                    "products": Product.objects.count(),
                    "orders": Order.objects.count(),
                    "sales": str(total_sales),
                    "pending_orders": Order.objects.filter(
                        status=Order.STATUS_PENDING,
                    ).count(),
                    "processing_orders": Order.objects.filter(
                        status=Order.STATUS_PROCESSING,
                    ).count(),
                    "delivered_orders": Order.objects.filter(
                        status=Order.STATUS_DELIVERED,
                    ).count(),
                    "low_stock_products": low_stock_products,
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminCustomerListView(generics.ListAPIView):

    serializer_class = AdminCustomerSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = User.objects.filter(
            role=User.ROLE_CUSTOMER,
        ).annotate(
            total_orders=Count("orders", distinct=True),
            total_spent=Sum("orders__total_amount"),
        ).order_by("-created_at")

        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        is_active = self.request.query_params.get("is_active")
        if is_active in {"true", "false"}:
            queryset = queryset.filter(is_active=is_active == "true")

        for customer in queryset:
            customer.latest_order_object = customer.orders.order_by(
                "-created_at"
            ).first()

        return queryset


class AdminCustomerDetailView(generics.RetrieveAPIView):

    serializer_class = AdminCustomerSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return User.objects.filter(
            role=User.ROLE_CUSTOMER,
        ).annotate(
            total_orders=Count("orders", distinct=True),
            total_spent=Sum("orders__total_amount"),
        )

    def retrieve(self, request, *args, **kwargs):
        customer = self.get_object()
        customer.latest_order_object = customer.orders.order_by(
            "-created_at"
        ).first()
        data = self.get_serializer(customer).data
        data["orders"] = AdminCustomerOrderSerializer(
            customer.orders.order_by("-created_at"),
            many=True,
        ).data
        return Response(data)


class AdminCustomerStatusView(generics.UpdateAPIView):

    serializer_class = AdminCustomerSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ["patch"]

    def get_queryset(self):
        return User.objects.filter(
            role=User.ROLE_CUSTOMER,
        ).annotate(
            total_orders=Count("orders", distinct=True),
            total_spent=Sum("orders__total_amount"),
        )
    
