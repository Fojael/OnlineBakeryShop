from django.urls import path

from .views import (
    # ADMIN
    AdminOrderListView,
    AdminOrderDetailView,
    AdminOrderUpdateView,
    AdminDeliveryRiderListView,
    AdminCreateDeliveryRiderView,
    AdminUpdateDeliveryRiderView,
    AdminToggleDeliveryRiderStatusView,
    AdminAssignDeliveryView,

    # SUPPLIER
    SupplierOrderListView,
    SupplierOrderDetailView,
    SupplierOrderItemStatusUpdateView,
    SupplierDashboardView,
    SupplierSalesAnalyticsView,
    SupplierProductPerformanceView,

    # CUSTOMER
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,
    CustomerRefundRequestView,
    AdminRefundListView,
    AdminRefundUpdateView,

    # DELIVERY
    DeliveryDashboardView,
    DeliveryListView,
    DeliveryDetailView,
    DeliveryStatusUpdateView,
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
    # ADMIN - DELIVERY RIDERS
    # ======================================================

    path(
        "admin/delivery-riders/",
        AdminDeliveryRiderListView.as_view(),
        name="admin-delivery-riders-list",
    ),

    path(
        "admin/delivery-riders/create/",
        AdminCreateDeliveryRiderView.as_view(),
        name="admin-create-delivery-rider",
    ),

    path(
        "admin/delivery-riders/<int:rider_id>/update/",
        AdminUpdateDeliveryRiderView.as_view(),
        name="admin-update-delivery-rider",
    ),

    path(
        "admin/delivery-riders/<int:rider_id>/toggle-status/",
        AdminToggleDeliveryRiderStatusView.as_view(),
        name="admin-toggle-delivery-rider-status",
    ),

    path(
        "admin/<int:order_id>/assign-delivery/",
        AdminAssignDeliveryView.as_view(),
        name="admin-assign-delivery",
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
    # DELIVERY RIDER
    # ======================================================

    path(
        "delivery/dashboard/",
        DeliveryDashboardView.as_view(),
        name="delivery-dashboard",
    ),

    path(
        "delivery/",
        DeliveryListView.as_view(),
        name="delivery-list",
    ),

    path(
        "delivery/<int:delivery_id>/",
        DeliveryDetailView.as_view(),
        name="delivery-detail",
    ),

    path(
        "delivery/<int:delivery_id>/status/",
        DeliveryStatusUpdateView.as_view(),
        name="delivery-status-update",
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
        "refunds/request/",
        CustomerRefundRequestView.as_view(),
        name="customer-refund-request",
    ),

    path(
        "refunds/admin/",
        AdminRefundListView.as_view(),
        name="admin-refunds-list",
    ),

    path(
        "refunds/admin/<int:refund_id>/update/",
        AdminRefundUpdateView.as_view(),
        name="admin-update-refund",
    ),

    path(
        "<int:order_id>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),
]