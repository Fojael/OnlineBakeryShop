from django.db import transaction

from rest_framework import generics
from rest_framework import status

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin

from .models import Supplier

from .serializers import (
    SupplierSerializer,
    SupplierRegisterSerializer,
)


# ==========================================================
# SUPPLIER REGISTER
# ==========================================================

class SupplierRegisterView(
    generics.CreateAPIView
):

    queryset = Supplier.objects.all()

    serializer_class = (
        SupplierRegisterSerializer
    )

    permission_classes = [
        AllowAny,
    ]


# ==========================================================
# ADMIN
# SUPPLIER LIST + CREATE
# ==========================================================

class SupplierListCreateView(
    generics.ListCreateAPIView
):

    queryset = (
        Supplier.objects
        .select_related("user")
        .order_by("-created_at")
    )

    serializer_class = (
        SupplierSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]


# ==========================================================
# ADMIN
# SUPPLIER DETAILS
# ==========================================================

class SupplierRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = (
        Supplier.objects
        .select_related("user")
        .order_by("-created_at")
    )

    serializer_class = (
        SupplierSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @transaction.atomic
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        supplier = (
            Supplier.objects
            .select_for_update()
            .select_related("user")
            .get(
                pk=kwargs["pk"]
            )
        )

        user = supplier.user

        if user:

            # Because Supplier.user uses
            # on_delete=models.CASCADE
            # deleting the user will automatically
            # delete the supplier.
            user.delete()

        else:

            supplier.delete()

        return Response(
            {
                "message":
                "Supplier deleted successfully."
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN
# ACTIVATE SUPPLIER
# ==========================================================

class SupplierActivateView(
    APIView
):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def patch(
        self,
        request,
        pk,
    ):

        try:

            supplier = (
                Supplier.objects
                .select_related("user")
                .get(
                    pk=pk
                )
            )

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Supplier not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if supplier.user is None:

            return Response(
                {
                    "detail":
                    "Supplier account not found."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        supplier.user.is_active = True

        supplier.user.save(
            update_fields=[
                "is_active",
            ]
        )

        return Response(
            {
                "message":
                "Supplier activated successfully."
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ADMIN
# DEACTIVATE SUPPLIER
# ==========================================================

class SupplierDeactivateView(
    APIView
):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def patch(
        self,
        request,
        pk,
    ):

        try:

            supplier = (
                Supplier.objects
                .select_related("user")
                .get(
                    pk=pk
                )
            )

        except Supplier.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Supplier not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if supplier.user is None:

            return Response(
                {
                    "detail":
                    "Supplier account not found."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        supplier.user.is_active = False

        supplier.user.save(
            update_fields=[
                "is_active",
            ]
        )

        return Response(
            {
                "message":
                "Supplier deactivated successfully."
            },
            status=status.HTTP_200_OK,
        )