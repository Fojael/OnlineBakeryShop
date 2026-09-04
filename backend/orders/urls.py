from django.urls import path

from .views import (
    # ======================================================
    # ADMIN ORDER VIEWS
    # ======================================================
    AdminOrderListView,
    AdminOrderDetailView,
    AdminOrderUpdateView,
    AdminAcceptOrderView,

    # ======================================================
    # ADMIN DELIVERY RIDER MANAGEMENT
    # ======================================================
    AdminDeliveryRiderListView,
    AdminCreateDeliveryRiderView,
    AdminUpdateDeliveryRiderView,
    AdminToggleDeliveryRiderStatusView,

    # ======================================================
    # ADMIN DELIVERY ASSIGNMENT
    # ======================================================
    AdminAssignDeliveryView,

    # ======================================================
    # SUPPLIER VIEWS
    # ======================================================
    SupplierOrderListView,
    SupplierOrderDetailView,
    SupplierOrderItemStatusUpdateView,
    SupplierDashboardView,
    SupplierSalesAnalyticsView,
    SupplierProductPerformanceView,

    # ======================================================
    # CUSTOMER ORDER VIEWS
    # ======================================================
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,

    # ======================================================
    # REFUND VIEWS
    # ======================================================
    CustomerRefundRequestView,
    AdminRefundListView,
    AdminRefundUpdateView,
)


app_name = "orders"


urlpatterns = [

    # ======================================================
    # ADMIN ORDER MANAGEMENT
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

    path(
        "admin/<int:order_id>/accept/",
        AdminAcceptOrderView.as_view(),
        name="admin-accept-order",
    ),


    # ======================================================
    # ADMIN DELIVERY RIDER MANAGEMENT
    # ======================================================

    path(
        "admin/delivery-riders/",
        AdminDeliveryRiderListView.as_view(),
        name="admin-delivery-rider-list",
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


    # ======================================================
    # ADMIN ASSIGN DELIVERY
    # ======================================================
    #
    # Workflow:
    #
    # Customer Order
    #       ↓
    # Pending
    #       ↓ Admin Accept
    # Accepted
    #       ↓ Supplier Processing
    # Processing
    #       ↓ All Supplier Items Ready
    # Ready
    #       ↓ Admin selects a specific rider
    # Assigned
    #
    # The rider does NOT claim an available delivery.
    # Admin explicitly assigns the rider.
    # ======================================================

    path(
        "admin/<int:order_id>/assign-delivery/",
        AdminAssignDeliveryView.as_view(),
        name="admin-assign-delivery",
    ),


    # ======================================================
    # SUPPLIER ORDER MANAGEMENT
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
        name="supplier-order-item-status-update",
    ),


    # ======================================================
    # SUPPLIER DASHBOARD
    # ======================================================

    path(
        "supplier/dashboard/",
        SupplierDashboardView.as_view(),
        name="supplier-dashboard",
    ),

    path(
        "supplier/analytics/",
        SupplierSalesAnalyticsView.as_view(),
        name="supplier-analytics",
    ),

    path(
        "supplier/products/performance/",
        SupplierProductPerformanceView.as_view(),
        name="supplier-product-performance",
    ),


    # ======================================================
    # CUSTOMER ORDER MANAGEMENT
    # ======================================================

    # GET  -> Customer's orders
    # POST -> Create a new order
    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),

    # GET -> Customer's specific order
    path(
        "<int:order_id>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    # POST/PATCH -> Cancel customer's order
    path(
        "<int:order_id>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),


    # ======================================================
    # CUSTOMER REFUND
    # ======================================================

    path(
        "refunds/request/",
        CustomerRefundRequestView.as_view(),
        name="customer-refund-request",
    ),


    # ======================================================
    # ADMIN REFUND MANAGEMENT
    # ======================================================

    path(
        "refunds/admin/",
        AdminRefundListView.as_view(),
        name="admin-refund-list",
    ),

    path(
        "refunds/admin/<int:refund_id>/update/",
        AdminRefundUpdateView.as_view(),
        name="admin-refund-update",
    ),
]

