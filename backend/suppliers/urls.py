from django.urls import path

from .views import (
    SupplierRegisterView,
    SupplierListCreateView,
    SupplierRetrieveUpdateDestroyView,
    SupplierActivateView,
    SupplierDeactivateView,
    SupplierProfileView,
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
    # SUPPLIER REGISTRATION
    # ==========================================================

    path(
        "register/",
        SupplierRegisterView.as_view(),
        name="supplier-register",
    ),


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