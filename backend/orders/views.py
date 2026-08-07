from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer

from accounts.permissions import IsAdmin


# =========================================================
# CUSTOMER
# GET  /api/orders/
# POST /api/orders/
# =========================================================

class OrderListCreateView(generics.ListCreateAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Order.objects.filter(
            customer=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):

        serializer.save(
            customer=self.request.user,
            status="Pending",
        )


# =========================================================
# CUSTOMER
# GET /api/orders/<id>/
# =========================================================

class OrderDetailView(generics.RetrieveAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Order.objects.filter(
            customer=self.request.user
        )


# =========================================================
# CUSTOMER
# PATCH /api/orders/<id>/cancel/
#
# Pending -> Cancelled
#
# Order is NOT deleted.
# =========================================================

class OrderCancelView(generics.UpdateAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Order.objects.filter(
            customer=self.request.user
        )

    def update(self, request, *args, **kwargs):

        order = self.get_object()

        if order.status != "Pending":

            return Response(
                {
                    "detail": (
                        "Only pending orders "
                        "can be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = "Cancelled"

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        serializer = self.get_serializer(order)

        return Response(
            {
                "message": (
                    "Order cancelled successfully."
                ),
                "order": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# ADMIN
# GET /api/orders/admin/
# =========================================================

class AdminOrderListView(generics.ListAPIView):

    queryset = Order.objects.all().order_by(
        "-created_at"
    )

    serializer_class = OrderSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]


# =========================================================
# ADMIN
# GET  /api/orders/admin/<id>/
# PUT  /api/orders/admin/<id>/
# PATCH /api/orders/admin/<id>/
# =========================================================

class AdminOrderUpdateView(
    generics.RetrieveUpdateAPIView
):

    queryset = Order.objects.all()

    serializer_class = OrderSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def update(
        self,
        request,
        *args,
        **kwargs
    ):

        order = self.get_object()

        serializer = self.get_serializer(
            order,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Order updated successfully."
                ),
                "order": serializer.data,
            },
            status=status.HTTP_200_OK,
        )