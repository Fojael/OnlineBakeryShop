from django.urls import path

from .views import (
    # ==========================================================
    # ADMIN ORDER MANAGEMENT
    # ==========================================================
    AdminOrderListView,
    AdminOrderDetailView,
    AdminOrderUpdateView,
    AdminAcceptOrderView,

    # ==========================================================
    # ADMIN DELIVERY RIDER ACCOUNT MANAGEMENT
    # ==========================================================
    AdminDeliveryRiderListView,
    AdminCreateDeliveryRiderView,
    AdminUpdateDeliveryRiderView,
    AdminToggleDeliveryRiderStatusView,
    AdminDeliveryRiderDeliveriesView,

    # ==========================================================
    # SUPPLIER ORDER MANAGEMENT
    # ==========================================================
    SupplierOrderListView,
    SupplierOrderDetailView,
    SupplierOrderItemStatusUpdateView,
    SupplierDashboardView,
    SupplierSalesAnalyticsView,
    SupplierProductPerformanceView,

    # ==========================================================
    # CUSTOMER ORDER MANAGEMENT
    # ==========================================================
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,

    # ==========================================================
    # CUSTOMER REFUND
    # ==========================================================
    CustomerRefundRequestView,

    # ==========================================================
    # ADMIN REFUND
    # ==========================================================
    AdminRefundListView,
    AdminRefundUpdateView,
)


app_name = "orders"


urlpatterns = [

    # ==========================================================
    # ADMIN — ORDER MANAGEMENT
    # ==========================================================

    # GET
    # All customer orders
    path(
        "admin/",
        AdminOrderListView.as_view(),
        name="admin-order-list",
    ),

    # GET
    # Single order details
    path(
        "admin/<int:order_id>/",
        AdminOrderDetailView.as_view(),
        name="admin-order-detail",
    ),

    # PATCH / PUT
    # Admin can update allowed order statuses
    path(
        "admin/<int:order_id>/update/",
        AdminOrderUpdateView.as_view(),
        name="admin-order-update",
    ),

    # POST
    # Pending → Accepted
    path(
        "admin/<int:order_id>/accept/",
        AdminAcceptOrderView.as_view(),
        name="admin-accept-order",
    ),


    # ==========================================================
    # ADMIN — DELIVERY RIDER ACCOUNT MANAGEMENT
    # ==========================================================

    # GET
    # List delivery riders
    path(
        "admin/delivery-riders/",
        AdminDeliveryRiderListView.as_view(),
        name="admin-delivery-rider-list",
    ),
    path(
        "admin/delivery-riders/",
        AdminDeliveryRiderListView.as_view(),
        name="admin-delivery-riders-list",
    ),

    # POST
    # Create a new delivery rider
    path(
        "admin/delivery-riders/create/",
        AdminCreateDeliveryRiderView.as_view(),
        name="admin-create-delivery-rider",
    ),

    # PATCH / PUT
    # Update rider information
    path(
        "admin/delivery-riders/<int:rider_id>/update/",
        AdminUpdateDeliveryRiderView.as_view(),
        name="admin-update-delivery-rider",
    ),

    # POST
    # Activate / deactivate rider
    path(
        "admin/delivery-riders/<int:rider_id>/toggle-status/",
        AdminToggleDeliveryRiderStatusView.as_view(),
        name="admin-toggle-delivery-rider-status",
    ),

    path(
        "admin/delivery-riders/<int:rider_id>/deliveries/",
        AdminDeliveryRiderDeliveriesView.as_view(),
        name="admin-delivery-rider-deliveries",
    ),


    # ==========================================================
    # SUPPLIER — ORDER MANAGEMENT
    # ==========================================================

    # GET
    # Supplier's orders
    path(
        "supplier/",
        SupplierOrderListView.as_view(),
        name="supplier-order-list",
    ),

    # GET
    # Supplier order details
    path(
        "supplier/<int:order_id>/",
        SupplierOrderDetailView.as_view(),
        name="supplier-order-detail",
    ),

    # PATCH / PUT
    # Supplier updates their OrderItem:
    # Pending → Processing → Ready
    path(
        "supplier/items/<int:item_id>/update/",
        SupplierOrderItemStatusUpdateView.as_view(),
        name="supplier-order-item-status-update",
    ),

    # GET
    # Supplier dashboard
    path(
        "supplier/dashboard/",
        SupplierDashboardView.as_view(),
        name="supplier-dashboard",
    ),

    # GET
    # Supplier sales analytics
    path(
        "supplier/analytics/",
        SupplierSalesAnalyticsView.as_view(),
        name="supplier-analytics",
    ),

    # GET
    # Supplier product performance
    path(
        "supplier/products/performance/",
        SupplierProductPerformanceView.as_view(),
        name="supplier-product-performance",
    ),


    # ==========================================================
    # CUSTOMER — ORDERS
    # ==========================================================

    # GET
    # Customer's orders
    #
    # POST
    # Create a new order
    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),

    # GET
    # Single customer order
    path(
        "<int:order_id>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    # POST
    # Cancel an eligible order
    path(
        "<int:order_id>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),


    # ==========================================================
    # CUSTOMER — REFUND REQUEST
    # ==========================================================

    # POST
    # Customer can request refund only after Delivered
    path(
        "refunds/request/",
        CustomerRefundRequestView.as_view(),
        name="customer-refund-request",
    ),


    # ==========================================================
    # ADMIN — REFUND MANAGEMENT
    # ==========================================================

    # GET
    # List refund requests
    path(
        "refunds/admin/",
        AdminRefundListView.as_view(),
        name="admin-refund-list",
    ),

    # PATCH / PUT
    # Approve / reject / complete refund
    path(
        "refunds/admin/<int:refund_id>/update/",
        AdminRefundUpdateView.as_view(),
        name="admin-refund-update",
    ),
]

