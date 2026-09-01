from django.db import transaction
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsSupplier

from .models import Supplier
from .serializers import (
    SupplierCreateSerializer,
    SupplierSerializer,
    SupplierProfileSerializer,
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

    def get_serializer_class(self):

        if self.request.method == "POST":
            return SupplierCreateSerializer

        return SupplierSerializer


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
        supplier.is_approved = True
        supplier.approved_at = timezone.now()
        supplier.approved_by = request.user

        supplier.save(
            update_fields=[
                "is_active",
                "is_approved",
                "approved_at",
                "approved_by",
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
        supplier.is_approved = False
        supplier.approved_at = None
        supplier.approved_by = None

        supplier.save(
            update_fields=[
                "is_active",
                "is_approved",
                "approved_at",
                "approved_by",
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