from django.urls import path

from .views import (
    InventoryListView,
    InventoryUpdateView,
    InventoryTransactionListCreateView,
    ProductionBatchListCreateView,
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
        "transactions/",
        InventoryTransactionListCreateView.as_view(),
        name="inventory-transactions",
    ),

    path(
        "batches/",
        ProductionBatchListCreateView.as_view(),
        name="production-batches",
    ),

    path(
        "<int:pk>/",
        InventoryUpdateView.as_view(),
        name="inventory-update",
    ),

]

