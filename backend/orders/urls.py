from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,
    AdminOrderListView,
    AdminOrderUpdateView,
)

app_name = "orders"

urlpatterns = [
    # ==========================================================
    # CUSTOMER
    # ==========================================================

    # GET    /api/orders/
    # POST   /api/orders/
    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),

    # GET /api/orders/<order_id>/
    path(
        "<int:order_id>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    # POST /api/orders/<order_id>/cancel/
    path(
        "<int:order_id>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),

    # ==========================================================
    # ADMIN
    # ==========================================================

    # GET /api/orders/admin/
    path(
        "admin/",
        AdminOrderListView.as_view(),
        name="admin-order-list",
    ),

    # PATCH /api/orders/admin/<order_id>/
    path(
        "admin/<int:order_id>/",
        AdminOrderUpdateView.as_view(),
        name="admin-order-update",
    ),
]