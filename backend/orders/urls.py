from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,
    AdminOrderListView,
    AdminOrderDetailView,
    AdminOrderUpdateView,
    
    SupplierOrderListView,
    SupplierOrderDetailView,
    SupplierOrderItemStatusUpdateView,
    SupplierDashboardView,
    SupplierSalesAnalyticsView,
    SupplierProductPerformanceView,
)


app_name = "orders"


urlpatterns = [

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

    # ======================================================
    # SUPPLIER
    # ======================================================

    path(
        "supplier/",
        SupplierOrderListView.as_view(),
        name="supplier-order-list",
    ),

    path(
        "supplier/<int:order_id>/",
        SupplierOrderDetailView.as_view(),
        name="supplier-order-detail",
    ),
    
    path(
    "supplier/items/<int:item_id>/update/",
    SupplierOrderItemStatusUpdateView.as_view(),
    name="supplier-order-item-update",
    ),
    
    path(
    "supplier/dashboard/",
    SupplierDashboardView.as_view(),
    name="supplier-dashboard",
    ),
    
    path(
    "supplier/analytics/",
    SupplierSalesAnalyticsView.as_view(),
    name="supplier-sales-analytics",
    ),
    
    path(
    "supplier/products/performance/",
    SupplierProductPerformanceView.as_view(),
    name="supplier-product-performance",
    ),
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

]