from django.urls import path

from .views import (
    InventoryListView,
    InventoryUpdateView,
)

urlpatterns = [

    path(
        "",
        InventoryListView.as_view(),
        name="inventory-list",
    ),

    path(
        "<int:pk>/",
        InventoryUpdateView.as_view(),
        name="inventory-update",
    ),

]