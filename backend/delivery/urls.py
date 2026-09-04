from django.urls import path

from .views import (
    AdminCreateDeliveryView,
    DeliveryDashboardView,
    MyDeliveryListView,
    DeliveryDetailView,
    DeliveryStatusUpdateView,
)


app_name = "delivery"


urlpatterns = [

    # ======================================================
    # ADMIN
    # Assign a specific rider to a Ready order
    # ======================================================

    path(
        "admin/orders/<int:order_id>/create/",
        AdminCreateDeliveryView.as_view(),
        name="admin-create-delivery",
    ),

    # ======================================================
    # DELIVERY RIDER DASHBOARD
    # ======================================================

    path(
        "dashboard/",
        DeliveryDashboardView.as_view(),
        name="delivery-dashboard",
    ),

    # ======================================================
    # RIDER'S ASSIGNED DELIVERIES
    # ======================================================

    path(
        "my/",
        MyDeliveryListView.as_view(),
        name="my-deliveries",
    ),

    # ======================================================
    # DELIVERY DETAIL
    # ======================================================

    path(
        "<int:delivery_id>/",
        DeliveryDetailView.as_view(),
        name="delivery-detail",
    ),

    # ======================================================
    # RIDER STATUS UPDATE
    # ======================================================

    path(
        "<int:delivery_id>/status/",
        DeliveryStatusUpdateView.as_view(),
        name="delivery-status-update",
    ),
]
