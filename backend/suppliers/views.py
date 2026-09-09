from django.db import transaction
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from accounts.permissions import IsAdmin, IsSupplier
from inventory.services import receive_replenishment
from .services import (
    notify_replenishment_created,
    notify_replenishment_status,
)

from .models import ReplenishmentRequest, Supplier
from .models import (
    ReplenishmentRequest,
    ReplenishmentStatusHistory,
    Supplier,
)
from .serializers import (
    ReplenishmentRequestSerializer,
    ReplenishmentStatusSerializer,
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
        "get",
        "patch",
        "post",
    ]

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        return self.update(
            request,
            *args,
            **kwargs,
        )

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
        "get",
        "patch",
        "post",
    ]

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        return self.update(
            request,
            *args,
            **kwargs,
        )

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


class ReplenishmentRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        queryset = ReplenishmentRequest.objects.select_related(
            "supplier",
            "product",
            "created_by",
        )

        if request.user.role == "ADMIN":
            return queryset

        if request.user.role == "SUPPLIER":
            if not IsSupplier().has_permission(request, self):
                return queryset.none()

            return queryset.filter(
                supplier__user=request.user,
            )

        return queryset.none()

    def get(self, request):
        if request.user.role not in ["ADMIN", "SUPPLIER"]:
            return Response(
                {"detail": "Supplier access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            request.user.role == "SUPPLIER"
            and not IsSupplier().has_permission(request, self)
        ):
            return Response(
                {"detail": "Active supplier access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReplenishmentRequestSerializer(
            self.get_queryset(request),
            many=True,
        )
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        if not IsAdmin().has_permission(request, self):
            return Response(
                {"detail": "Admin permission required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReplenishmentRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        replenishment_request = serializer.save(
            created_by=request.user,
        )
        notify_replenishment_created(replenishment_request)

        return Response(
            ReplenishmentRequestSerializer(
                replenishment_request,
            ).data,
            status=status.HTTP_201_CREATED,
        )


class ReplenishmentRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, request_id):
        queryset = ReplenishmentRequest.objects.select_related(
            "supplier",
            "product",
            "created_by",
        )

        if request.user.role == "ADMIN":
            return get_object_or_404(queryset, id=request_id)

        if request.user.role == "SUPPLIER":
            if not IsSupplier().has_permission(request, self):
                raise PermissionDenied(
                    "Active supplier access required."
                )

            return get_object_or_404(
                queryset,
                id=request_id,
                supplier__user=request.user,
            )

        raise PermissionDenied("Supplier access required.")

    def get(self, request, request_id):
        replenishment_request = self.get_object(
            request,
            request_id,
        )
        return Response(
            ReplenishmentRequestSerializer(
                replenishment_request,
            ).data,
        )


class ReplenishmentStatusUpdateView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsSupplier,
    ]

    @transaction.atomic
    def patch(self, request, request_id):
        replenishment_request = get_object_or_404(
            ReplenishmentRequest.objects.select_for_update(),
            id=request_id,
            supplier__user=request.user,
        )

        serializer = ReplenishmentStatusSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        previous_status = replenishment_request.status

        transitions = {
            ReplenishmentRequest.STATUS_PENDING: [
                ReplenishmentRequest.STATUS_PROCESSING,
            ],
            ReplenishmentRequest.STATUS_PROCESSING: [
                ReplenishmentRequest.STATUS_READY,
            ],
            ReplenishmentRequest.STATUS_READY: [
                ReplenishmentRequest.STATUS_DELIVERED,
            ],
            ReplenishmentRequest.STATUS_DELIVERED: [],
        }

        allowed_next = transitions.get(
            replenishment_request.status,
            [],
        )

        if new_status not in allowed_next:
            return Response(
                {
                    "detail": (
                        "Invalid replenishment status transition: "
                        f"{replenishment_request.status} -> "
                        f"{new_status}."
                    ),
                    "current_status": replenishment_request.status,
                    "allowed_next_statuses": allowed_next,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        replenishment_request.status = new_status
        replenishment_request.save(
            update_fields=["status", "updated_at"],
        )

        if new_status == ReplenishmentRequest.STATUS_DELIVERED:
            replenishment_request = receive_replenishment(
                replenishment_request,
            )

        ReplenishmentStatusHistory.objects.create(
            replenishment_request=replenishment_request,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=request.user,
        )

        notify_replenishment_status(
            replenishment_request,
            new_status,
        )

        return Response(
            ReplenishmentRequestSerializer(
                replenishment_request,
            ).data,
        )
        
        
