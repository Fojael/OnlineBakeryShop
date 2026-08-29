from django.urls import path

from .views import (
    ProductListCreateView,
    ProductRetrieveUpdateDeleteView,
)


urlpatterns = [

    # ======================================================
    # PRODUCT LIST / CREATE
    # ======================================================

    path(
        "",
        ProductListCreateView.as_view(),
        name="product-list",
    ),

    # ======================================================
    # PRODUCT DETAIL / UPDATE / DELETE
    # ======================================================

    path(
        "<int:pk>/",
        ProductRetrieveUpdateDeleteView.as_view(),
        name="product-detail",
    ),
]