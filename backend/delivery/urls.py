from django.urls import path

from .views import (
    AdminCreateDeliveryView,
    DeliveryDashboardView,
    DeliveryAvailableListView,
    MyDeliveryListView,
    AcceptDeliveryView,
    DeliveryDetailView,
    DeliveryStatusUpdateView,
)


app_name = "delivery"


urlpatterns = [

    # ======================================================
    # ADMIN
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
    # AVAILABLE DELIVERIES
    # ======================================================

    path(
        "available/",
        DeliveryAvailableListView.as_view(),
        name="delivery-available",
    ),

    # ======================================================
    # MY DELIVERIES
    # ======================================================

    path(
        "my/",
        MyDeliveryListView.as_view(),
        name="my-deliveries",
    ),

    # ======================================================
    # ACCEPT DELIVERY
    # ======================================================

    path(
        "<int:delivery_id>/accept/",
        AcceptDeliveryView.as_view(),
        name="accept-delivery",
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
    # UPDATE DELIVERY STATUS
    # ======================================================

    path(
        "<int:delivery_id>/status/",
        DeliveryStatusUpdateView.as_view(),
        name="delivery-status-update",
    ),
]

