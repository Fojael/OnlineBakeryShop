from django.urls import path

from .views import (
    SupplierListCreateView,
    SupplierRetrieveUpdateDestroyView,
    SupplierActivateView,
    SupplierDeactivateView,
    SupplierProfileView,
    ReplenishmentRequestListCreateView,
    ReplenishmentRequestDetailView,
    ReplenishmentStatusUpdateView,
)

from .dashboard_views import (
    SupplierDashboardView,
)

from .product_views import (
    SupplierProductListCreateView,
    SupplierProductRetrieveUpdateDestroyView,
)


urlpatterns = [

    # ==========================================================
    # SUPPLIER PROFILE
    # ==========================================================

    path(
        "profile/",
        SupplierProfileView.as_view(),
        name="supplier-profile",
    ),


    # ==========================================================
    # SUPPLIER DASHBOARD
    # ==========================================================

    path(
        "dashboard/",
        SupplierDashboardView.as_view(),
        name="supplier-dashboard",
    ),


    # ==========================================================
    # SUPPLIER PRODUCTS
    # ==========================================================

    path(
        "products/",
        SupplierProductListCreateView.as_view(),
        name="supplier-products",
    ),

    path(
        "products/<int:pk>/",
        SupplierProductRetrieveUpdateDestroyView.as_view(),
        name="supplier-product-detail",
    ),


    # ==========================================================
    # STOCK REPLENISHMENT
    # ==========================================================

    path(
        "replenishments/",
        ReplenishmentRequestListCreateView.as_view(),
        name="replenishment-list-create",
    ),

    path(
        "replenishments/<int:request_id>/",
        ReplenishmentRequestDetailView.as_view(),
        name="replenishment-detail",
    ),

    path(
        "replenishments/<int:request_id>/status/",
        ReplenishmentStatusUpdateView.as_view(),
        name="replenishment-status-update",
    ),


    # ==========================================================
    # ADMIN SUPPLIER CRUD
    # ==========================================================

    path(
        "",
        SupplierListCreateView.as_view(),
        name="supplier-list",
    ),

    path(
        "<int:pk>/activate/",
        SupplierActivateView.as_view(),
        name="supplier-activate",
    ),

    path(
        "<int:pk>/deactivate/",
        SupplierDeactivateView.as_view(),
        name="supplier-deactivate",
    ),

    path(
        "<int:pk>/",
        SupplierRetrieveUpdateDestroyView.as_view(),
        name="supplier-detail",
    ),

]

