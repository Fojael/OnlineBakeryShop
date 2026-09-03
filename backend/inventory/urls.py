from django.urls import path

from .views import (
    InventoryListView,
    InventoryUpdateView,
)

from .dashboard_views import (
    InventoryDashboardView,
)

urlpatterns = [

    path(
        "",
        InventoryListView.as_view(),
        name="inventory-list",
    ),

    path(
        "dashboard/",
        InventoryDashboardView.as_view(),
        name="inventory-dashboard",
    ),

    path(
        "<int:pk>/",
        InventoryUpdateView.as_view(),
        name="inventory-update",
    ),

]

