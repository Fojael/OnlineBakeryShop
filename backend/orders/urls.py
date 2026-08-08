from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,
    AdminOrderListView,
    AdminOrderUpdateView,
)


urlpatterns = [
    # Customer orders
    path(
        "",
        OrderListCreateView.as_view(),
        name="orders",
    ),

    # Customer single order
    path(
        "<int:pk>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    # Customer cancel order
    path(
        "<int:pk>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),

    # Admin orders
    path(
        "admin/",
        AdminOrderListView.as_view(),
        name="admin-orders",
    ),

    # Admin update order
    path(
        "admin/<int:pk>/",
        AdminOrderUpdateView.as_view(),
        name="admin-order-update",
    ),
]