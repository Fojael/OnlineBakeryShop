from django.urls import path

from .views import (
    SupplierRegisterView,
    SupplierListCreateView,
    SupplierRetrieveUpdateDestroyView,
    SupplierActivateView,
    SupplierDeactivateView,
)

from .dashboard_views import (
    SupplierDashboardView,
)

urlpatterns = [

    # ==========================================================
    # Supplier Registration
    # ==========================================================

    path(
        "register/",
        SupplierRegisterView.as_view(),
        name="supplier-register",
    ),

    # ==========================================================
    # Admin Supplier CRUD
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

    # ==========================================================
    # Supplier Dashboard
    # ==========================================================

    path(
        "dashboard/",
        SupplierDashboardView.as_view(),
        name="supplier-dashboard",
    ),
]