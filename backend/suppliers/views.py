from django.db import transaction

from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsSupplier

from .models import Supplier
from .serializers import (
    SupplierRegisterSerializer,
    SupplierSerializer,
    SupplierProfileSerializer,
)


# ==========================================================
# SUPPLIER REGISTRATION
# ==========================================================

class SupplierRegisterView(
    generics.CreateAPIView
):
    """
    Public supplier registration.

    Workflow:

        Register
            ↓
        Create User
            ↓
        role = SUPPLIER
            ↓
        User.is_active = False
            ↓
        Supplier.is_approved = False
            ↓
        Admin approval
            ↓
        Supplier can login
    """

    serializer_class = SupplierRegisterSerializer

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
# ADMIN - SUPPLIER LIST + CREATE
# ==========================================================

class SupplierListCreateView(
    generics.ListCreateAPIView
):
    """
    Admin supplier management.

    GET:
        List all suppliers.

    POST:
        Create a supplier manually from admin/API.
    """

    serializer_class = SupplierSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    queryset = (
        Supplier.objects
        .select_related(
            "user",
            "approved_by",
        )
        .prefetch_related(
            "products",
        )
        .all()
    )

    def get_queryset(self):

        queryset = super().get_queryset()

        return queryset.order_by(
            "-created_at"
        )


# ==========================================================
# ADMIN - SUPPLIER DETAIL
# ==========================================================

class SupplierRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Admin supplier detail management.

    GET:
        Get one supplier.

    PUT:
        Update supplier.

    PATCH:
        Partially update supplier.

    DELETE:
        Delete supplier.
    """

    serializer_class = SupplierSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    queryset = (
        Supplier.objects
        .select_related(
            "user",
            "approved_by",
        )
        .all()
    )

    def get_object(self):

        try:

            return (
                self.get_queryset()
                .get(
                    pk=self.kwargs["pk"],
                )
            )

        except Supplier.DoesNotExist:

            raise NotFound(
                "Supplier does not exist."
            )


# ==========================================================
# ADMIN - ACTIVATE SUPPLIER
# ==========================================================

class SupplierActivateView(
    generics.UpdateAPIView
):
    """
    Activate a supplier.

    Both Supplier.is_active and
    User.is_active are updated.
    """

    serializer_class = SupplierSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    queryset = Supplier.objects.select_related(
        "user",
    )

    http_method_names = [
        "patch",
        "post",
    ]

    @transaction.atomic
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):

        supplier = self.get_object()

        supplier.is_active = True

        supplier.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        if supplier.user:

            supplier.user.is_active = True

            supplier.user.save(
                update_fields=[
                    "is_active",
                ]
            )

        serializer = self.get_serializer(
            supplier,
        )

        return Response(
            {
                "success": True,

                "message": (
                    "Supplier activated successfully."
                ),

                "supplier": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN - DEACTIVATE SUPPLIER
# ==========================================================

class SupplierDeactivateView(
    generics.UpdateAPIView
):
    """
    Deactivate a supplier.

    Both Supplier.is_active and
    User.is_active are updated.
    """

    serializer_class = SupplierSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    queryset = Supplier.objects.select_related(
        "user",
    )

    http_method_names = [
        "patch",
        "post",
    ]

    @transaction.atomic
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):

        supplier = self.get_object()

        supplier.is_active = False

        supplier.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        if supplier.user:

            supplier.user.is_active = False

            supplier.user.save(
                update_fields=[
                    "is_active",
                ]
            )

        serializer = self.get_serializer(
            supplier,
        )

        return Response(
            {
                "success": True,

                "message": (
                    "Supplier deactivated successfully."
                ),

                "supplier": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SUPPLIER PROFILE
# ==========================================================

class SupplierProfileView(
    generics.RetrieveUpdateAPIView
):
    """
    Retrieve and update the authenticated
    supplier profile.

    Only the logged-in supplier can access
    this endpoint.
    """

    serializer_class = SupplierProfileSerializer

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
                .select_related(
                    "user",
                )
                .get(
                    user=self.request.user,
                )
            )

        except Supplier.DoesNotExist:

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