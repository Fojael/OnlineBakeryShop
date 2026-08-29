from django.urls import path

from .views import (
    SupplierListCreateView,
    SupplierRetrieveUpdateDestroyView,
)

from .dashboard_views import (
    SupplierDashboardView,
)

urlpatterns = [
    path(
        "",
        SupplierListCreateView.as_view(),
    ),

    path(
        "<int:pk>/",
        SupplierRetrieveUpdateDestroyView.as_view(),
    ),

    path(
        "dashboard/",
        SupplierDashboardView.as_view(),
        name="supplier-dashboard",
    ),
]