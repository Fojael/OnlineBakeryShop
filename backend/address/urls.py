from django.urls import path

from .views import (
    AddressListCreateView,
    AddressDetailView,
)

urlpatterns = [
    path(
        "",
        AddressListCreateView.as_view(),
        name="address-list",
    ),

    path(
        "<int:pk>/",
        AddressDetailView.as_view(),
        name="address-detail",
    ),
]

