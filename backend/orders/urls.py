from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderCancelView,
    AdminOrderListView,
    AdminOrderUpdateView,
)


urlpatterns = [

    # =====================================================
    # CUSTOMER ORDERS
    # =====================================================

    # GET  -> Customer's orders
    # POST -> Create new order
    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),

    # GET -> Customer views one order
    path(
        "<int:pk>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    # PATCH -> Cancel pending order
    path(
        "<int:pk>/cancel/",
        OrderCancelView.as_view(),
        name="order-cancel",
    ),

    # =====================================================
    # ADMIN ORDERS
    # =====================================================

    # GET -> Admin sees ALL orders
    path(
        "admin/",
        AdminOrderListView.as_view(),
        name="admin-order-list",
    ),

    # GET/PUT/PATCH -> Admin updates order
    path(
        "admin/<int:pk>/",
        AdminOrderUpdateView.as_view(),
        name="admin-order-update",
    ),
]