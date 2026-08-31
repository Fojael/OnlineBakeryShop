from django.db import transaction

from rest_framework import generics
from rest_framework import status

from rest_framework.response import Response

from .models import Supplier

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

from accounts.permissions import (
    IsSupplier,
)

from rest_framework.exceptions import NotFound

from .services import (
    SupplierDashboardService,
)

from .serializers import (
    SupplierRegisterSerializer,
    SupplierProfileSerializer,
    SupplierDashboardSerializer,
)

# ==========================================================
# SUPPLIER REGISTRATION
# ==========================================================

class SupplierRegisterView(
    generics.CreateAPIView,
):
    """
    Public supplier registration.

    Workflow

    Register
        ↓
    Create User(role=SUPPLIER)
        ↓
    User.is_active = False
        ↓
    Supplier.is_approved = False
        ↓
    Admin approval required
        ↓
    Supplier can login
    """

    serializer_class = (
        SupplierRegisterSerializer
    )

    permission_classes = [
        AllowAny,
    ]

    queryset = Supplier.objects.none()

    @transaction.atomic
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        supplier = serializer.save()

        return Response(

            {

                "success": True,

                "message": (
                    "Supplier registration submitted successfully. "
                    "Your account is awaiting administrator approval."
                ),

                "supplier": {

                    "id": supplier.id,

                    "name": supplier.name,

                    "company": supplier.company,

                    "email": supplier.email,

                    "phone": supplier.phone,

                    "is_active": supplier.is_active,

                    "is_approved": supplier.is_approved,

                    "created_at": supplier.created_at,

                },

            },

            status=status.HTTP_201_CREATED,

        )
        
# ==========================================================
# SUPPLIER PROFILE
# ==========================================================

class SupplierProfileView(
    generics.RetrieveUpdateAPIView,
):
    """
    Retrieve and update the authenticated supplier profile.

    Only the logged-in supplier can access this endpoint.
    """

    serializer_class = (
        SupplierProfileSerializer
    )

    permission_classes = [

        IsAuthenticated,

        IsSupplier,

    ]

    http_method_names = [

        "get",

        "put",

        "patch",

    ]

    def get_object(self):

        try:

            return (

                Supplier.objects

                .select_related("user")

                .get(

                    user=self.request.user,

                )

            )

        except Supplier.DoesNotExist:

            from rest_framework.exceptions import NotFound

            raise NotFound(

                "Supplier profile does not exist."

            )

    @transaction.atomic
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):

        partial = kwargs.pop(
            "partial",
            False,
        )

        supplier = self.get_object()

        serializer = self.get_serializer(

            supplier,

            data=request.data,

            partial=partial,

        )

        serializer.is_valid(

            raise_exception=True,

        )

        serializer.save()

        return Response(

            {

                "success": True,

                "message": (
                    "Supplier profile updated successfully."
                ),

                "supplier": serializer.data,

            },

            status=status.HTTP_200_OK,

        )
        
# ==========================================================
# SUPPLIER DASHBOARD
# ==========================================================

class SupplierDashboardView(
    generics.RetrieveAPIView,
):
    """
    Supplier dashboard.

    Returns dashboard statistics and products
    for the authenticated supplier only.
    """

    serializer_class = (
        SupplierDashboardSerializer
    )

    permission_classes = [

        IsAuthenticated,

        IsSupplier,

    ]

    queryset = (

        Supplier.objects

        .select_related(
            "user",
        )

        .prefetch_related(
            "products",
            "products__inventory",
            "products__category",
        )

    )

    def get_object(self):

        try:

            return self.get_queryset().get(

                user=self.request.user,

            )

        except Supplier.DoesNotExist:

            raise NotFound(

                "Supplier profile does not exist."

            )

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):

        supplier = self.get_object()

        dashboard = SupplierDashboardService(
            supplier
        )

        serializer = self.get_serializer(

            supplier,

            context={

                "request": request,

            },

        )

        data = serializer.data

        data.update(

            {

                "total_products":
                    dashboard.total_products(),

                "available_products":
                    dashboard.available_products(),

                "low_stock":
                    dashboard.low_stock_products(),

                "out_of_stock":
                    dashboard.out_of_stock_products(),

                "total_stock":
                    dashboard.total_stock(),

            }

        )

        return Response(

            {

                "success": True,

                "dashboard": data,

            },

            status=status.HTTP_200_OK,

        )