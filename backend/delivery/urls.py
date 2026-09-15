from django.urls import path

from .views import (
    AdminCreateDeliveryView,
    DeliveryDashboardView,
    MyDeliveryListView,
    DeliveryDetailView,
    DeliveryOTPRequestView,
    DeliveryOTPVerifyView,
    DeliveryStatusUpdateView,
)

app_name = "delivery"


urlpatterns = [
    # ==========================================================
    # ADMIN
    # ==========================================================

    # Admin assigns a specific delivery rider to a Ready order.
    #
    # POST:
    # /api/delivery/admin/orders/<order_id>/create/
    #
    # Body:
    # {
    #     "rider_id": 5
    # }
    path(
        "admin/orders/<int:order_id>/create/",
        AdminCreateDeliveryView.as_view(),
        name="admin-create-delivery",
    ),

    # ==========================================================
    # RIDER DASHBOARD
    # ==========================================================

    path(
        "dashboard/",
        DeliveryDashboardView.as_view(),
        name="delivery-dashboard",
    ),

    # ==========================================================
    # RIDER'S OWN DELIVERIES
    # ==========================================================

    path(
        "my/",
        MyDeliveryListView.as_view(),
        name="my-deliveries",
    ),

    # ==========================================================
    # DELIVERY DETAILS
    # ==========================================================

    path(
        "<int:delivery_id>/",
        DeliveryDetailView.as_view(),
        name="delivery-detail",
    ),

    # ==========================================================
    # RIDER STATUS UPDATE
    # ==========================================================

    path(
        "<int:delivery_id>/status/",
        DeliveryStatusUpdateView.as_view(),
        name="delivery-status-update",
    ),

    path(
        "<int:delivery_id>/request-otp/",
        DeliveryOTPRequestView.as_view(),
        name="request-otp",
    ),

    path(
        "<int:delivery_id>/verify-otp/",
        DeliveryOTPVerifyView.as_view(),
        name="verify-otp",
    ),
]

