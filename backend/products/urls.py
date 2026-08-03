from django.urls import path

from .views import (
    ProductListCreateView,
    ProductRetrieveUpdateDeleteView,
)

urlpatterns = [
    path(
        "",
        ProductListCreateView.as_view(),
        name="product-list",
    ),

    path(
        "<int:pk>/",
        ProductRetrieveUpdateDeleteView.as_view(),
        name="product-detail",
    ),
]