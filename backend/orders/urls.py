from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,
    AdminOrderListView,
    AdminOrderUpdateView,
)


urlpatterns = [
    # =========================================================
    # ADMIN ORDERS
    # =========================================================

    path(
        "admin/",
        AdminOrderListView.as_view(),
        name="admin-orders",
    ),

    path(
        "admin/<int:pk>/",
        AdminOrderUpdateView.as_view(),
        name="admin-order-update",
    ),

    # =========================================================
    # CUSTOMER ORDERS
    # =========================================================

    path(
        "",
        OrderListCreateView.as_view(),
        name="orders",
    ),

    path(
        "<int:pk>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    path(
        "<int:pk>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),
]