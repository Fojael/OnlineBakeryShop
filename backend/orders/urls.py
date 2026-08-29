from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,
    AdminOrderListView,
    AdminOrderDetailView,
    AdminOrderUpdateView,
)


app_name = "orders"


urlpatterns = [

    # ======================================================
    # CUSTOMER
    # ======================================================

    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),

    path(
        "<int:order_id>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    path(
        "<int:order_id>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),

    # ======================================================
    # ADMIN
    # ======================================================

    path(
        "admin/",
        AdminOrderListView.as_view(),
        name="admin-order-list",
    ),

    path(
        "admin/<int:order_id>/",
        AdminOrderDetailView.as_view(),
        name="admin-order-detail",
    ),

    path(
        "admin/<int:order_id>/update/",
        AdminOrderUpdateView.as_view(),
        name="admin-order-update",
    ),
]