from django.urls import path

from .views import (
    OrderListCreateView,
    OrderRetrieveView,
    AdminOrderListView,
    AdminOrderUpdateView,
)

urlpatterns = [
    # Customer
    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),
    path(
        "<int:pk>/",
        OrderRetrieveView.as_view(),
        name="order-detail",
    ),

    # Admin
    path(
        "admin/",
        AdminOrderListView.as_view(),
        name="admin-order-list",
    ),
    path(
        "admin/<int:pk>/",
        AdminOrderUpdateView.as_view(),
        name="admin-order-update",
    ),
]